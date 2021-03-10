import asyncio
from typing import *

import numpy as np

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
        self.__r_target_angle: float = np.pi / 2
        self.__l_angle: float = np.pi / 2
        self.__l_target_angle: float = np.pi / 2
        self.__upper_arm_length = upper_arm_length
        self.__lower_arm_length = lower_arm_length
        self.__distance = servo_distance
        self.servo_speed = servo_speed
        self.__t_x: float = 0
        self.__t_y: float = 0
        self.__x: float = 0
        self.__y: float = 0
        self.angle_tolerance = servo_speed * 2

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
        return [self.__x, self.__y]

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
        coord = [self.left_servo, self.left_joint, self.pen_joint, self.right_joint, self.right_servo]
        xs, ys = zip(*coord)  # create lists of x and y values
        return xs, ys

    # ##################################################################################################################
    # public methods
    # ##################################################################################################################
    async def got_to(self, x: float, y: float):
        self.__t_x = x
        self.__t_y = y
        self.__calc_angles()
        await self.__move_to_angle()

    # ##################################################################################################################
    # private methods
    # ##################################################################################################################
    def __calc_angles(self):
        x = self.__t_x
        y = self.__t_y
        q_alpha = np.sqrt(np.abs(x ** 2) + np.abs(y ** 2)) if x != 0 else np.abs(y)
        alpha_1 = loc(q_alpha, self.__lower_arm_length, self.__upper_arm_length)
        alpha_2 = np.arctan(y / x) if x != 0 else np.pi / 2
        self.__l_target_angle = alpha_1 + alpha_2

        r_x = self.__distance - x
        q_beta = np.sqrt(np.abs(r_x ** 2) + np.abs(y ** 2)) if r_x != 0 else np.abs(y)

        beta_1 = loc(q_beta, self.__lower_arm_length, self.__upper_arm_length)
        beta_2 = np.arctan(y / r_x) if r_x != 0 else np.pi / 2
        self.__r_target_angle = np.pi - (beta_1 + beta_2)

    async def __move_to_angle(self):
        while not self.__target_angles_reached():
            sgn = np.sign(self.__r_target_angle - self.__r_angle)
            self.__r_angle += sgn * self.servo_speed
            sgn = np.sign(self.__l_target_angle - self.__l_angle)
            self.__l_angle += sgn * self.servo_speed
            self.__calc_pos()
            await asyncio.sleep(.01)

    def __target_angles_reached(self) -> bool:
        return np.abs(self.__r_target_angle - self.__r_angle) < self.angle_tolerance \
               and np.abs(self.__l_target_angle - self.__l_angle) < self.angle_tolerance

    def __calc_pos(self):
        q = self.__lower_arm_length * (np.sin(self.__l_angle) - np.sin(self.__r_angle))
        q_2 = np.power(q, 2)
        cos_a = np.cos(self.__l_angle)
        cos_b = np.cos(self.__r_angle)
        l1 = self.__lower_arm_length
        l1_2 = np.power(self.__lower_arm_length, 2)
        d = self.__distance
        d_2 = np.power(self.__distance, 2)
        d_3 = np.power(self.__distance, 3)
        d_4 = np.power(self.__distance, 4)
        sin_b = np.sin(self.__r_angle)
        cos_a_2 = np.power(cos_a, 2)
        cos_b_2 = np.power(cos_b, 2)

        a = 1 + (-2 * cos_a * cos_b
                 - 2 * l1 * d * cos_a
                 + l1_2 * cos_a_2
                 + 2 * d * l1 * cos_b
                 + l1_2 * cos_b_2 + d_2) \
            / q_2

        b = -2 * l1 * cos_a \
            + (2 * d * l1_2 * cos_a * cos_b
               + d_2 * l1 * cos_a
               - 3 * d_2 * l1 * cos_b
               - 2 * d * l1_2 * cos_b
               - d_3
               - 2 * l1 * sin_b * (d + l1 * cos_b - l1 * cos_a)) \
            / q

        c = l1_2 * cos_a_2 \
            + (d_3 * l1 * cos_b
               + d_2 * l1_2 * cos_b_2
               + d_4 / 4) \
            / q_2 \
            + (l1 * sin_b * d_2
               + 2 * l1_2 * sin_b * cos_b * d) \
            / q \
            + l1_2 * np.power(sin_b, 2) \
            - np.power(self.__upper_arm_length, 2)

        D = np.power(b, 2) - 4 * a * c
        # print(f"{a}, {b}, {c}, {D}")

        y = lambda x: ((d + l1 * cos_b - l1 * cos_a) * x - .5 * d - d * l1 - cos_b) / q
        x1 = (-b + np.sqrt(D)) / (2*a)
        x2 = (-b - np.sqrt(D)) / (2*a)
        y1 = y(x1)
        y2 = y(x2)
        print(f"{x1}, {y1}; {x2}, {y2}")
        if y1 > y2:
            self.__x = x1
            self.__y = y1
            return

        self.__x = x2
        self.__y = y2
