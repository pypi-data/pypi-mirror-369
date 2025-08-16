from os import environ
from pathlib import Path
from re import compile
from shutil import copyfile
from typing import Dict, List

import numpy as np
import yaml

from ..fileio import check_filepath, lsdir, mkdir, read_json, write_json
from ..math.geometry import (convert_velos, quaternion_to_rotmat,
                             rotvec_to_rotmat, transform_matrix)
from ..sensor.camera import calculate_camera_fov
from ..system import logger, multi_process_thread, timestamp_to_time_of_date
from .dataclass import *
from .rules import pose_sanity_check
from .type_sensor import *
from .utils import get_closest_pose, microseconds_to_second

__all__ = ['ClipFileParser', 'get_clip_info']


class ClipFileParser:

    def __init__(
        self,
        clip_root: Path,
        output_path: str = None,
        search_global: bool = False,
        calib_root: str = '/opt/calibration',
        collect_time: int = 0, # microseconds
        plate_no: str = '',
        **whatever,
    ):
        """
        @param clip_root: path to clip
        @param output_path: path to output
        @param seach_global: whether to use calib params at calib_root
        @param calib_root: path to calibration files
        @param collect_time: collect time of clip
        @param plate_no: plate number of vehicle
        """
        self.clip_root = clip_root
        self.output_path = output_path

        self.collect_time = int(timestamp_to_time_of_date(collect_time * 1e-6, '%Y%m%d%H%M%S'))
        self.plate_no = compile(r'[\u4e00-\u9fa5]').sub('', plate_no)
        self.search_global = search_global
        self.get_clip_info_status()
        logger.debug(f'plate_no {self.plate_no}, collect_time {self.collect_time}')

        self.calib_root = check_filepath(calib_root, strict=True)
        if search_global:
            logger.debug(f'search calibration files from {calib_root}')

    def get_clip_info_status(self):
        """
        get vehicle id & imu height
        """
        self.vehicle_id = VehicleID[self.plate_no]

        if self.vehicle_id is None:
            raise NotImplementedError(f'vehicle id {self.plate_no} not registered')

        imu_height = IMU_HEIGHT.get(self.vehicle_id)
        if imu_height is None:
            raise NotImplementedError(f'imu height {self.plate_no} not registered')

        self.imu2ego = transform_matrix([0., 0., imu_height], rotvec_to_rotmat(yaw=-np.pi * 0.5))

    def parse_calib_single(self, sensor_name: SensorName, calibrations: Dict[SensorName, SensorCalib]):
        if sensor_name in SENSOR_TYPE_CAMERA:
            calibrations[sensor_name].update(self.parse_intrinsic_camera(sensor_name))
            calibrations[sensor_name].extrinsic_matrix = self.parse_extrinsic_lidar2camera(sensor_name)
        elif sensor_name in MAIN_SENSOR_LIDAR:
            calibrations[sensor_name].extrinsic_matrix = self.parse_extrinsic_lidar2ego(sensor_name)
            assert calibrations[sensor_name].extrinsic_matrix is not None
        elif sensor_name in SENSOR_TYPE_LIDAR_BLIND_SOPT:
            calibrations[sensor_name].extrinsic_matrix = self.parse_extrinsic_lidar2lidar(sensor_name)
            if calibrations[sensor_name].extrinsic_matrix is None:
                calibrations.pop(sensor_name)
        else:
            logger.warning(f'unknown sensor type {sensor_name}')

    def parse_calib(self, sensor_names: List[SensorName]) -> Dict[SensorName, SensorCalib]:
        """
        Parse calibration files

        @param sensor_names: names of sensors
        """
        calibrations = {sensor: SensorCalib() for sensor in sensor_names}
        multi_process_thread(self.parse_calib_single,
            [[name, calibrations] for name in sensor_names], nprocess=4,
            pool_func='ThreadPoolExecutor', map_func='map', progress_bar=False)

        calibrations[SENSOR_IMU] = SensorCalib(extrinsic_matrix=self.imu2ego)

        return calibrations

    def default_calib_yaml_path(self, yaml_path: str, yaml_name: str) -> Path:
        """
        get default calibration yaml file path
        @param yaml_path: path to calibration yaml file
        @param yaml_name: name of calibration yaml file
        """
        return self.calib_root / yaml_path / f'{yaml_name}.yaml'

    def load_yaml_file(self, yaml_path: str) -> Dict:
        """
        Load calibration yaml file path

        @param yaml_path: path to calibration yaml file
        """
        _yaml_path = check_filepath(yaml_path, strict=False)
        if _yaml_path is not None:
            return yaml.safe_load(_yaml_path.read_text().replace('\t', ' ' * 4))

    def load_json_file(self, json_path: str) -> Path:
        """
        Load localization file path

        @param json_path: path to localization file
        """
        return read_json(self.clip_root / json_path, strict=False)

    def backup_calib_yaml_file(
        self,
        calib_yaml_path: Path,
        yaml_path: str,
        yaml_name: str
    ) -> None:
        """
        Backup calibration yaml file

        @param calib_yaml_path: path to calibration yaml file
        @param yaml_path: path to calibration yaml file
        @param yaml_name: name of calibration yaml file
        """
        if self.output_path is not None and calib_yaml_path.exists():
            target_yaml_path = mkdir(f'{self.output_path}/{yaml_path}') / f'{yaml_name}.yaml'
            if not target_yaml_path.exists() and \
                calib_yaml_path.resolve() != target_yaml_path.resolve() and \
                environ.get('RANK', '0') == '0':
                copyfile(calib_yaml_path, target_yaml_path)

    def backup_json_file(
        self,
        json_path: str,
    ) -> None:
        """
        Backup localization file

        @param json_path: path to localization file
        """
        if self.output_path is not None:
            backup_json_path = self.output_path / json_path
            if not Path(backup_json_path).exists() and \
                self.clip_root.resolve() / json_path != backup_json_path.resolve() and \
                environ.get('RANK', '0') == '0':
                copyfile(self.clip_root / json_path, backup_json_path)

    def get_extrinsic_path(self, yaml_path: str, yaml_name: str) -> Path:
        """
        Get extrinsic calibration file path

        @param yaml_path: path to extrinsic calibration file
        @param yaml_name: name of extrinsic calibration file
        """
        calib_yaml_path = self.default_calib_yaml_path(yaml_path, yaml_name)

        if self.search_global:
            available_calibs = lsdir(self.calib_root / self.vehicle_id.name / yaml_path)

            min_date_diff, _calib_yaml_path = np.inf, None
            for _yaml_path in available_calibs:
                if _yaml_path.stem.isdigit() and (_yaml_path / f'{yaml_name}.yaml').exists():
                    date_diff = np.abs(int(_yaml_path.stem) - self.collect_time)
                    if date_diff < min_date_diff:
                        min_date_diff = min(min_date_diff, date_diff)
                        _calib_yaml_path = _yaml_path / f'{yaml_name}.yaml'

            calib_yaml_path = _calib_yaml_path or calib_yaml_path
            extrinsic_name = yaml_path.split('/')[1]

            if self.vehicle_id.name == 'B781L6' and extrinsic_name in ['lidar2imu'] \
                and self.collect_time < 20240321000000:
                calib_yaml_path = self.calib_root / self.vehicle_id.name / \
                    yaml_path / '20240321000000' / f'{yaml_name}.yaml'

            if self.vehicle_id.name == 'B781L6' and extrinsic_name in ['lidar2camera'] \
                and self.collect_time < 20231013000000:
                calib_yaml_path = self.calib_root / self.vehicle_id.name / \
                    yaml_path / '20231013000000' / f'{yaml_name}.yaml'

        self.backup_calib_yaml_file(calib_yaml_path, yaml_path, yaml_name)

        return calib_yaml_path

    def get_intrinsic_path(self, yaml_path: str, yaml_name: str) -> Path:
        """
        get intrinsic calibration file path
        @param yaml_path: path to intrinsic calibration file
        @param yaml_name: name of intrinsic calibration file
        """
        calib_yaml_path = self.default_calib_yaml_path(yaml_path, yaml_name)

        if self.search_global:
            available_calibs = lsdir(self.calib_root / self.vehicle_id.name / yaml_path / yaml_name)

            min_date_diff, _calib_yaml_path = np.inf, None
            for _yaml_path in available_calibs:
                if _yaml_path.stem.isdigit() and _yaml_path.exists():
                    date_diff = np.abs(int(_yaml_path.stem) - self.collect_time)
                    if date_diff < min_date_diff:
                        min_date_diff = min(min_date_diff, date_diff)
                        _calib_yaml_path = _yaml_path

            calib_yaml_path = _calib_yaml_path or calib_yaml_path

        self.backup_calib_yaml_file(calib_yaml_path, yaml_path, yaml_name)

        return calib_yaml_path

    def parse_intrinsic_camera(self, sensor_name: SensorName) -> Dict:
        """
        parse intrinsic calibration file
        @param sensor_name: name of sensor
        """
        calib_yaml_path = self.get_intrinsic_path(*SENSOR_CALIB_INTRINSICS[sensor_name])
        logger.debug(f'load {sensor_name} intrinsics from {calib_yaml_path}')

        yaml_dict = self.load_yaml_file(calib_yaml_path)
        if yaml_dict is None:
            return

        fx, fy, cx, cy = yaml_dict['K']
        intrinsic_dict = dict(
            distortion_model=yaml_dict['distortion_model'],
            intrinsic_matrix=np.asarray([[fx, 0, cx], [0, fy, cy], [0, 0, 1]]),
            intrinsic_matrix_scaled=np.asarray([[fx, 0, cx], [0, fy, cy], [0, 0, 1]]),
            distortion=np.asarray(yaml_dict['D']),
            width=yaml_dict['width'],
            height=yaml_dict['height'],
        )

        if intrinsic_dict['distortion_model'] in ['equidistant', 'equi', 'radtan']:
            intrinsic_dict['distortion_model'] = 'pinhole'

        if intrinsic_dict['distortion_model'] == 'fisheye':
            intrinsic_dict['distortion'] = intrinsic_dict['distortion'][:4]

        if sensor_name in [SensorName.camera_front_center]:
            undistort_scale = intrinsic_dict['width'] / 2 / np.tan(np.deg2rad(105) / 2) / fx
            intrinsic_dict['intrinsic_matrix_scaled'][:2, :2] *= undistort_scale

        intrinsic_dict.update(fov=calculate_camera_fov(intrinsic_dict),
                              camera_type=CAMERA_TYPE[sensor_name])
        return intrinsic_dict

    def parse_extrinsic_lidar2camera(self, sensor_name: SensorName) -> np.ndarray:
        """
        parse extrinsic calibration file
        @param sensor_name: name of sensor
        """
        calib_yaml_path = self.get_extrinsic_path(*SENSOR_CALIB_EXTRINSICS[sensor_name])
        logger.debug(f'load {sensor_name} to main-lidar extrinsics from {calib_yaml_path}')

        yaml_dict = self.load_yaml_file(calib_yaml_path)
        if yaml_dict is None:
            return

        return np.asarray(yaml_dict['transform'])

    def parse_extrinsic_lidar2lidar(self, sensor_name: SensorName) -> np.ndarray:
        """
        parse extrinsic calibration file
        @param sensor_name: name of sensor
        """
        calib_yaml_path = self.get_extrinsic_path(*SENSOR_CALIB_EXTRINSICS[sensor_name])
        logger.debug(f'load {sensor_name} to main-lidar extrinsics from {calib_yaml_path}')

        yaml_dict = self.load_yaml_file(calib_yaml_path)
        if yaml_dict is None:
            return

        lidar2lidar = transform_matrix(
            [
                yaml_dict['transform']['translation']['x'],
                yaml_dict['transform']['translation']['y'],
                yaml_dict['transform']['translation']['z'],
            ], [
                yaml_dict['transform']['rotation']['x'],
                yaml_dict['transform']['rotation']['y'],
                yaml_dict['transform']['rotation']['z'],
                yaml_dict['transform']['rotation']['w'],
            ],
        )
        return lidar2lidar

    def parse_extrinsic_lidar2ego(self, sensor_name: SensorName) -> np.ndarray:
        """
        parse extrinsic calibration file
        @param sensor_name: name of sensor
        """
        calib_yaml_path = self.get_extrinsic_path(*SENSOR_CALIB_EXTRINSICS[sensor_name])
        logger.debug(f'load {sensor_name} to imu extrinsics from {calib_yaml_path}')

        yaml_dict = self.load_yaml_file(calib_yaml_path)
        if yaml_dict is None:
            return

        lidar2imu = transform_matrix(
            [
                yaml_dict['transform']['translation']['x'],
                yaml_dict['transform']['translation']['y'],
                yaml_dict['transform']['translation']['z'],
            ], [
                yaml_dict['transform']['rotation']['x'],
                yaml_dict['transform']['rotation']['y'],
                yaml_dict['transform']['rotation']['z'],
                yaml_dict['transform']['rotation']['w'],
            ],
        )
        return self.imu2ego @ lidar2imu

    def parse_localizations(
        self,
        lidar2ego: np.ndarray,
        json_path: str = 'localization.json',
    ) -> List[EgoPose]:
        """
        Parse localization file

        @param json_path: path to localization file
        """
        localization_dict = self.load_json_file(json_path)
        if localization_dict is None:
            return None

        self.backup_json_file(json_path)

        poses = []
        for pose_dict in localization_dict:

            timestamp = pose_dict.get('timestamp', pose_dict.get('measurementTime'))

            if timestamp is None:
                continue

            imu_translation = np.asarray([
                pose_dict['pose']['position']['x'],
                pose_dict['pose']['position']['y'],
                pose_dict['pose']['position']['z'],
            ])
            imu_rotation = np.asarray([
                pose_dict['pose']['orientation']['qx'],
                pose_dict['pose']['orientation']['qy'],
                pose_dict['pose']['orientation']['qz'],
                pose_dict['pose']['orientation']['qw'],
            ])
            imu_velocity = np.asarray([
                pose_dict['pose'].get('linear_velocity', pose_dict['pose'].get('linearVelocity'))['x'],
                pose_dict['pose'].get('linear_velocity', pose_dict['pose'].get('linearVelocity'))['y'],
                pose_dict['pose'].get('linear_velocity', pose_dict['pose'].get('linearVelocity'))['z'],
            ])

            imu2utm = transform_matrix(imu_translation, imu_rotation)
            ego2utm = imu2utm @ np.linalg.inv(self.imu2ego)
            lidar2utm = ego2utm @ lidar2ego

            poses.append(EgoPose(
                timestamp=timestamp,
                imu_translation=imu2utm[:3, 3],
                imu_rotation=imu2utm[:3, :3],
                imu_velocity=imu_velocity,
                ego_translation=ego2utm[:3, 3],
                ego_rotation=ego2utm[:3, :3],
                ego_velocity=convert_velos(imu_velocity, np.linalg.inv(ego2utm)),
                lidar_translation=lidar2utm[:3, 3],
                lidar_rotation=lidar2utm[:3, :3],
                lidar_velocity=convert_velos(imu_velocity, np.linalg.inv(lidar2utm)),
            ))
        return sorted(poses, key=lambda pose: pose.timestamp)

    def parse_slam_localizations(
        self,
        lidar2ego: np.ndarray,
        pose0: EgoPose,
        json_path: str = 'corrected_localization.json'
    ) -> List[EgoPose]:
        """
        Parse slam corrected localization file

        @param json_path: path to slam corrected localization file
        """
        localization_dict = self.load_json_file(json_path)
        if localization_dict is None:
            return None

        if isinstance(localization_dict, dict) and 'correct_localization.json' in localization_dict:
            localization_dict = localization_dict['correct_localization.json']

        poses = []
        for pose_dict in localization_dict:
            if 'lidar_localization_pose' in pose_dict:
                lidar_translation = np.asarray([
                    pose_dict['lidar_localization_pose']['position']['x'],
                    pose_dict['lidar_localization_pose']['position']['y'],
                    pose_dict['lidar_localization_pose']['position']['z'],
                ]) + pose0.imu_translation
                lidar_rotation = np.asarray([
                    pose_dict['lidar_localization_pose']['orientation']['x'],
                    pose_dict['lidar_localization_pose']['orientation']['y'],
                    pose_dict['lidar_localization_pose']['orientation']['z'],
                    pose_dict['lidar_localization_pose']['orientation']['w'],
                ])
                timestamp = pose_dict['lidar_localization_pose']['time']

                lidar2utm = transform_matrix(lidar_translation, lidar_rotation)
                ego2utm = lidar2utm @ np.linalg.inv(lidar2ego)
                imu2utm = ego2utm @ self.imu2ego

            else:
                imu_translation = np.asarray([
                    pose_dict['localization_pose']['position']['x'],
                    pose_dict['localization_pose']['position']['y'],
                    pose_dict['localization_pose']['position']['z'],
                ])
                imu_rotation = np.asarray([
                    pose_dict['localization_pose']['orientation']['x'],
                    pose_dict['localization_pose']['orientation']['y'],
                    pose_dict['localization_pose']['orientation']['z'],
                    pose_dict['localization_pose']['orientation']['w'],
                ])
                timestamp = pose_dict['localization_pose']['time']

                imu2utm = transform_matrix(imu_translation, imu_rotation)
                ego2utm = imu2utm @ np.linalg.inv(self.imu2ego)
                lidar2utm = ego2utm @ lidar2ego

            poses.append(EgoPose(
                timestamp=timestamp,
                imu_translation=imu2utm[:3, 3],
                imu_rotation=imu2utm[:3, :3],
                imu_velocity=None,
                ego_translation=ego2utm[:3, 3],
                ego_rotation=ego2utm[:3, :3],
                ego_velocity=None,
                lidar_translation=lidar2utm[:3, 3],
                lidar_rotation=lidar2utm[:3, :3],
                lidar_velocity=None,
            ))

        return sorted(poses, key=lambda pose: pose.timestamp)


