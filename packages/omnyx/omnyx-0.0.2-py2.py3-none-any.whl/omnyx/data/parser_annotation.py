import json
from collections import defaultdict
from pathlib import Path
from typing import Dict, List

import numpy as np

from ..fileio import check_filepath, lsdir, mkdir, read_json, read_text
from ..math.geometry import (quaternion_to_rotvec, rotvec_to_quaternion,
                             rotvec_to_rotmat, transform_matrix)
from ..sensor.camera import calculate_camera_fov
from ..system.logging import logger
from ..system.threading import multi_process_thread
from .dataclass import (ClipInfo, FrameInfo, MotionState, ObjectInfo,
                        ObjSubType, SensorCalib)
from .type_annotation import (ANNOTATION_ID, ANNOTATION_INFO, ANNOTATION_TYPE,
                              AnnotationType, parse_3d_lane_anno_info)
from .type_obstacle import (MOVABLE_BICYCLE, SUBTYPE_TO_TYPE, ObjSubType,
                            SensetimeType)
from .type_sensor import (MAIN_LIDAR_COMPENSATED, MAIN_SENSOR_LIDAR,
                          SENSOR_TYPE_CAMERA, SensetimeSensorName, SensorName)

__all__ = ['get_annotation_type', 'get_annotation_info', 'recast_annotation',
           'get_sensetime_info', 'get_maxieye_info']


def get_annotation_type(
    clip_path: Path,
    anno_dir: str = 'annotation',
    anno_type: str = 'PVB'
) -> AnnotationType:
    avaliable_anno_type = [anno_subtype for anno_subtype in ANNOTATION_TYPE[anno_type]
        if (clip_path / anno_dir / anno_subtype.value / f'{clip_path.stem}.json').exists()]

    if len(avaliable_anno_type) == 0:
        logger.error(f'no {anno_type} annotation found for {clip_path.stem}')
        return

    elif len(avaliable_anno_type) > 1:
        logger.warning(f'multiple annotation types found for {clip_path.stem}: {avaliable_anno_type}, '
                       f'use {avaliable_anno_type[0]} by default')

    logger.debug(f'found annotation {avaliable_anno_type[0]} {ANNOTATION_ID.get(avaliable_anno_type[0])}')
    return avaliable_anno_type[0]


