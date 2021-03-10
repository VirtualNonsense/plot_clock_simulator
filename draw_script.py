import asyncio
from typing import *
from argparse import ArgumentParser
from enum import IntEnum

import matplotlib.pyplot as plt
from matplotlib.axes import Axes as Axes
from matplotlib.figure import Figure as Figure
import numpy as np

from plot_clock import PlotClock


async def __got_to_indefinitely(plot_clock: PlotClock, points: List[List[float]]):
    while True:
        for p in points:
            await plot_clock.got_to(p[0], p[1])
            await asyncio.sleep(1)


async def __update_plot(ax: Axes, plot_clock: PlotClock, color: str = "b"):
    while True:
        t = ax.get_lines()
        while len(t) > 0:
            ax.lines.remove(t[-1])
            t = ax.get_lines()
        ax.axvline()
        ax.axvline(x=2)
        x, y = plot_clock.arms
        ax.plot(x, y, color=color)
        x, y = plot_clock.pen_trail
        ax.plot(x, y, color='r')
        plt.pause(.01)
        await asyncio.sleep(.01)


async def __main(loop):
    D = 2
    lower = 2
    upper = 2

    p = PlotClock(lower_arm_length=lower, upper_arm_length=upper, servo_distance=D, servo_speed=.01)
    start = 0
    end = D

    points = [
    ]
    for index, value in enumerate(range(22, 18, -1)):
        if index % 2 == 0:
            points.append([start, value/10.0])
            points.append([end, value/10.0])
            continue
        points.append([end, value/10.0])
        points.append([start, value/10.0])


    plt.style.use("dark_background")
    fig = plt.figure()
    ax0 = fig.add_subplot(1, 1, 1)
    ax0.set_title("PlotClock")
    ax0.axis("equal")

    await asyncio.gather(
        __update_plot(ax0, p),
        __got_to_indefinitely(p, points)
    )


if __name__ == '__main__':

    loop = asyncio.get_event_loop()

    try:
        loop.run_until_complete(__main(loop))
    except KeyboardInterrupt:
        pass
    finally:
        pass