def get_clip_info(
    clip_path: Path,
    clip_id: str = None,
    obs_path: str = None,
    search_global: bool = True,
    calib_root: str = '/opt/calibration',
    output_path: str = None,
    info_json: str = 'info.json',
    localization_json: str = 'localization.json',
    slam_info_prefix: str = 'static_obj/lidar_slam',
    sensor_names: List[str] = SENSOR_TYPE_CAMERA + SENSOR_TYPE_LIDAR,
) -> ClipInfo:
    """
    @param clip_path: path to clip
    @param sensor_names: sensor names to be parsed
    @param search_global: whether to search global calib params
    @param calib_root: path to calibration files
    @param output_path: path to save parsed calib params
    @param info_json: path to info.json
    @param localization_json: path to raw localization
    return: parsed clip info
    """
    _clip_path: Path = check_filepath(clip_path).resolve()
    logger.debug(f'checking clip path {_clip_path}')
    clip_json_info = read_json(_clip_path / info_json, strict=False)
    if clip_json_info is None:
        return

    file_parser = ClipFileParser(_clip_path, output_path, search_global, calib_root, **clip_json_info)
    calibrations = file_parser.parse_calib(sensor_names)

    clip_info = ClipInfo(
        vehicle_id=file_parser.vehicle_id,
        weather=clip_json_info['weather'],
        scene=clip_json_info['scene'],
        clip_id=clip_id,
        clip_name=_clip_path.stem,
        clip_path=_clip_path.as_posix(),
        obs_path=obs_path,
        collect_time=clip_json_info['collect_time'],
        calibrations=calibrations,
    )

    clip_info.poses = file_parser.parse_localizations(
        clip_info.calibrations[MAIN_SENSOR_LIDAR].extrinsic_matrix,
        localization_json)

    if not pose_sanity_check(clip_info.poses):
        logger.error('failed pose check')
        return

    clip_info.reference_ego_pose = transform_matrix(clip_info.poses[0].ego_translation)
    clip_info.reference_lidar_pose = transform_matrix(clip_info.poses[0].lidar_translation)

    slam_json_path = lsdir(_clip_path / slam_info_prefix, 'lidar0_stitch_config_*.json')
    if len(slam_json_path) == 1:
        clip_info.slam_poses = file_parser.parse_slam_localizations(
            clip_info.calibrations[MAIN_SENSOR_LIDAR].extrinsic_matrix,
            clip_info.poses[0], slam_json_path[0])

    frame_path_list = lsdir(clip_path, 'sample_*')
    if len(frame_path_list) != len(clip_json_info['frames']):
        logger.warning(f'update frame list in clip_info.json {clip_path}')
        frame_names = ' '.join([f['frame_name'] for f in clip_json_info['frames']])
        for frame_path in frame_path_list:
            if frame_path.name not in frame_names:
                clip_json_info['frames'].append(dict(
                    frame_name=frame_path.name,
                    lidar_collect=int(frame_path.name.replace('sample_', ''))))

    frames_info = multi_process_thread(_fill_single_frame,
        [[_clip_path, frame_dict, sensor_names, clip_info.poses, clip_info.slam_poses]
        for frame_dict in clip_json_info['frames']],
        nprocess=4, pool_func='ThreadPoolExecutor', map_func='map', progress_bar=False)

    clip_info.frames = {info['lidar_timestamp']: info for info in
        sorted(frames_info, key=lambda frame: frame['lidar_timestamp'])}

    logger.debug(f'{len(clip_info.frames)} frames found')
    if output_path is not None and environ.get('RANK', '0') == '0':
        write_json(output_path / 'info.json', clip_json_info)

    return clip_info


