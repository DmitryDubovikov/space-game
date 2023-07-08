import time
import asyncio
import curses
import random


async def blink(canvas, row, column, symbol="*"):
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        await asyncio.sleep(0)


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

    delays = [2, 0.3, 0.5, 0.3]
    j = 0

    while True:
        for coroutine in coroutines.copy():
            try:
                coroutine.send(None)

            except StopIteration:
                coroutines.remove(coroutine)
        if len(coroutines) == 0:
            break
        canvas.refresh()
        time.sleep(delays[j])
        j = (j + 1) % 4


if __name__ == "__main__":
    curses.update_lines_cols()
    curses.wrapper(draw)
