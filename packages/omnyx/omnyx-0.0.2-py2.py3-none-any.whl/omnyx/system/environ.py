import os
from pathlib import Path

__all__ = ['AUTOLABEL_PATH']


if 'AUTOLABEL_PATH' not in os.environ:
    autolabel_root = Path(__file__).parents[2]
    raise NotImplementedError(f'source {autolabel_root}/env.sh needed')

AUTOLABEL_PATH = Path(os.environ['AUTOLABEL_PATH'])