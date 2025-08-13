# pyright: reportArgumentType=false
import numpy as np
from nerfbaselines import Cameras
from nerfbaselines._types import GenericCamerasImpl


def test_generic_cameras_impl_implements_cameras_protocol():
    cameras = GenericCamerasImpl[np.ndarray](np.ones(1), np.ones(1), np.ones(1), np.ones(1), np.ones(1), None)
    assert isinstance(cameras, Cameras)

