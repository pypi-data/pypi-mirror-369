from .baseclass import _Enum

__all__ = [
    'CameraObjType', 'LidarObjType', 'ObjType', 'ObjSubType',
    'SensetimeType', 'LaneType', 'MotionState', 'SUBTYPE_TO_TYPE',
    'CAMERA_TO_FUSION_TYPE', 'LIDAR_TO_FUSION_TYPE', 'LIDAR_TO_MOVABLE_TYPE',
    'MOVABLE_VEHICLE', 'MOVABLE_BICYCLE', 'MOVABLE_PERSON', 'UNMOVABLE'
]


class CameraObjType(int, _Enum):
    person = 0
    bicycle = 1
    car = 2
    motorcycle = 3
    bus = 5
    truck = 7
    traffic_light = 9


class LidarObjType(int, _Enum):
    car = 0
    truck = 1
    construction_vehicle = 2
    bus = 3
    tricycle = 4
    motorcycle = 5
    bicycle = 6
    person = 7


class ObjSubType(int, _Enum):
    car = 0
    bus = 1
    truck = 2
    pickup_truck = 3
    trailer = 4
    cement_mixer = 5
    construction_vehicle = 6
    recreational_vehicle = 7
    special_vehicle = 8         # 购物车 婴儿车 轮椅
    unknown_vehicle = 9         # 

    bicycle = 10
    motorcycle = 11
    tricycle = 12

    person = 13
    large_animal = 14
    small_animal = 15

    traffic_cone = 16
    traffic_warning = 17
    warning_post = 18
    construction_sign = 19
    barrier = 20
    anti_collision_barrel = 21
    no_parking_sign = 22
    barrier_gate = 23
    wall_column = 24
    round_column = 25
    lock = 26

    special_pillar = 27
    railing_post = 28
    stone_pier = 29
    trash_bin = 30
    speed_bump = 31
    fire_hydrant_cabinet = 32
    charging_pile = 33

    unknown = -1
    traffic_light = -2
    traffic_sign = -3


class ObjType(int, _Enum):
    car = 0
    bus = 1
    truck = 2

    cyclist = 3
    tricyclist = 4
    pedestrian = 5

    cone = 6
    column = 7

    movable = 8
    unmovable = 9


class SensetimeType(str, _Enum):
    car = 'VEHICLE_CAR'
    trailer = 'TRAILER'
    pickup_truck = 'VEHICLE_PICKUP'
    truck = 'VEHICLE_TRUCK'
    construction_vehicle = 'VEHICLE_CONSTRUCTION'
    cement_mixer = 'CEMENT_MIXER'
    bus = 'VEHICLE_BUS'
    recreational_vehicle = 'RECREATIONAL_VEHICLE'

    motorcycle = 'CYCLIST_MOTOR'
    tricycle = 'VEHICLE_TRIKE'
    bicycle = 'CYCLIST_BICYCLE'
    person = 'PEDESTRIAN_NORMAL'

    traffic_cone = 'CONE'
    barrier = 'BARRIER'
    anti_collision_barrel = 'ISOLATION_BARRIER'
    no_parking_sign = 'NO_PARKING_SIGN'
    traffic_warning = 'TRAFFIC_WARNING_SIGN'
    construction_sign = 'CONSTRUCTION_SIGN'

    barrier_gate = 'BARRIER_GATE'
    warning_post = 'WARNING_POST'
    wall_column = 'WALL_COLUMN'
    round_column = 'WALL_COLUMN'
    lock = 'PARKING_LOCK'

    special_pillar = 'SPECIAL_PILLAR'
    railing_post = 'RAILING_POST'
    stone_pier = 'STONE_PIER'
    trash_bin = 'TRASH_BIN'
    speed_bump = 'SPEED_BUMP'
    fire_hydrant_cabinet = 'FIRE_HYDRANT_CABINET'
    charging_pile = 'CHARGING_PILE'

    special_vehicle = 'SPECIAL_VEHICLE'
    unknown_vehicle = 'UNKNOWN_VEHICLE'

    small_animal = 'SMALL_ANIMAL'
    large_animal = 'LARGE_ANIMAL'
    unknown = 'UNKNOWN'
    traffic_sign = 'TRAFFIC_SIGN'


class LaneType(int, _Enum):
    single_dash = 0
    single_solid = 1
    road_edge = 2
    dense_wide_dash = 3
    others = 4


class MotionState(str, _Enum):
    uncertain = 0
    stationary = 1
    moving = 2


