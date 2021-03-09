import numpy as np


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
