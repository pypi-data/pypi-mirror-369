from typing import Dict

import numpy as np

from .dataclass import FrameInfo, ObjectInfo
from .type_obstacle import (SUBTYPE_TO_TYPE, CameraObjType, LidarObjType,
                            MotionState, ObjSubType)
from .type_sensor import SENSOR_TYPE_CAMERA, SENSOR_TYPE_LIDAR, SensorName

__all__ = ['encode_psr_frame', 'decode_psr_frame']


def encode_psr_frame(frame: FrameInfo) -> Dict:
    """
    @param frame: detection frame
    return: frame dictionary
    """
    return dict(
        frame_id=frame.lidar_timestamp,
        objects={sensor_name.value: [dict(
            psr=None if obj.lidar_box3d is None else dict(
                position=dict(
                    x=round(obj.lidar_box3d[0], 4),
                    y=round(obj.lidar_box3d[1], 4),
                    z=round(obj.lidar_box3d[2], 4)),
                scale=dict(
                    x=round(obj.lidar_box3d[3], 4),
                    y=round(obj.lidar_box3d[4], 4),
                    z=round(obj.lidar_box3d[5], 4)),
                rotation=dict(
                    x=0,
                    y=0,
                    z=round(obj.lidar_box3d[6], 4)),
            ),
            camera_box3d=None if obj.camera_box3d is None else obj.camera_box3d.tolist(),
            bbox=None if obj.camera_box2d is None else dict(
                x1=round(float(obj.camera_box2d[0]), 2),
                y1=round(float(obj.camera_box2d[1]), 2),
                x2=round(float(obj.camera_box2d[2]), 2),
                y2=round(float(obj.camera_box2d[3]), 2),
            ),
            timestamp=obj.timestamp,
            obj_score=None if obj.lidar_confidence is None else round(float(obj.lidar_confidence), 4),
            cam_obj_score=None if obj.camera_confidence is None else round(float(obj.camera_confidence), 4),
            category=None if obj.obj_subtype is None else obj.obj_subtype.name,
            lidar_category=None if obj.lidar_type is None else obj.lidar_type.name,
            # camera_category=None if obj.camera_type is None else obj.camera_type.name,
            cross_lane=str(obj.cross_lane),
            # visible=obj.visible,
            occlusion=obj.occlusion,
            truncation=obj.truncation,
            lidar_velocity=None if obj.lidar_velo is None else dict(
                x=round(float(obj.lidar_velo[0]), 4),
                y=round(float(obj.lidar_velo[1]), 4),
                z=round(float(obj.lidar_velo[2]), 4),
            ),
            num_lidar_pts=None if obj.lidar_pts_count is None else int(obj.lidar_pts_count),
            frame_id=obj.frame_id,
            track_id=obj.track_id,
            group_id=obj.group_id or obj.track_id,
            is_group=obj.is_group,
            is_cyclist=obj.is_cyclist,
            is_fake=obj.is_fake,
            lane_id=obj.lane_id,
            signal=obj.signal,
            motion_state=None if obj.motion_state is None else obj.motion_state.name,
        ) for obj in sensor_objects]
        for sensor_name, sensor_objects in frame.objects.items()}
    )


def decode_psr_frame(frame_dict: Dict) -> FrameInfo:
    """
    @param frame_dict: frame dictionary
    return: decoded detection frame
    """
    if frame_dict is None:
        return

    return FrameInfo(
        lidar_timestamp=frame_dict.get('frame_id'),
        objects={SensorName[sensor_name]: [
            ObjectInfo(
                camera_type=None if obj.get('camera_category') is None else CameraObjType[obj['camera_category']],
                camera_confidence=obj.get('obj_score') if SensorName[sensor_name].name in SENSOR_TYPE_CAMERA else None,
                camera_box2d=None if obj.get('bbox') is None else [
                    obj['bbox']['x1'],
                    obj['bbox']['y1'],
                    obj['bbox']['x2'],
                    obj['bbox']['y2']],
                camera_box3d=None if obj.get('camera_box3d') is None else np.asarray(obj['camera_box3d']),
                # visible=obj.get('visible'),
                occlusion=obj.get('occlusion'),
                truncation=obj.get('truncation'),
                lidar_type=None if obj.get('lidar_category') is None else LidarObjType[obj['lidar_category']],
                lidar_confidence=obj.get('obj_score') if SensorName[sensor_name] in SENSOR_TYPE_LIDAR else None,
                lidar_box3d=None if obj.get('psr') is None else [
                    obj['psr']['position']['x'],
                    obj['psr']['position']['y'],
                    obj['psr']['position']['z'],
                    obj['psr']['scale']['x'],
                    obj['psr']['scale']['y'],
                    obj['psr']['scale']['z'],
                    obj['psr']['rotation']['z']],
                lidar_velo=None if obj.get('lidar_velocity') is None else [
                    obj['lidar_velocity']['x'], obj['lidar_velocity']['y'], obj['lidar_velocity']['z']],
                lidar_pts_count=obj.get('num_lidar_pts'),
                frame_id=obj.get('frame_id'),
                track_id=obj.get('track_id'),
                obj_type=None if obj.get('category') is None else SUBTYPE_TO_TYPE[ObjSubType[obj['category']]],
                obj_subtype=None if obj.get('category') is None else ObjSubType[obj['category']],
                timestamp=obj.get('timestamp'),
                group_id=obj.get('group_id'),
                cross_lane=obj.get('cross_lane'),
                is_group=obj.get('is_group'),
                is_cyclist=obj.get('is_cyclist'),
                is_fake=obj.get('is_fake'),
                lane_id=obj.get('lane_id'),
                signal=obj.get('signal'),
                motion_state=None if obj.get('motion_state') is None else MotionState[obj['motion_state']],
            ) for obj in sensor_objects]
        for sensor_name, sensor_objects in frame_dict['objects'].items()}
    )
