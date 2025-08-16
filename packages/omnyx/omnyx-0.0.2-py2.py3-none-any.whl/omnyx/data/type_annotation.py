from functools import partial
from typing import Dict, List

from .baseclass import _Enum

__all__ = ['AnnotationType', 'AnnotationPrefix',
           'ANNOTATION_INFO', 'ANNOTATION_TYPE', 'ANNOTATION_ID']


def parse_3d_od_anno_info(anno_dict: Dict, info_prefix: str) -> List:
    return dict(
        lidar0=anno_dict['annotated_info']\
                        [info_prefix]\
                        ['annotated_info']\
                        ['3d_object_detection_info']\
                        ['3d_object_detection_anns_info'])


def parse_3d_gop_anno_info(anno_dict: Dict) -> List:
    return dict(
        lidar0=anno_dict['annotated_record_info']\
                        ['annotated_info']\
                        ['3d_object_detection_info']\
                        ['3d_object_detection_anns_info'])


def parse_23d_od_anno_info(anno_dict: Dict) -> List:
    return dict(
        lidar0=anno_dict['annotated_info']\
                       ['3d_object_annotated_info']\
                       ['annotated_info']\
                       ['3d_object_detection_info']\
                       ['3d_object_detection_anns_info'],
        **anno_dict['annotated_info']\
                   ['2d_object_annotated_info']\
                   ['annotated_info'])


def parse_interped_od_anno_info(anno_dict: Dict) -> List:
    return dict(
        lidar0=anno_dict['annotated_info']\
                       ['3d_city_object_detection_annotated_info']\
                       ['annotated_info']\
                       ['3d_object_detection_info']\
                       ['3d_object_detection_anns_info'],
        **{k: v['objects'] for k, v in anno_dict['annotated_info']\
                   ['2d_city_object_detection_annotated_info']\
                   ['annotated_info'].items()})


def parse_3d_fs_anno_info(anno_dict: Dict) -> List:
    return anno_dict['annotated_info']\
                    ['driving_free_space_frame_annotated_info']\
                    ['annotated_info']\
                    ['free_space']\
                    ['3d_object_detection_anns_info']


def parse_3d_lane_anno_info(anno_dict: Dict) -> List:
    if 'annotated_info' in anno_dict:
        if '3d_lane_annotated_info' in anno_dict['annotated_info']:
            return anno_dict['annotated_info']['3d_lane_annotated_info']['annotated_info']['lines']
        elif '3d_lane_clip_annotated_info' in anno_dict['annotated_info']:
            return anno_dict['annotated_info']['3d_lane_clip_annotated_info']['annotated_info']['lines']
        else:
            return anno_dict['annotated_info']['lines']
    elif 'annotated_record_info' in anno_dict:
        return anno_dict['annotated_record_info']['annotated_info']['lines']
    else:
        return []


def parse_parking_surround_space_anno_info(anno_dict: Dict)-> List:
    return anno_dict['annotated_info']\
                    ['parking_surround_space_detection_frame_annotated_info']\
                    ['annotated_info']\
                    ['parking_space']


class AnnotationType(str, _Enum):
    ROBO_HIGHWAY_OD_23D = '23d_object'
    ROBO_URBAN_OD_3D = 'only_3d_city_object_detection'
    ROBO_HIGHWAY_OD_3D = '23d_object_detection'

    HNOA_URBAN_OD_3D = '3d_city_object_detection_with_fish_eye'
    HNOA_HIGHWAY_OD_3D = '3d_highway_object_detection_with_fish_eye'
    HNOA_PARKING_OD_3D = 'parking_movable_object_detection'

    HNOA_GOP_OD_3D = 'gop_object_detection'
    HNOA_URBAN_GOP_3D = 'driving_gop_object_detection'
    HNOA_PARKING_GOP_3D = 'parking_gop_object_detection'

    HNOA_TRAFFIC_SIGN = '23d_traffic_sign'

    LANE_KEY_POINTS_3D = '3d_lane'
    LANE_KEY_POINTS_4D = 'auto_4d_lane'
    PARKING_KEY_POINTS = 'parking_surround_space_detection'

    INTERPOLATED_PVB = 'pvb_10hz'
    REPROJECTED_GOP = 'gop_10hz'


