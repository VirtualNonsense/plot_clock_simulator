import asyncio
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.axes import Axes as Axes
from matplotlib.figure import Figure as Figure
from typing import *

from math_util import loc


class Queue:
    def __init__(self):
        self.__list: List[str] = []

    def put(self, input: str):
        self.__list.append(input)

    def pop(self):
        self.__list.pop(0)


class PlotClock:
    def __init__(self, upper_arm_length: float, lower_arm_length: float, servo_distance: float, servo_speed: float):
        self.__r_angle: float = np.pi / 2
        self.__l_angle: float = np.pi / 2
        self.__upper_arm_length = upper_arm_length
        self.__lower_arm_length = lower_arm_length
        self.__distance = servo_distance
        self.servo_speed = servo_speed
        self.__t_x: float = 0
        self.__t_y: float = 0

    # ##################################################################################################################
    # Properties
    # ##################################################################################################################
    @property
    def left_servo(self) -> List[int]:
        return [0, 0]

    @property
    def right_servo(self) -> List[int]:
        return [self.__distance, 0]

    @property
    def pen_joint(self):
        return

    @property
    def theory_pen_joint(self):
        return [self.__t_x, self.__t_y]

    @property
    def left_joint(self) -> List[int]:
        return [self.__lower_arm_length * np.cos(self.__l_angle), self.__lower_arm_length * np.sin(self.__l_angle)]

    @property
    def right_joint(self) -> List[int]:
        return [self.__lower_arm_length * np.cos(self.__r_angle) + self.__distance,
                self.__lower_arm_length * np.sin(self.__r_angle)]

    @property
    def servo_angles(self):
        return np.array([self.__l_angle, self.__r_angle])

    @property
    def arms(self) -> Tuple[List[int], List[int]]:
        coord = [self.left_servo, self.left_joint, self.theory_pen_joint, self.right_joint, self.right_servo]
        xs, ys = zip(*coord)  # create lists of x and y values
        return xs, ys

    # ##################################################################################################################
    # public methods
    # ##################################################################################################################
    def got_to(self, x: float, y: float):
        self.__t_x = x
        self.__t_y = y
        q_alpha = np.sqrt(np.abs(x ** 2) + np.abs(y ** 2)) if x != 0 else np.abs(y)
        alpha_1 = loc(q_alpha, self.__lower_arm_length, self.__upper_arm_length)
        alpha_2 = np.arctan(y / x) if x != 0 else np.pi / 2
        self.__l_angle = alpha_1 + alpha_2

        r_x = self.__distance - x
        q_beta = np.sqrt(np.abs(r_x ** 2) + np.abs(y ** 2)) if r_x != 0 else np.abs(y)

        beta_1 = loc(q_beta, self.__lower_arm_length, self.__upper_arm_length)

        beta_2 = np.arctan(y / r_x) if r_x != 0 else np.pi / 2
        self.__r_angle = np.pi - (beta_1 + beta_2)

    # ##################################################################################################################
    # private methods
    # ##################################################################################################################
    def __calc_pos(self):
        y = - np.tan((self.__l_angle + self.__r_angle) / 2)

        l1 = self.__lower_arm_length
        l2 = self.__upper_arm_length
        cosa = np.cos(self.__l_angle)
        sina = np.sin(self.__l_angle)
        # D = np.power(2*l1*cosa, 2) - 4 * (np.power(l1*cosa, 2) + np.power(y, 2) + 2*y*l1*sina + np.power())