def get_annotation_info(
    clip_path: str,
    anno_dir: str = 'annotation',
    anno_type: str = 'PVB',
    anno_path: str = None,
    anno_subtype: AnnotationType = None,
    merge_gop: str = None,
) -> ClipInfo:
    """
    @param clip_path: clip root or annotation path
    @param anno_dir: sub directory to annotation
    @param anno_type: annotation type PVB, GOP, etc
    @param [optional] anno_path: annotation path
    @param [optional] anno_subtype: annotation prefix
    return: annotations
    """
    _clip_path: Path = check_filepath(clip_path)

    _anno_subtype = anno_subtype or get_annotation_type(_clip_path, anno_dir, anno_type)
    if _anno_subtype is None:
        return

    _anno_path = anno_path or _clip_path / anno_dir / _anno_subtype.value / f'{_clip_path.stem}.json'

    anno_info = read_json(_anno_path, strict=False)
    if anno_info is None:
        return

    annotation_info = ClipInfo(
        clip_name=_clip_path.stem,
        clip_path=clip_path,
        anno_type=_anno_subtype,
        calibrations={
            SensorName[sensor_name]: SensorCalib(
                extrinsic_matrix=np.asarray(sensor_calib['extrinsic']),
                intrinsic_matrix=np.asarray(sensor_calib['intrinsic']),
                intrinsic_matrix_scaled=np.asarray(sensor_calib['intrinsic_scaled'])
                    if 'intrinsic_scaled' in sensor_calib else None,
                distortion=np.asarray(sensor_calib['distcoeff']).flatten(),
                width=sensor_calib['width'],
                height=sensor_calib['height'],
                distortion_model=sensor_calib['distortion_model'],
                fov=calculate_camera_fov(dict(
                    distortion_model=sensor_calib['distortion_model'],
                    intrinsic_matrix=np.asarray(sensor_calib['intrinsic']),
                    distortion=np.asarray(sensor_calib['distcoeff']).flatten(),
                    width=sensor_calib['width'],
                    height=sensor_calib['height'])),
            ) if SensorName[sensor_name] in SENSOR_TYPE_CAMERA else SensorCalib(
                extrinsic_matrix=np.asarray(sensor_calib['extrinsic']),
            )
            for sensor_name, sensor_calib in anno_info['calibration'].items()
        }, frames={})

    def _fill_pvb_gop_anno_obj(sensor_name: str, anno_info: Dict[str, List[Dict]], track_ids: List, track_offset: int = 0) -> List[ObjectInfo]:
        return [
            ObjectInfo(
                lidar_box3d=anno['obj_center_pos'] + anno['size'] + [quaternion_to_rotvec(anno['obj_rotation'])[2]],
                lidar_velo=anno.get('velocity'),
                # lidar_confidence=anno.get('confidence'),
                lidar_pts_count=anno.get('num_lidar_pts'),
                camera_box3d=anno['obj_center_pos_cam'] + anno['size'] + [quaternion_to_rotvec(anno['obj_rotation_cam'])[2]]
                    if anno.get('obj_center_pos_cam') is not None and anno.get('obj_rotation_cam') is not None else None,
                obj_subtype=ObjSubType[anno['category']],
                obj_type=SUBTYPE_TO_TYPE[ObjSubType[anno['category']]],
                track_id=anno['track_id'] + track_offset,
                motion_state=None if anno.get('motion_state') is None else MotionState[anno['motion_state']],
                group_id=anno.get('group_id'),
                is_group=anno.get('is_group'),
                is_cyclist=anno.get('is_cyclist'),
                is_fake=anno.get('is_fake', False),
                cross_lane=anno.get('cross_lane'),
                lane_id=anno.get('lane_id'),
                signal=anno.get('signal'),
            ) if sensor_name == MAIN_SENSOR_LIDAR.value else
            ObjectInfo(
                camera_box2d=[
                    anno['bbox'][0] - anno['bbox'][2] // 2,
                    anno['bbox'][1] - anno['bbox'][3] // 2,
                    anno['bbox'][0] + anno['bbox'][2] - anno['bbox'][2] // 2,
                    anno['bbox'][1] + anno['bbox'][3] - anno['bbox'][3] // 2,
                ],
                undistorted_box2d=[
                    anno['undistort'][0] - anno['undistort'][2] // 2,
                    anno['undistort'][1] - anno['undistort'][3] // 2,
                    anno['undistort'][0] + anno['undistort'][2] - anno['undistort'][2] // 2,
                    anno['undistort'][1] + anno['undistort'][3] - anno['undistort'][3] // 2,
                ] if 'undistort' in anno else None,
                camera_box3d=anno_info[MAIN_SENSOR_LIDAR.value][track_ids.index(anno['track_id'])]['obj_center_pos_cam'] + \
                            anno_info[MAIN_SENSOR_LIDAR.value][track_ids.index(anno['track_id'])]['size'] + \
                            [quaternion_to_rotvec(anno_info[MAIN_SENSOR_LIDAR.value][track_ids.index(anno['track_id'])]['obj_rotation_cam'])[2]]
                    if anno_info[MAIN_SENSOR_LIDAR.value][track_ids.index(anno['track_id'])].get('obj_center_pos_cam') is not None and \
                       anno_info[MAIN_SENSOR_LIDAR.value][track_ids.index(anno['track_id'])].get('obj_rotation_cam') is not None else None,
                # camera_confidence=anno.get('confidence'),
                obj_subtype=ObjSubType[anno_info[MAIN_SENSOR_LIDAR.value][track_ids.index(anno['track_id'])]['category']],
                obj_type=SUBTYPE_TO_TYPE[ObjSubType[anno_info[MAIN_SENSOR_LIDAR.value][track_ids.index(anno['track_id'])]['category']]],
                track_id=anno['track_id'] + track_offset,
                occlusion=anno.get('occlusion'),
                truncation=anno.get('truncation'),
            ) for anno in anno_info[sensor_name]]

    def _fill_pvb_gop_anno_frame(annotation_info: Dict) -> FrameInfo:

        anno_info = ANNOTATION_INFO[_anno_subtype.name](annotation_info)
        recast_annotation(anno_info[MAIN_SENSOR_LIDAR.value], annotation_info['frame_name'])
        track_ids = [_obj['track_id'] for _obj in anno_info[MAIN_SENSOR_LIDAR.value]]

        return FrameInfo(
            frame_name=annotation_info['frame_name'],
            camera_timestamp=annotation_info['camera_collect'],
            lidar_timestamp=annotation_info['lidar_collect'],
            lidar2slam=np.asarray(annotation_info['lidar_pose']) if 'lidar_pose' in annotation_info else None,
            lidar_velo=np.asarray(annotation_info['lidar_velo']) if 'lidar_velo' in annotation_info else None,
            sensor_timestamps={
                SensorName[key]: int(annotation_info[key].split('_')[1])
                for key in annotation_info if SensorName[key] is not None},
            sensor_filepaths={
                SensorName[key]: _clip_path / f'{annotation_info["frame_name"]}/{annotation_info[key]}'
                for key in annotation_info if SensorName[key] is not None},
            objects={
                SensorName[sensor_name]: _fill_pvb_gop_anno_obj(sensor_name, anno_info, track_ids)
                for sensor_name in anno_info},
        )

    if _anno_subtype in ANNOTATION_TYPE['LANE3D']:
        annotation_info.frames = [dict(
            type=lines['type'], line_key_points=np.asarray([l for l in 
                lines['line_key_points'] if isinstance(l, list)])
        ) for lines in parse_3d_lane_anno_info(anno_info)]

    else:
        frames_info: List[FrameInfo] = multi_process_thread(
            _fill_pvb_gop_anno_frame, anno_info['frames'], nprocess=4,
            pool_func='ThreadPoolExecutor', map_func='map', progress_bar=False)

        annotation_info.frames = {info['lidar_timestamp']: info for info in
            sorted(frames_info, key=lambda frame: frame['lidar_timestamp'])}

    for frame_info in annotation_info.frames.values():
        frame_info.sensor_filepaths[MAIN_LIDAR_COMPENSATED] = \
            mkdir(_clip_path / 'static_obj/lidar_slam/mc_pcds') / \
        f'{frame_info.frame_name}_{frame_info.sensor_filepaths[MAIN_SENSOR_LIDAR].name}'

    if merge_gop is not None and _anno_subtype in [AnnotationType.INTERPOLATED_PVB]:
        gop_info = read_json(merge_gop, strict=False)

        if gop_info is None:
            return

        max_track_id = max([obj_info.track_id for anno in frames_info
            for obj_info in anno.objects[MAIN_SENSOR_LIDAR]]) if \
        len([_ for anno in frames_info for _ in anno.objects[MAIN_SENSOR_LIDAR]]) > 0 else 0

        frame_indices = np.argsort([f['frame_name'] for f in gop_info['frames']])

        for indx in frame_indices:
            annotated_gop = ANNOTATION_INFO[AnnotationType.REPROJECTED_GOP.name](gop_info['frames'][indx])
            track_ids = [_obj['track_id'] for _obj in annotated_gop[MAIN_SENSOR_LIDAR.value]]

            [annotation_info.frames[gop_info['frames'][indx]['lidar_collect']].objects[SensorName[sensor_name]].extend(
                _fill_pvb_gop_anno_obj(sensor_name, annotated_gop, track_ids, max_track_id))
                for sensor_name in annotated_gop]

    return annotation_info


