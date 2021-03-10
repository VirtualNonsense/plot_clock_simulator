import math

import numpy as np
from typing import *


def loc(a, b, c):
    """
    law of cosines - returns the angle between a and b in a triangle
    :param a: length next to the desired angle
    :param b: length next to the desired angle
    :param c: side opposing the desired angle
    :return: the angle between a and b in rad.
    """
    cos_gamma = (a ** 2 + b ** 2 - c ** 2) / (2 * a * b)
    return np.arccos(cos_gamma)


def get_intersections(x0: float, y0: float, r0: float, x1: float, y1: float, r1: float) \
        -> Union[None, Tuple[float, float, float, float]]:
    """
    http://paulbourke.net/geometry/circlesphere/
    :param x0:
    :param y0:
    :param r0:
    :param x1:
    :param y1:
    :param r1:
    :return:
    """
    d = math.sqrt((x1 - x0) ** 2 + (y1 - y0) ** 2)

    # non intersecting
    if d > r0 + r1:
        return None
    # One circle within other
    if d < abs(r0 - r1):
        return None
    # coincident circles
    if d == 0 and r0 == r1:
        return None
    else:
        a = (r0 ** 2 - r1 ** 2 + d ** 2) / (2 * d)
        h = math.sqrt(r0 ** 2 - a ** 2)
        x2 = x0 + a * (x1 - x0) / d
        y2 = y0 + a * (y1 - y0) / d
        x3 = x2 + h * (y1 - y0) / d
        y3 = y2 - h * (x1 - x0) / d

        x4 = x2 - h * (y1 - y0) / d
        y4 = y2 + h * (x1 - x0) / d

        return x3, y3, x4, y4


def point_to_angles(x, y, lower_arm_length, upper_arm_length, distance):
    q_alpha = np.sqrt(np.abs(x ** 2) + np.abs(y ** 2)) if x != 0 else np.abs(y)
    alpha_1 = loc(q_alpha, lower_arm_length, upper_arm_length)
    alpha_2 = np.arctan(y / x) if x != 0 else np.pi / 2
    l_target_angle = alpha_1 + alpha_2

    r_x = distance - x
    q_beta = np.sqrt(np.abs(r_x ** 2) + np.abs(y ** 2)) if r_x != 0 else np.abs(y)

    beta_1 = loc(q_beta, lower_arm_length, upper_arm_length)
    beta_2 = np.arctan(y / r_x) if r_x != 0 else np.pi / 2
    r_target_angle = np.pi - (beta_1 + beta_2)
    return l_target_angle, r_target_angle
