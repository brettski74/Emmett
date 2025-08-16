from typing import Tuple
from math import sqrt


def add_vec(v1: Tuple[float, float], v2: Tuple[float, float]) -> Tuple[float, float]:
    return (v1[0] + v2[0], v1[1] + v2[1])

def sub_vec(v1: Tuple[float, float], v2: Tuple[float, float]) -> Tuple[float, float]:
    return (v1[0] - v2[0], v1[1] - v2[1])

def scale_vec(v1: Tuple[float, float], scale: float) -> Tuple[float, float]:
    return (v1[0] * scale, v1[1] * scale)

def shrink_vec(v1: Tuple[float, float], shrink: float) -> Tuple[float, float]:
    return (v1[0] / shrink, v1[1] / shrink)

def normalize_vec(v1: Tuple[float, float], magnitude: float) -> Tuple[float, float]:
    scale = magnitude / sqrt(v1[0] * v1[0] + v1[1] * v1[1])
    return scale_vec(v1, scale)

def perp_vec(v1: Tuple[float, float]) -> Tuple[float, float]:
    return (v1[1], -v1[0])

def invert_vec(v1: Tuple[float, float]) -> Tuple[float, float]:
    return (-v1[0], -v1[1])

def x_mirror_vec(v1: Tuple[float, float]) -> Tuple[float, float]:
    return (-v1[0], v1[1])

def y_mirror_vec(v1: Tuple[float, float]) -> Tuple[float, float]:
    return (v1[0], -v1[1])

def distance(v1: Tuple[float, float], v2: Tuple[float, float]) -> float:
    dx = v1[0] - v2[0]
    dy = v1[1] - v2[1]

    return sqrt(dx*dx + dy*dy)