class AnnotationPrefix(str, _Enum):
    ROBO_URBAN_OD_3D = 'only_3d_city_object_detection_annotated_info'
    ROBO_HIGHWAY_OD_3D = '3d_object_detection_annotated_info'

    HNOA_URBAN_OD_3D = '3d_city_object_detection_with_fish_eye_annotated_info'
    HNOA_HIGHWAY_OD_3D = '3d_highway_object_detection_with_fish_eye_annotated_info'
    HNOA_PARKING_OD_3D = 'parking_movable_object_detection_annotated_info'

    HNOA_GOP_OD_3D = 'gop_object_detection_clip_annotated_info'
    HNOA_TRAFFIC_SIGN = '3d_traffic_sign_clip_annotated_info'


ANNOTATION_INFO = {
    'ROBO_HIGHWAY_OD_23D': parse_23d_od_anno_info,

    'ROBO_URBAN_OD_3D': partial(parse_3d_od_anno_info, info_prefix=AnnotationPrefix.ROBO_URBAN_OD_3D.value),
    'ROBO_HIGHWAY_OD_3D': partial(parse_3d_od_anno_info, info_prefix=AnnotationPrefix.ROBO_HIGHWAY_OD_3D.value),

    'HNOA_URBAN_OD_3D': partial(parse_3d_od_anno_info, info_prefix=AnnotationPrefix.HNOA_URBAN_OD_3D.value),
    'HNOA_HIGHWAY_OD_3D': partial(parse_3d_od_anno_info, info_prefix=AnnotationPrefix.HNOA_HIGHWAY_OD_3D.value),
    'HNOA_PARKING_OD_3D': partial(parse_3d_od_anno_info, info_prefix=AnnotationPrefix.HNOA_PARKING_OD_3D.value),

    'HNOA_GOP_OD_3D': partial(parse_3d_od_anno_info, info_prefix=AnnotationPrefix.HNOA_GOP_OD_3D.value),
    'HNOA_URBAN_GOP_3D': parse_3d_gop_anno_info,
    'HNOA_PARKING_GOP_3D': parse_3d_gop_anno_info,

    'HNOA_TRAFFIC_SIGN': partial(parse_3d_od_anno_info, info_prefix=AnnotationPrefix.HNOA_TRAFFIC_SIGN.value),

    'PARKING_KEY_POINTS': parse_parking_surround_space_anno_info,
    'LANE_KEY_POINTS_3D': parse_3d_lane_anno_info,
    'LANE_KEY_POINTS_4D': parse_3d_lane_anno_info,

    'INTERPOLATED_PVB': parse_interped_od_anno_info,
    'REPROJECTED_GOP': parse_interped_od_anno_info,
}


ANNOTATION_TYPE: Dict[str, List[AnnotationType]] = {
    'PVB': [
        AnnotationType.HNOA_URBAN_OD_3D,
        AnnotationType.HNOA_HIGHWAY_OD_3D,
        AnnotationType.HNOA_PARKING_OD_3D,

        AnnotationType.ROBO_HIGHWAY_OD_23D,
        AnnotationType.ROBO_URBAN_OD_3D,
        AnnotationType.ROBO_HIGHWAY_OD_3D,
    ],
    'GOP': [
        AnnotationType.HNOA_URBAN_GOP_3D,
        AnnotationType.HNOA_PARKING_GOP_3D,
        AnnotationType.HNOA_GOP_OD_3D,
    ],
    'LANE3D': [
        AnnotationType.LANE_KEY_POINTS_3D,
        AnnotationType.LANE_KEY_POINTS_4D,
    ]
}

ANNOTATION_ID = {
    AnnotationType.HNOA_URBAN_OD_3D: 15,
    AnnotationType.HNOA_HIGHWAY_OD_3D: 16,
    AnnotationType.HNOA_PARKING_OD_3D: 17,

    AnnotationType.ROBO_HIGHWAY_OD_23D: 3,
    AnnotationType.ROBO_URBAN_OD_3D: 9,
    AnnotationType.ROBO_HIGHWAY_OD_3D: 10,

    AnnotationType.HNOA_GOP_OD_3D: 23,
    AnnotationType.HNOA_URBAN_GOP_3D: 33,
    AnnotationType.HNOA_PARKING_GOP_3D: 36,

    AnnotationType.LANE_KEY_POINTS_3D: 2,
    AnnotationType.LANE_KEY_POINTS_4D: 18,
    AnnotationType.PARKING_KEY_POINTS: 19,
}

