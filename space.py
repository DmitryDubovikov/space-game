import time
import asyncio
import curses
import random
from itertools import cycle
from curses_tools import draw_frame


async def blink(canvas, row, column, symbol="*"):
    delays = [20, 3, 5, 3]

    while True:
        # случайное смещение
        for _ in range(random.randint(0, 8)):
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

    for frame in cycle(frames):
        draw_frame(canvas, start_row, start_column, frame)
        for _ in range(random.randint(0, 3)):
            await asyncio.sleep(0)
        draw_frame(canvas, start_row, start_column, frame, True)


def draw(canvas):
    TIC_TIMEOUT = 0.1
    canvas.border()
    canvas.refresh()
    curses.curs_set(False)

    max_y, max_x = canvas.getmaxyx()
    number_of_stars = 100

    spaceship_frames = []
    with open("rocket_frame_1.txt", "r") as f:
        spaceship_frames.append(f.read())

    with open("rocket_frame_2.txt", "r") as f:
        spaceship_frames.append(f.read())

    coroutines = [
        blink(
            canvas,
            random.randint(1, max_y - 2),
            random.randint(1, max_x - 2),
            random.choice("+*.:"),
        )
        for _ in range(number_of_stars)
    ]

    coroutines.append(fire(canvas, max_y // 2, max_x // 2))
    coroutines.append(fly(canvas, max_y // 2, max_x // 2 - 2, spaceship_frames))

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


if __name__ == "__main__":
    curses.update_lines_cols()
    curses.wrapper(draw)