def get_sensetime_info(
    clip_path: str,
    anno_path: str,
    calibrations: Dict[SensorName, SensorCalib] = None,
) -> ClipInfo:
    _clip_path: Path = check_filepath(clip_path)

    def _fill_obj_anno_frame(_annotation_info_raw: str) -> FrameInfo:
        _annotation_info = json.loads(_annotation_info_raw)

        object_infos = defaultdict(list)
        object_infos[MAIN_SENSOR_LIDAR] = [ObjectInfo(
            lidar_box3d=_obj['bbox3d'][:6] + _obj['bbox3d'][8:],
            lidar_velo=_obj['velocity'],
            lidar_pts_count=_obj['num_lidar_pts'],
            obj_subtype=ObjSubType[SensetimeType[_obj['label']].name],
            obj_type=SUBTYPE_TO_TYPE[ObjSubType[SensetimeType[_obj['label']].name]],
            track_id=_obj['id'],
            motion_state=MotionState[_obj['motion_state']],
        ) for _obj in _annotation_info['Objects']]

        [object_infos[SensorName[SensetimeSensorName[camera_name]]].append(
            ObjectInfo(camera_box2d=camera_obj['bbox2d'],
                       camera_box3d=_obj['bbox3d'][:6] + _obj['bbox3d'][8:],
                       obj_subtype=ObjSubType[SensetimeType[_obj['label']].name],
                       obj_type=SUBTYPE_TO_TYPE[ObjSubType[SensetimeType[_obj['label']].name]],
                       track_id=_obj['id'],
        )) for _obj in _annotation_info['Objects']
        for camera_name, camera_obj in _obj['info2d'].items() if \
            ObjSubType[SensetimeType[_obj['label']].name] not in MOVABLE_BICYCLE or \
            (ObjSubType[SensetimeType[_obj['label']].name] in MOVABLE_BICYCLE and \
             _obj.get('is_cyclist') == True)]

        return FrameInfo(
            frame_name=_annotation_info['timestamp'] * 1e3,
            lidar_timestamp=_annotation_info['timestamp'] * 1e3,
            ego2slam=np.asarray(_annotation_info['ego2global_transformation_matrix']),
            ego_velo=_annotation_info['ego_velocity'],
            sensor_timestamps=dict(**{
                SensorName[SensetimeSensorName[camera_name]]: camera_info['timestamp'] * 1e3
                for camera_name, camera_info in _annotation_info['sensors']['cameras'].items()
            }, **{MAIN_SENSOR_LIDAR: _annotation_info['sensors']['lidar']['car_center']['timestamp']}),
            sensor_filepaths=dict(**{
                SensorName[SensetimeSensorName[camera_name]]:
                _clip_path / camera_info['data_path'].split(_clip_path.name)[-1]
                for camera_name, camera_info in _annotation_info['sensors']['cameras'].items()
            }, **{MAIN_SENSOR_LIDAR:
                _clip_path / _annotation_info['sensors']['lidar']['car_center']['data_path'].split(_clip_path.name)[-1]
            }),
            objects=object_infos,
        )

    anno_info_raw = read_text(anno_path)
    sensors_info = json.loads(anno_info_raw[0])['sensors']
    annotation_info = ClipInfo(
        clip_name=_clip_path.stem,
        calibrations={
            SensorName[SensetimeSensorName[camera_name]]: SensorCalib(
                extrinsic_matrix=np.asarray(camera_calib['extrinsic']),
                intrinsic_matrix=np.asarray(camera_calib['camera_intrinsic']),
                distortion=np.asarray(camera_calib['camera_dist']).flatten(),
                distortion_model='fisheye' if len(camera_calib['camera_dist']) > 0 else 'pinhole',
                fov=calibrations[SensorName[SensetimeSensorName[camera_name]]].fov,
                width=calibrations[SensorName[SensetimeSensorName[camera_name]]].width,
                height=calibrations[SensorName[SensetimeSensorName[camera_name]]].height,
            ) for camera_name, camera_calib in sensors_info['cameras'].items()
        }
    )
    annotation_info.calibrations[MAIN_SENSOR_LIDAR] = calibrations[MAIN_SENSOR_LIDAR]

    frames_info = multi_process_thread(
        _fill_obj_anno_frame, anno_info_raw, nprocess=4,
            pool_func='ThreadPoolExecutor', map_func='map', progress_bar=False)

    annotation_info.frames = {info['lidar_timestamp']: info for info in
        sorted(frames_info, key=lambda frame: frame['lidar_timestamp'])}

    return annotation_info


