from .baseclass import _Enum


class SensorName(str, _Enum):
    camera_front_center =       'camera0'
    camera_front_center_tele =  'camera1'
    camera_front_left =         'camera2'
    camera_rear_left =          'camera3'
    camera_front_right =        'camera4'
    camera_rear_right =         'camera5'
    camera_rear_center =        'camera6'

    camera_omni_left =          'camera7'
    camera_omni_rear =          'camera8'
    camera_omni_front =         'camera9'
    camera_omni_right =         'camera10'

    lidar_top_pandar128 =       'lidar0'
    lidar_blind_spot_left =     'lidar1'
    lidar_blind_spot_front =    'lidar2'
    lidar_blind_spot_right =    'lidar3'
    lidar_blind_spot_rear =     'lidar4'
    lidar_m2_front =            'lidar5'


class SensetimeSensorName(str, _Enum):
    front_wide_camera = 'camera0'
    front_main_camera = 'camera1'
    left_front_camera = 'camera2'
    left_rear_camera = 'camera3'
    right_front_camera = 'camera4'
    right_rear_camera = 'camera5'
    rear_main_camera = 'camera6'

    fisheye_left_camera = 'camera7'
    fisheye_rear_camera = 'camera8'
    fisheye_front_camera = 'camera9'
    fisheye_right_camera = 'camera10'

    lidar = 'lidar0'


class CameraType(str, _Enum):
    pinhole_30 = 0
    pinhole_105 = 1
    pinhole_120 = 2
    pinhole_60 = 3
    omni_180 = 4


class VehicleID(str, _Enum):
    B781L6 =    '揽月_01'
    B550M0 =    '揽月_02'
    B559Q1 =    '艾瑞泽_03'

    AF080 =     'T28_12'
    B8340 =     'T28_14'
    F58584 =    'T28_16'
    BF81597 =   'T28_17'
    FA1583 =    'T28_19'

    B8044 =     'E03_01'
    BDJ0636 =   'E03_05'
    DJ5363 =    'E03_06'
    BQ597 =     'E03_07'
    S106LS =    'E03_08'
    E03309 =    'E03_09'
    E03630 =    'E03_10'


MAIN_SENSOR_CAMERA = SensorName.camera_front_center_tele
MAIN_SENSOR_LIDAR = SensorName.lidar_top_pandar128

SENSOR_TYPE_CAMERA_FRONT_VIEW = [
    SensorName.camera_front_center_tele,
    SensorName.camera_front_left,
    SensorName.camera_front_center,
    SensorName.camera_front_right,
]
SENSOR_TYPE_CAMERA_REAR_VIEW = [
    SensorName.camera_rear_left,
    SensorName.camera_rear_center,
    SensorName.camera_rear_right,
]
SENSOR_TYPE_CAMERA_OMNI = [
    SensorName.camera_omni_front,
    SensorName.camera_omni_right,
    SensorName.camera_omni_rear,
    SensorName.camera_omni_left,
]
SENSOR_TYPE_LIDAR_BLIND_SOPT = [
    SensorName.lidar_blind_spot_left,
    SensorName.lidar_blind_spot_front,
    SensorName.lidar_blind_spot_right,
    SensorName.lidar_blind_spot_rear,
]

SENSOR_TYPE_CAMERA = SENSOR_TYPE_CAMERA_FRONT_VIEW + SENSOR_TYPE_CAMERA_REAR_VIEW + SENSOR_TYPE_CAMERA_OMNI
SENSOR_TYPE_LIDAR = [MAIN_SENSOR_LIDAR] + SENSOR_TYPE_LIDAR_BLIND_SOPT
SENSOR_IMU = 'imu'
MAIN_LIDAR_COMPENSATED = 'compensated'

CAMERA_TYPE = {
    SensorName.camera_front_center: CameraType.pinhole_120,
    SensorName.camera_front_center_tele: CameraType.pinhole_30,
    SensorName.camera_front_left: CameraType.pinhole_105,
    SensorName.camera_rear_left: CameraType.pinhole_105,
    SensorName.camera_front_right: CameraType.pinhole_105,
    SensorName.camera_rear_right: CameraType.pinhole_105,
    SensorName.camera_rear_center: CameraType.pinhole_60,
    SensorName.camera_omni_left: CameraType.omni_180,
    SensorName.camera_omni_rear: CameraType.omni_180,
    SensorName.camera_omni_front: CameraType.omni_180,
    SensorName.camera_omni_right: CameraType.omni_180,
}
CAMERA_NAME_SHORT = {
    SensorName.camera_front_left: 'FL',
    SensorName.camera_front_center: 'FC',
    SensorName.camera_front_right: 'FR',
    SensorName.camera_rear_left: 'RL',
    SensorName.camera_rear_center: 'RC',
    SensorName.camera_rear_right: 'RR',
    SensorName.camera_front_center_tele: 'FT',
    SensorName.camera_omni_front: 'FRONT',
    SensorName.camera_omni_right: 'RIGHT',
    SensorName.camera_omni_rear: 'REAR',
    SensorName.camera_omni_left: 'LEFT',
}