CAMERA_TO_FUSION_TYPE = {
    CameraObjType.person: ObjSubType.person,
    CameraObjType.bicycle: ObjSubType.bicycle,
    CameraObjType.car: ObjSubType.car,
    CameraObjType.motorcycle: ObjSubType.motorcycle,
    CameraObjType.bus: ObjSubType.bus,
    CameraObjType.truck: ObjSubType.truck,
    CameraObjType.traffic_light: ObjSubType.traffic_light,
}
LIDAR_TO_FUSION_TYPE = {
    LidarObjType.car: ObjSubType.car,
    LidarObjType.truck: ObjSubType.truck,
    LidarObjType.construction_vehicle: ObjSubType.construction_vehicle,
    LidarObjType.bus: ObjSubType.bus,
    LidarObjType.tricycle: ObjSubType.tricycle,
    LidarObjType.motorcycle: ObjSubType.motorcycle,
    LidarObjType.bicycle: ObjSubType.bicycle,
    LidarObjType.person: ObjSubType.person,
}
SUBTYPE_TO_TYPE = {
    ObjSubType.car: ObjType.car,
    ObjSubType.bus: ObjType.bus,
    ObjSubType.truck: ObjType.truck,
    ObjSubType.pickup_truck: ObjType.truck,
    ObjSubType.trailer: ObjType.truck,
    ObjSubType.cement_mixer: ObjType.truck,
    ObjSubType.construction_vehicle: ObjType.truck,
    ObjSubType.recreational_vehicle: ObjType.car,
    ObjSubType.special_vehicle: ObjType.movable,
    ObjSubType.unknown_vehicle: ObjType.movable,

    ObjSubType.bicycle: ObjType.cyclist,
    ObjSubType.motorcycle: ObjType.cyclist,
    ObjSubType.tricycle: ObjType.tricyclist,

    ObjSubType.person: ObjType.pedestrian,
    ObjSubType.large_animal: ObjType.movable,
    ObjSubType.small_animal: ObjType.movable,

    ObjSubType.traffic_cone: ObjType.cone,
    ObjSubType.traffic_warning: ObjType.cone,
    ObjSubType.warning_post: ObjType.cone,
    ObjSubType.construction_sign: ObjType.cone,
    ObjSubType.barrier: ObjType.cone,
    ObjSubType.anti_collision_barrel: ObjType.cone,
    ObjSubType.no_parking_sign: ObjType.cone,
    ObjSubType.barrier_gate: ObjType.unmovable,
    ObjSubType.wall_column: ObjType.column,
    ObjSubType.round_column: ObjType.column,
    ObjSubType.lock: ObjType.unmovable,

    ObjSubType.special_pillar: ObjType.cone,
    ObjSubType.railing_post: ObjType.cone,
    ObjSubType.stone_pier: ObjType.cone,
    ObjSubType.trash_bin: ObjType.cone,
    ObjSubType.speed_bump: ObjType.cone,
    ObjSubType.fire_hydrant_cabinet: ObjType.cone,
    ObjSubType.charging_pile: ObjType.cone,

    ObjSubType.traffic_light: ObjType.unmovable,
    ObjSubType.traffic_sign: ObjType.unmovable,
    ObjSubType.unknown: ObjType.unmovable,
}


MOVABLE_VEHICLE = [
    ObjSubType.car,
    ObjSubType.bus,
    ObjSubType.truck,
    ObjSubType.pickup_truck,
    ObjSubType.trailer,
    ObjSubType.construction_vehicle,
    ObjSubType.recreational_vehicle,
    ObjSubType.cement_mixer,
    ObjSubType.special_vehicle,
    ObjSubType.unknown_vehicle,
]
MOVABLE_BICYCLE = [
    ObjSubType.bicycle,
    ObjSubType.tricycle,
    ObjSubType.motorcycle,
]
MOVABLE_PERSON = [
    ObjSubType.person,
    ObjSubType.small_animal,
    ObjSubType.large_animal,
]
UNMOVABLE = [
    ObjSubType.traffic_cone,
    ObjSubType.traffic_warning,
    ObjSubType.warning_post,
    ObjSubType.construction_sign,
    ObjSubType.barrier,
    ObjSubType.anti_collision_barrel,
    ObjSubType.no_parking_sign,
    ObjSubType.barrier_gate,
    ObjSubType.wall_column,
    ObjSubType.round_column,
    ObjSubType.lock,
    ObjSubType.special_pillar,
    ObjSubType.railing_post,
    ObjSubType.stone_pier,
    ObjSubType.trash_bin,
    ObjSubType.speed_bump,
    ObjSubType.fire_hydrant_cabinet,
    ObjSubType.charging_pile,
    ObjSubType.traffic_sign
]
LIDAR_TO_MOVABLE_TYPE = {
    LidarObjType.car: 'MOVABLE_VEHICLE',
    LidarObjType.truck: 'MOVABLE_VEHICLE',
    LidarObjType.construction_vehicle: 'MOVABLE_VEHICLE',
    LidarObjType.bus: 'MOVABLE_VEHICLE',
    LidarObjType.tricycle: 'MOVABLE_BICYCLE',
    LidarObjType.motorcycle: 'MOVABLE_BICYCLE',
    LidarObjType.bicycle: 'MOVABLE_BICYCLE',
    LidarObjType.person: 'MOVABLE_PERSON',
}