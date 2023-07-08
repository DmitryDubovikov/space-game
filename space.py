import time
import asyncio
import curses


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
    canvas.refresh()
    row, column = (5, 20)
    canvas.addstr(row, column, "Hello, World!")
    canvas.border()
    canvas.refresh()
    curses.curs_set(False)

    delays = [2, 0.3, 0.5, 0.3]  # Задержка в миллисекундах между кадрами
    j = 0

    coroutines = [blink(canvas, 3, i * 2) for i in range(1, 6)]

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