SENSOR_CALIB_EXTRINSICS = {
    SensorName.camera_front_center: ['extrinsics/lidar2camera', 'lidar2frontwide'],
    SensorName.camera_front_center_tele: ['extrinsics/lidar2camera', 'lidar2frontmain'],
    SensorName.camera_front_left: ['extrinsics/lidar2camera', 'lidar2leftfront'],
    SensorName.camera_front_right: ['extrinsics/lidar2camera', 'lidar2rightfront'],
    SensorName.camera_rear_left: ['extrinsics/lidar2camera', 'lidar2leftrear'],
    SensorName.camera_rear_right: ['extrinsics/lidar2camera', 'lidar2rightrear'],
    SensorName.camera_rear_center: ['extrinsics/lidar2camera', 'lidar2rearmain'],
    SensorName.camera_omni_left: ['extrinsics/lidar2camera', 'lidar2fisheyeleft'],
    SensorName.camera_omni_rear: ['extrinsics/lidar2camera', 'lidar2fisheyerear'],
    SensorName.camera_omni_front: ['extrinsics/lidar2camera', 'lidar2fisheyefront'],
    SensorName.camera_omni_right: ['extrinsics/lidar2camera', 'lidar2fisheyeright'],
    SensorName.lidar_top_pandar128: ['extrinsics/lidar2imu', 'lidar2imu'],
    SensorName.lidar_blind_spot_left: ['extrinsics/lidar2lidar', 'left2mainlidar'],
    SensorName.lidar_blind_spot_front: ['extrinsics/lidar2lidar', 'front2mainlidar'],
    SensorName.lidar_blind_spot_right: ['extrinsics/lidar2lidar', 'right2mainlidar'],
    SensorName.lidar_blind_spot_rear: ['extrinsics/lidar2lidar', 'rear2mainlidar'],
}
SENSOR_CALIB_INTRINSICS = {
    SensorName.camera_front_center: ['intrinsics', 'front_wide_camera'],
    SensorName.camera_front_center_tele: ['intrinsics', 'front_main_camera'],
    SensorName.camera_front_left: ['intrinsics', 'left_front_camera'],
    SensorName.camera_front_right: ['intrinsics', 'right_front_camera'],
    SensorName.camera_rear_left: ['intrinsics', 'left_rear_camera'],
    SensorName.camera_rear_right: ['intrinsics', 'right_rear_camera'],
    SensorName.camera_rear_center: ['intrinsics', 'rear_main_camera'],
    SensorName.camera_omni_left: ['intrinsics', 'fisheye_left_camera'],
    SensorName.camera_omni_rear: ['intrinsics', 'fisheye_rear_camera'],
    SensorName.camera_omni_front: ['intrinsics', 'fisheye_front_camera'],
    SensorName.camera_omni_right: ['intrinsics', 'fisheye_right_camera'],
}

IMU_HEIGHT = {
    VehicleID.B781L6: 0.13,         # 揽月
    VehicleID.B550M0: 0.13,         # 揽月
    VehicleID.B559Q1: 0.13,         # 艾瑞泽

    VehicleID.AF080: 0.28,          # T28
    VehicleID.B8340: 0.28,          # T28
    VehicleID.BF81597: 0.28,        # T28
    VehicleID.F58584: 0.28,         # T28
    VehicleID.FA1583: 0.28,         # T28

    VehicleID.B8044: 0.20,          # E03
    VehicleID.BDJ0636: 0.20,        # E03
    VehicleID.DJ5363: 0.20,         # E03
    VehicleID.BQ597: 0.20,          # E03
    VehicleID.S106LS: 0.20,         # E03
    VehicleID.E03309: 0.20,         # E03
    VehicleID.E03630: 0.20,         # E03
}
