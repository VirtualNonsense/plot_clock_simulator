import asyncio
from typing import *
import numpy as np

import matplotlib.pyplot as plt
from matplotlib.axes import Axes as Axes
from matplotlib.ticker import FormatStrFormatter

from plot_clock import PlotClock


def generate_horizontal_parallel_test_lines(point_list: list,
                                            left: float,
                                            right: float,
                                            up: float,
                                            down: float,
                                            lines: int):
    values = np.linspace(up, down, lines)

    for index, value in enumerate(values):
        if index % 2 == 0:
            point_list.append([left, value])
            point_list.append([right, value])
            continue
        point_list.append([right, value])
        point_list.append([left, value])


async def __got_to_indefinitely(plot_clock: PlotClock, points: List[List[float]]):
    while True:
        for p in points:
            await plot_clock.got_to(p[0], p[1])
            await asyncio.sleep(1)


def delete_lines_in_axes(ax: Axes):
    t = ax.get_lines()
    while len(t) > 0:
        ax.lines.remove(t[-1])
        t = ax.get_lines()


async def __update_plot(xy_ax: Axes,
                        angle_ax: Axes,
                        plot_clock: PlotClock,
                        clock_color: str = "b",
                        pen_trail_color: str = "r",
                        target_marker_color: str = "m"):
    while True:
        delete_lines_in_axes(xy_ax)
        delete_lines_in_axes(angle_ax)
        xy_ax.axvline()
        xy_ax.axvline(x=2)
        x, y = plot_clock.pen_trail
        xy_ax.plot(x, y, color=pen_trail_color, label="pen trail")

        x, y = plot_clock.target_trail
        xy_ax.plot(x, y, color=target_marker_color, linestyle=" ", marker="+", label="target points")

        x, y = plot_clock.arms
        xy_ax.plot(x, y, color=clock_color, label="plotclock")
        x, y = plot_clock.angle_trail
        angle_ax.plot(x, y, color=pen_trail_color)

        plt.pause(.01)
        await asyncio.sleep(.01)


async def __main(loop):
    D = 2
    lower = 2
    upper = 2

    p = PlotClock(lower_arm_length=lower, upper_arm_length=upper, servo_distance=D, servo_speed=.05)

    points = [
    ]

    generate_horizontal_parallel_test_lines(points, -1, D+1, 2.5, 1.8, 20)
    # generate_vertical_parallel_test_lines(points,)
    plt.style.use("dark_background")
    fig = plt.figure()
    ax0: Axes = fig.add_subplot(1, 2, 1)
    ax0.set_title("plot view")
    ax0.set_xlabel("X")
    ax0.set_ylabel("Y")
    ax0.axis("equal")

    ax1: Axes = fig.add_subplot(1, 2, 2)
    ax1.set_title("angles")
    ax1.set_xlabel("left angle")
    ax1.set_ylabel("right angle")
    ax1.xaxis.set_major_formatter(FormatStrFormatter('%g $\pi$'))
    ax1.yaxis.set_major_formatter(FormatStrFormatter('%g $\pi$'))
    ax1.axis("equal")

    await asyncio.gather(
        __update_plot(ax0, ax1, p),
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
