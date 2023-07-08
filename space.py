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

    # coro = blink(canvas, 3, 3)

    coroutines = [blink(canvas, 3, i * 2) for i in range(1, 6)]

    while True:
        canvas.refresh()
        time.sleep(1)
        for coroutine in coroutines.copy():
            try:
                coroutine.send(None)

            except StopIteration:
                coroutines.remove(coroutine)
        if len(coroutines) == 0:
            break

    # frames = [
    #     "*",  # 1 кадр
    #     "*",  # 2 кадр
    #     "*",  # 3 кадр
    #     "*",  # 4 кадр
    # ]
    # attributes = [
    #     curses.A_DIM,  # Атрибут для тусклой звезды
    #     curses.A_NORMAL,  # Обычная звезда
    #     curses.A_BOLD,  # Атрибут для яркой звезды
    #     curses.A_NORMAL,  # Обычная звезда
    # ]

    # while True:
    #     for frame, attribute in zip(frames, attributes):
    #         canvas.clear()
    #         canvas.addstr(5, 5, frame, attribute)
    #         canvas.refresh()
    #         time.sleep(1)


if __name__ == "__main__":
    curses.update_lines_cols()
    curses.wrapper(draw)
