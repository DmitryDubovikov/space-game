import time
import asyncio
import curses
import random


async def blink(canvas, row, column, symbol="*"):
    delays = [20, 3, 5, 3]

    while True:
        # случайное смещение
        for _ in range(random.randint(0, 6)):
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


def draw(canvas):
    canvas.border()
    canvas.refresh()
    curses.curs_set(False)

    max_y, max_x = canvas.getmaxyx()
    number_of_stars = 100

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

    while True:
        for coroutine in coroutines.copy():
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)
        if len(coroutines) == 0:
            break
        canvas.refresh()
        time.sleep(0.1)


if __name__ == "__main__":
    curses.update_lines_cols()
    curses.wrapper(draw)