def get_maxieye_info(
    clip_path: str,
    **whatever: Dict,
):
    _clip_path: Path = check_filepath(clip_path)
    import xmltodict

    _sensor_camera = {
        'cam_hk_x3j_back': SensorName.camera_rear_center,
        'cam_hk_x8b_front': SensorName.camera_front_center,
        'cam_st_x3j_front_avm': SensorName.camera_omni_front,
        'cam_st_x3j_left_avm': SensorName.camera_omni_left,
        'cam_st_x3j_rear_avm': SensorName.camera_omni_rear,
        'cam_st_x3j_right_avm': SensorName.camera_omni_right,
        'cam_st_x8d_front_narrow': SensorName.camera_front_center_tele,
    }
    _camera_size = {
        'cam_hk_x3j_back': dict(width=1920, height=1536),
        'cam_hk_x8b_front': dict(width=3840, height=2160),
        'cam_st_x3j_front_avm': dict(width=1920, height=1536),
        'cam_st_x3j_left_avm': dict(width=1920, height=1536),
        'cam_st_x3j_rear_avm': dict(width=1920, height=1536),
        'cam_st_x3j_right_avm': dict(width=1920, height=1536),
        'cam_st_x8d_front_narrow': dict(width=3840, height=2160),
    }

    _obj_subtype = {
        'Pedestrian': ObjSubType.person,
        'Vehicle': ObjSubType.car,
        'Rider': ObjSubType.bicycle,
        'Three': ObjSubType.tricycle,
        'Special': ObjSubType.special_vehicle,
    }

    def _fill_obj_anno_frame(_annotation_info_raw: Path):
        object_infos = defaultdict(list)
        # object_infos[MAIN_SENSOR_LIDAR] = []
        for sensor_str, sensor_name in _sensor_camera.items():
            sensor_frame_info = xmltodict.parse('\n'.join(read_text(
                _annotation_info_raw.as_posix().replace('cam_hk_x8b_front', sensor_str))))

            object_infos[sensor_name] = [
                ObjectInfo(
                    # camera_box2d=camera_obj['bbox2d'],
                    camera_box3d=np.asarray([
                        _obj['objWx'], _obj['objWy'], _obj['objWz'],
                        _obj['objLength'], _obj['objWidth'], _obj['objHeight'],
                        _obj['objYaw'],
                    ], dtype=float),
                    obj_subtype=_obj_subtype[obj_type],
                    obj_type=SUBTYPE_TO_TYPE[_obj_subtype[obj_type]],
                    track_id=int(_obj['@tracking_id']),
                ) for obj_type, obj_info in sensor_frame_info['Lidar']['LabelInfo'].items()
                for _obj in (obj_info['Object'] if isinstance(obj_info['Object'], list) else [obj_info['Object']])
                if _obj['cleanType'] == '0'
            ]
            object_infos[MAIN_SENSOR_LIDAR].extend([
                ObjectInfo(
                    # camera_box2d=camera_obj['bbox2d'],
                    lidar_box3d=np.asarray([
                        _obj['objWx'], _obj['objWy'], _obj['objWz'],
                        _obj['objLength'], _obj['objWidth'], _obj['objHeight'],
                        _obj['objYaw'],
                    ], dtype=float),
                    obj_subtype=_obj_subtype[obj_type],
                    obj_type=SUBTYPE_TO_TYPE[_obj_subtype[obj_type]],
                    track_id=int(_obj['@tracking_id']),
                ) for obj_type, obj_info in sensor_frame_info['Lidar']['LabelInfo'].items()
                for _obj in (obj_info['Object'] if isinstance(obj_info['Object'], list) else [obj_info['Object']])
            ])

        # import pdb; pdb.set_trace()
        return FrameInfo(
            frame_name=int(_annotation_info_raw.stem.replace('.', '')) * 1e3,
            lidar_timestamp=int(_annotation_info_raw.stem.replace('.', '')) * 1e3,
            ego2slam=transform_matrix([
                sensor_frame_info['Lidar']['CaptureInfo']['EgoPoseParam']['wx'],
                sensor_frame_info['Lidar']['CaptureInfo']['EgoPoseParam']['wy'],
                sensor_frame_info['Lidar']['CaptureInfo']['EgoPoseParam']['wz'],
            ], [
                sensor_frame_info['Lidar']['CaptureInfo']['EgoPoseParam']['qx'],
                sensor_frame_info['Lidar']['CaptureInfo']['EgoPoseParam']['qy'],
                sensor_frame_info['Lidar']['CaptureInfo']['EgoPoseParam']['qz'],
                sensor_frame_info['Lidar']['CaptureInfo']['EgoPoseParam']['qw'],
            ]),
            # ego_velo=_annotation_info['ego_velocity'],
            sensor_timestamps=dict(**{
                sensor_name: int(_annotation_info_raw.stem.replace('.', '')) * 1e3
                for sensor_name in _sensor_camera.values()}),
            sensor_filepaths=dict(**{
                sensor_name: _clip_path / sensor_str / f'{_annotation_info_raw.stem}.jpg'
                for sensor_str, sensor_name in _sensor_camera.items()}),
            objects=object_infos,
        )

    main_camera_anno_list = lsdir(_clip_path / 'label_lidar_rs_rubyplus128_topmiddle_align/cam_hk_x8b_front')
    main_camera_first_frame_info = xmltodict.parse(
        '\n'.join(read_text(main_camera_anno_list[0].as_posix())))

    annotation_info = ClipInfo(
        clip_name=_clip_path.stem,
        calibrations={
            _sensor_camera[sensor_name]: SensorCalib(
                extrinsic_matrix=transform_matrix(
                    [float(sensor_param[f'translation_vector{i}']) for i in range(3)],
                    rotvec_to_rotmat(*[float(sensor_param[f'rotation_vector{j}']) for j in range(3)])),
                intrinsic_matrix=np.asarray([sensor_param[f'intrinsic_matrix{i}'] for i in range(9)], dtype=float).reshape(3, 3),
                intrinsic_matrix_scaled=np.asarray([sensor_param[f'intrinsic_matrix{i}'] for i in range(9)], dtype=float).reshape(3, 3),
                distortion=np.asarray([float(sensor_param[f'distortion_coeffs{i}']) for i in range(4 if 'avm' in sensor_name else 8)], dtype=float).flatten(),
                distortion_model='fisheye' if 'avm' in sensor_name else 'pinhole',
                fov=calculate_camera_fov(dict(
                    intrinsic_matrix=np.asarray([sensor_param[f'intrinsic_matrix{i}'] for i in range(9)], dtype=float).reshape(3, 3),
                    distortion=np.asarray([sensor_param[f'distortion_coeffs{i}'] for i in range(4 if 'avm' in sensor_name else 8)], dtype=float).flatten(),
                    distortion_model='fisheye' if 'avm' in sensor_name else 'pinhole',
                    **_camera_size[sensor_name],
                )),
                **_camera_size[sensor_name],
            ) for sensor_name, sensor_param in main_camera_first_frame_info['Lidar']['CaptureInfo']['Lidar2CamParam'].items()
        }
    )

    frames_info = multi_process_thread(
        _fill_obj_anno_frame, main_camera_anno_list, nprocess=1,
        pool_func='ThreadPoolExecutor', map_func='map', progress_bar=False)

    annotation_info.frames = {info['lidar_timestamp']: info for info in
        sorted(frames_info, key=lambda frame: frame['lidar_timestamp'])}

    return annotation_info

