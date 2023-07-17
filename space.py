import time
import asyncio
import curses
import random
from itertools import cycle
from curses_tools import draw_frame, read_controls, get_frame_size
from physics import update_speed
from obstacles import Obstacle, show_obstacles


TIC_TIMEOUT = 0.2


def read_frames():
    frames = dict()

    spaceship_frames = []
    with open("rocket_frame_1.txt", "r") as f:
        spaceship_frames.append(f.read())
    with open("rocket_frame_2.txt", "r") as f:
        spaceship_frames.append(f.read())
    frames["spaceship_frames"] = spaceship_frames

    garbage_frames = []
    with open("trash_large.txt", "r") as f:
        garbage_frames.append(f.read())
    with open("trash_small.txt", "r") as f:
        garbage_frames.append(f.read())
    with open("trash_xl.txt", "r") as f:
        garbage_frames.append(f.read())
    frames["garbage_frames"] = garbage_frames

    return frames


async def sleep(tics=1):
    for _ in range(tics):
        await asyncio.sleep(0)


async def blink(canvas, row, column, offset_tics=0, symbol="*"):
    delays = [20, 3, 5, 3]

    while True:
        # случайное смещение
        await sleep(offset_tics)

        canvas.addstr(row, column, symbol, curses.A_DIM)
        await sleep(delays[0])

        canvas.addstr(row, column, symbol)
        await sleep(delays[1])

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await sleep(delays[2])

        canvas.addstr(row, column, symbol)
        await sleep(delays[3])


async def fire(canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0):
    """Display animation of gun shot, direction and speed can be specified."""

    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), "*")
    await sleep()

    canvas.addstr(round(row), round(column), "O")
    await sleep()
    canvas.addstr(round(row), round(column), " ")

    row += rows_speed
    column += columns_speed

    symbol = "-" if columns_speed else "|"

    # ширина и высота всегда будут на единицу больше, чем координаты крайней ячейки т.к. нумерация начинается с нуля.
    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 1, columns - 1

    curses.beep()

    while 0 < row < max_row and 0 < column < max_column:
        canvas.addstr(round(row), round(column), symbol)
        await sleep()
        canvas.addstr(round(row), round(column), " ")
        row += rows_speed
        column += columns_speed


async def fly(canvas, row, column, frames):
    """Display animation of spaceship"""

    global coroutines

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 1, columns - 1
    row_speed = column_speed = 0

    duplicated_frames = [item for item in frames for _ in range(2)]

    for frame in cycle(duplicated_frames):
        rows_direction, columns_direction, space_pressed = read_controls(canvas)
        size_y, size_x = get_frame_size(frame)

        if space_pressed:
            coroutines.append(fire(canvas, row, column + size_x // 2))

        if (
            rows_direction == 1
            and (row + size_y < max_row)
            or rows_direction == -1
            and (row - 1 > 0)
        ):
            row_speed, column_speed = update_speed(
                row_speed, column_speed, rows_direction, 0
            )
            row += row_speed

        if (
            columns_direction == 1
            and (column + size_x < max_column)
            or columns_direction == -1
            and (column - 1 > 0)
        ):
            row_speed, column_speed = update_speed(
                row_speed, column_speed, 0, columns_direction
            )

            column += column_speed

        draw_frame(canvas, row, column, frame)
        await sleep(1)
        draw_frame(canvas, row, column, frame, True)


async def fly_garbage(canvas, column, garbage_frame, speed=0.5):
    """Animate garbage, flying from top to bottom. Сolumn position will stay same, as specified on start."""
    global obstacles

    rows_number, columns_number = canvas.getmaxyx()

    column = max(column, 0)
    column = min(column, columns_number - 1)

    row = 1
    row_size, col_size = get_frame_size(garbage_frame)
    obstacle = Obstacle(1, column, row_size, col_size)
    obstacles.append(obstacle)

    while row < rows_number:
        draw_frame(canvas, row, column, garbage_frame)
        obstacle.row = row
        await sleep()
        draw_frame(canvas, row, column, garbage_frame, negative=True)
        row += speed


async def fill_orbit_with_garbage(canvas, max_x, garbage_frames):
    global coroutines, obstacles

    while True:
        column = random.randint(1, max_x)
        frame = random.choice(garbage_frames)

        coroutines.append(fly_garbage(canvas, column, frame))

        await sleep(20)


def draw(canvas):
    global coroutines, obstacles

    canvas.border()
    canvas.refresh()
    canvas.nodelay(True)
    curses.curs_set(False)

    rows, columns = canvas.getmaxyx()
    max_y, max_x = rows - 1, columns - 1
    border_width = 1
    number_of_stars = 90

    frames = read_frames()

    obstacles = []

    coroutines = [
        blink(
            canvas,
            random.randint(border_width, max_y - border_width),
            random.randint(border_width, max_x - border_width),
            random.randint(0, 8),
            random.choice("+*.:"),
        )
        for _ in range(number_of_stars)
    ]

    y, x = max_y // 2, max_x // 2

    coroutines.append(fire(canvas, y, x))
    coroutines.append(fly(canvas, y, x - 2, frames["spaceship_frames"]))
    coroutines.append(fill_orbit_with_garbage(canvas, max_x, frames["garbage_frames"]))
    coroutines.append(show_obstacles(canvas, obstacles))

    while True:
        for coroutine in coroutines.copy():
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)
        if len(coroutines) == 0:
            break
        canvas.refresh()
        time.sleep(TIC_TIMEOUT)


def main():
    curses.update_lines_cols()
    curses.wrapper(draw)


if __name__ == "__main__":
    main()
