import time
import asyncio
import curses
import random
from itertools import cycle
from curses_tools import draw_frame, read_controls, get_frame_size


TIC_TIMEOUT = 0.1


async def blink(canvas, row, column, offset_tics=0, symbol="*"):
    delays = [20, 3, 5, 3]

    while True:
        # случайное смещение
        for _ in range(offset_tics):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_DIM)
        for _ in range(delays[0]):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for _ in range(delays[1]):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        for _ in range(delays[2]):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for _ in range(delays[3]):
            await asyncio.sleep(0)


async def fire(canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0):
    """Display animation of gun shot, direction and speed can be specified."""

    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), "*")
    await asyncio.sleep(0)

    canvas.addstr(round(row), round(column), "O")
    await asyncio.sleep(0)
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
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), " ")
        row += rows_speed
        column += columns_speed


async def fly(canvas, start_row, start_column, frames):
    """Display animation of spaceship"""

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 1, columns - 1

    duplicated_frames = [item for item in frames for _ in range(2)]

    for frame in cycle(duplicated_frames):
        rows_direction, columns_direction, space_pressed = read_controls(canvas)
        size_y, size_x = get_frame_size(frame)

        if (
            rows_direction == 1
            and (start_row + size_y < max_row)
            or rows_direction == -1
            and (start_row - 1 > 0)
        ):
            start_row += rows_direction

        if (
            columns_direction == 1
            and (start_column + size_x < max_column)
            or columns_direction == -1
            and (start_column - 1 > 0)
        ):
            start_column += columns_direction

        draw_frame(canvas, start_row, start_column, frame)
        await asyncio.sleep(0)
        draw_frame(canvas, start_row, start_column, frame, True)


def draw(canvas):
    canvas.border()
    canvas.refresh()
    canvas.nodelay(True)
    curses.curs_set(False)

    rows, columns = canvas.getmaxyx()
    max_y, max_x = rows - 1, columns - 1
    border_width = 1
    number_of_stars = 100

    spaceship_frames = []
    with open("rocket_frame_1.txt", "r") as f:
        spaceship_frames.append(f.read())

    with open("rocket_frame_2.txt", "r") as f:
        spaceship_frames.append(f.read())

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
    coroutines.append(fly(canvas, y, x - 2, spaceship_frames))

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