def _fill_single_frame(
    clip_path: Path,
    frame_dict: Dict,
    sensor_names: List[SensorName],
    ego_poses: List[EgoPose],
    slam_poses: List[EgoPose], 
):
    sensor_filepaths: Dict[SensorName, Path] = dict()
    for sensor in sensor_names:
        filepath = None
        if sensor.value in frame_dict:
            filepath = clip_path / frame_dict['frame_name'] / frame_dict[sensor.value]

        if sensor.value not in frame_dict or not filepath.exists():
            candidate = [p for p in lsdir(clip_path / frame_dict['frame_name'],
                f'{sensor.value}_*.{"jpg" if sensor in SENSOR_TYPE_CAMERA else "pcd"}')
                if len(p.stem.replace(sensor.value, '')) == 50]

            if len(candidate) == 1:
                filepath = candidate[0]
                logger.warning(f'update filepath in clip_info.json {filepath}')
                frame_dict[sensor.value] = filepath.name
            else:
                filepath = None
        sensor_filepaths[sensor] = filepath

    sensor_filepaths[MAIN_LIDAR_COMPENSATED] = mkdir(clip_path / 'static_obj/lidar_slam/mc_pcds') / \
        f'{frame_dict["frame_name"]}_{sensor_filepaths[MAIN_SENSOR_LIDAR].name}'

    _camera_collect = sensor_filepaths[MAIN_SENSOR_CAMERA].as_posix().split('_')[-2]
    camera_collect = int(_camera_collect)
    if frame_dict.get('camera_collect') != camera_collect:
        frame_dict.update(camera_collect=camera_collect)

    frame_info = FrameInfo(
        clip_name=clip_path.stem,
        frame_name=frame_dict['frame_name'],
        token=frame_dict.get('frame_id'),
        camera_timestamp=camera_collect,
        lidar_timestamp=frame_dict['lidar_collect'], # frame_id
        sensor_timestamps={
            sensor: int(frame_dict[sensor.value].split('_')[1])
            for sensor in sensor_names if sensor.value in frame_dict
        },
        sensor_filepaths=sensor_filepaths,
    )

    if ego_poses is not None:
        curr_pose_raw, _ = get_closest_pose(ego_poses, frame_dict['lidar_collect'])
        frame_info.lidar2utm = transform_matrix(curr_pose_raw.lidar_translation,
                                                curr_pose_raw.lidar_rotation)
        frame_info.ego2utm = transform_matrix(curr_pose_raw.ego_translation,
                                              curr_pose_raw.ego_rotation)
        frame_info.ego_velo = curr_pose_raw.ego_velocity
        frame_info.lidar_velo = curr_pose_raw.lidar_velocity

    if slam_poses is not None:
        curr_slam_pose, _ = get_closest_pose(slam_poses, camera_collect)
        frame_info.lidar2slam = transform_matrix(curr_slam_pose.lidar_translation,
                                                 curr_slam_pose.lidar_rotation)
        frame_info.ego2slam = transform_matrix(curr_slam_pose.ego_translation,
                                               curr_slam_pose.ego_rotation)

    return frame_info
