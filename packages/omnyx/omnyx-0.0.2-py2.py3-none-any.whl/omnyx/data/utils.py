from typing import Dict, List, Tuple

import numpy as np

from ..math.geometry import transform_matrix
from .dataclass import EgoPose

__all__ = ['get_closest_pose', 'microseconds_to_second', 'safe_pop',
           'merge_dicts']


def get_closest_pose(
    poses: List[EgoPose],
    target_timestamp: int,
    coordinate: str = None,
) -> Tuple[EgoPose, int]:
    """
    Get the closest pose to the target timestamp

    @param pose_record: list of ego poses
    @param target_timestamp: target timestamp
    return: closest pose and its index
    """
    pose_timestamps = np.asarray([pose.timestamp for pose in poses])
    closest_ind = np.fabs(pose_timestamps - target_timestamp * 1e-6).argmin()
    this_pose = poses[closest_ind]

    if coordinate is not None:
        this_pose = transform_matrix(
            getattr(poses[closest_ind], f'{coordinate}_translation'),
            getattr(poses[closest_ind], f'{coordinate}_rotation')
        )
    return this_pose, closest_ind


def microseconds_to_second(
    microseconds: int,
    as_string: bool = False
) -> float:
    """
    Milliseconds [16-digis] * 1e-6 will not always keep the same value
    """
    microseconds_str = microseconds if isinstance(microseconds, str) else str(microseconds)
    seconds_str = '.'.join([microseconds_str[:10], microseconds_str[10:]])
    if as_string:
        return seconds_str
    return float(seconds_str)


def safe_pop(dict_obj: Dict, key: str) -> None:
    """
    Safely pop the key from the dictionary
    """
    if key in dict_obj:
        dict_obj.pop(key)


def merge_dicts(*dict_args):
    """
    Given any number of dicts, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts.
    """
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result
