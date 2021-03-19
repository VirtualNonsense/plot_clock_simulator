import asyncio
from typing import *

import numpy as np

from math_util import loc, get_intersections, point_to_angles


class DataBuffer:
    def __init__(self, length):
        self.__max_length = length
        self.window: list = []

    def add(self, element: List):
        self.window.append(element)
        if len(self.window) > self.__max_length:
            self.window.pop(0)

    def add_range(self, elements: List[Any]):
        for e in elements:
            self.add(e)

    @property
    def length(self) -> int:
        return len(self.window)


class PlotClock:
    def __init__(self, upper_arm_length: float,
                 lower_arm_length: float,
                 servo_distance: float,
                 servo_speed: float,
                 trail_length: int = 2000):
        self.__r_angle: float = np.pi / 2
        self.__r_target_angle: float = np.pi / 2
        self.__l_angle: float = np.pi / 2
        self.__l_target_angle: float = np.pi / 2
        self.__upper_arm_length = upper_arm_length
        self.__lower_arm_length = lower_arm_length
        self.__distance = servo_distance
        self.servo_max_speed = servo_speed
        self.servo_min_speed = servo_speed * 0.1
        self.pen_trail_window = DataBuffer(trail_length)
        self.angle_trail_window = DataBuffer(trail_length)
        self.target_trail_window = DataBuffer(2)
        self.__t_x: float = 0
        self.__t_y: float = 0
        self.angle_tolerance = self.servo_min_speed * 2
        self.pen_trail_window.add(self.pen_joint_pos)

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
        if len(self.pen_trail_window.window) < 1:
            return [None, None]
        return self.pen_trail_window.window[-1]

    @property
    def target_pen_joint(self):
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

    @property
    def pen_trail(self):
        if len(self.pen_trail_window.window) < 1:
            return 0, 0
        xs, ys = zip(*self.pen_trail_window.window)
        return xs, ys

    @property
    def target_trail(self):
        if len(self.target_trail_window.window) < 1:
            return 0, 0
        xs, ys = zip(*self.target_trail_window.window)
        return xs, ys

    @property
    def angle_trail(self):
        if len(self.angle_trail_window.window) < 1:
            return 0, 0
        xs, ys = zip(*self.angle_trail_window.window)
        return xs, ys

    @property
    def pen_joint_pos(self) -> Union[None, List[float]]:
        intersections = get_intersections(self.left_joint[0], self.left_joint[1], self.__upper_arm_length,
                                          self.right_joint[0], self.right_joint[1], self.__upper_arm_length)

        if intersections is None:
            return None

        x1, y1, x2, y2 = intersections

        if y1 > y2:
            return [x1, y1]

        return [x2, y2]

    # ##################################################################################################################
    # public methods
    # ##################################################################################################################
    async def got_to(self, x: float, y: float):
        self.__t_x = x
        self.__t_y = y
        self.target_trail_window.add(self.target_pen_joint)
        if len(self.target_trail_window.window) > 1:
            last_x, last_y = self.target_trail_window.window[-2]
            d_x = x - last_x
            d_y = y - last_y
            distance = 8 * np.sqrt(np.power(d_x, 2) + np.power(d_y, 2))
            distance = distance if distance > 1 else 1
            for i in range(int(distance)):
                self.__calc_angles(last_x + i * d_x / distance, last_y + i * d_y / distance)
                await self.__move_to_angle()
            return
        self.__calc_angles(x, y)
        await self.__move_to_angle()
        return

    # ##################################################################################################################
    # private methods
    # ##################################################################################################################
    def __calc_angles(self, x, y):
        angles = point_to_angles(x, y, self.__lower_arm_length, self.__upper_arm_length,
                                 self.__distance)
        self.angle_trail_window.add([angles[0] / np.pi, angles[1] / np.pi])
        self.__l_target_angle = angles[0]
        self.__r_target_angle = angles[1]

    async def __move_to_angle(self):
        l_ratios = DataBuffer(2)
        r_ratios = DataBuffer(2)
        while not self.__target_angles_reached():
            r_angle_diff = self.__r_target_angle - self.__r_angle
            l_angle_diff = self.__l_target_angle - self.__l_angle
            max_angle_diff = np.max([np.abs(r_angle_diff), np.abs(l_angle_diff)])
            r_ratios.add(r_angle_diff / max_angle_diff)
            l_ratios.add(l_angle_diff / max_angle_diff)
            if r_ratios.length > 1 and np.sign(r_ratios.window[-2]) != np.sign(r_ratios.window[-1]):
                break
            if l_ratios.length > 1 and np.sign(l_ratios.window[-2]) != np.sign(l_ratios.window[-1]):
                break
            self.__r_angle += r_ratios.window[-1] * self.servo_max_speed
            self.__l_angle += l_ratios.window[-1] * self.servo_max_speed
            self.pen_trail_window.add(self.pen_joint_pos)
            await asyncio.sleep(.01)

    def __target_angles_reached(self) -> bool:
        return np.abs(self.__r_target_angle - self.__r_angle) < self.angle_tolerance \
               and np.abs(self.__l_target_angle - self.__l_angle) < self.angle_tolerance

