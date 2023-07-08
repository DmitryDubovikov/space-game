import time
import curses


def draw(canvas):
    canvas.refresh()
    height, width = canvas.getmaxyx()
    row, column = (5, 20)
    canvas.addstr(row, column, "Hello, World!")
    canvas.border()
    canvas.refresh()
    curses.curs_set(False)

    frames = [
        "*",  # 1 кадр
        "*",  # 2 кадр
        "*",  # 3 кадр
        "*",  # 4 кадр
    ]
    attributes = [
        curses.A_DIM,  # Атрибут для тусклой звезды
        curses.A_NORMAL,  # Обычная звезда
        curses.A_BOLD,  # Атрибут для яркой звезды
        curses.A_NORMAL,  # Обычная звезда
    ]

    while True:
        for frame, attribute in zip(frames, attributes):
            canvas.clear()
            canvas.addstr(5, 5, frame, attribute)
            canvas.refresh()
            time.sleep(1)


if __name__ == "__main__":
    curses.update_lines_cols()
    curses.wrapper(draw)