def recast_annotation(anno_info: List[Dict], frame_name: str) -> None:
    """ """
    for indx, _object in enumerate(anno_info):
        if _object['category'] == 'barrier':
            length_width_ratio = _object['size'][0] / _object['size'][1]
            if length_width_ratio > 0.91 and length_width_ratio < 1.1:
                logger.debug(f'{frame_name} obj {_object["track_id"]} '
                             f'recast barrier to anti_collision_barrel, l{_object["size"][0]:.1f}, '
                             f'w{_object["size"][1]:.1f}, l:w{length_width_ratio:.1f}')
                _object.update(category='anti_collision_barrel')

        if _object['category'] in ['traffic_warning', 'construction_sign',
                                   'barrier', 'no_parking_sign', 'barrier_gate',
                                   'wall_column', 'round_column', 'lock']:
            yaw = quaternion_to_rotvec(_object['obj_rotation'])[2]
            if _object['size'][0] < _object['size'][1]:
                yaw += np.pi / 2
                _object['size'][0], _object['size'][1] = _object['size'][1], _object['size'][0]

            _object.update(obj_rotation=[float(x) for x in rotvec_to_quaternion(yaw=yaw % np.pi)])

        if _object['category'] == 'truck':
            length = _object['size'][0]
            if length < 6.5:
                logger.debug(f'{frame_name} obj {_object["track_id"]} '
                             f'recast truck to pickup_truck, l{_object["size"][0]:.1f}')
                _object.update(category='pickup_truck')

        if _object['category'] == 'pickup_truck':
            length = _object['size'][0]
            if length > 6.5:
                logger.debug(f'{frame_name} obj {_object["track_id"]} '
                             f'recast pickup_truck to truck, l{_object["size"][0]:.1f}')
                _object.update(category='truck')

        if _object['category'] in ['unknown_unmovable', 'unknown_movable', 'gate']:
            logger.debug(f'{frame_name} obj {_object["track_id"]} '
                         f'recast {_object["category"]} to unknown')
            _object.update(category='unknown')

        if _object['category'] == 'animal':
            logger.debug(f'{frame_name} obj {_object["track_id"]} '
                            f'recast animal to small_animal')
            _object.update(category='small_animal')

        if _object['category'] not in ['bicycle', 'tricycle', 'motorcycle']:
            if _object.get('is_cyclist') is not None:
                logger.debug(f'{frame_name} obj {_object["track_id"]} '
                             f'{_object["category"]} recast is_cyclist to none')
                _object.update(is_cyclist=None)

        if _object['category'] == 'fake_car':
            logger.debug(f'{frame_name} obj {_object["track_id"]} '
                         f'{_object["category"]} recast fake_car to car')
            _object.update(category='car', is_fake=True)

        if _object['category'] == 'fake_person':
            logger.debug(f'{frame_name} obj {_object["track_id"]} '
                         f'{_object["category"]} recast fake_person to person')
            _object.update(category='person', is_fake=True)

        if _object['category'] == 'fake_bicycle':
            logger.debug(f'{frame_name} obj {_object["track_id"]} '
                         f'{_object["category"]} recast fake_bicycle to bicycle')
            _object.update(category='bicycle', is_fake=True)
