import time
import asyncio
import curses
import random
import os
from itertools import cycle
from curses_tools import draw_frame, read_controls, get_frame_size
from physics import update_speed
from obstacles import Obstacle, has_collision
from explosion import explode


TIC_TIMEOUT = 0.2


def read_frames():
    frames = dict()

    read_animation_frames(frames, "./animation/spaceship", "spaceship_frames")
    read_animation_frames(frames, "./animation/garbage", "garbage_frames")

    return frames


def read_animation_frames(frames, folder_path, animation_name):
    animation_list = []
    for filename in os.listdir(folder_path):
        filepath = os.path.join(folder_path, filename)
        if not os.path.isfile(filepath):
            continue
        with open(filepath, "r") as f:
            animation_list.append(f.read())
    frames[animation_name] = animation_list


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
    global obstacles, obstacles_in_last_collisions

    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), "*")
    await sleep()

    canvas.addstr(round(row), round(column), "O")
    await sleep()
    canvas.addstr(round(row), round(column), " ")

    row += rows_speed
    column += columns_speed

    symbol = "-" if columns_speed else "|"

    # ширина и высота всегда будут на единицу больше, чем координаты крайней ячейки,
    # т.к. нумерация начинается с нуля.
    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 1, columns - 1

    curses.beep()

    while 0 < row < max_row and 0 < column < max_column:
        canvas.addstr(round(row), round(column), symbol)
        await sleep()
        canvas.addstr(round(row), round(column), " ")
        row += rows_speed
        column += columns_speed

        for obstacle in obstacles:
            if has_collision(
                (obstacle.row, obstacle.column),
                (obstacle.rows_size, obstacle.columns_size),
                (row, column),
            ):
                obstacles_in_last_collisions.append(obstacle)
                await explode(canvas, row, column)
                return


def show_text(canvas, row, column, frame):
    draw_frame(canvas, row, column, frame)


async def explode_spaceship(canvas, row, column):
    with open("./animation/game_over.txt", "r") as f:
        game_over_text = f.read()
        game_over_size_y, game_over_size_x = get_frame_size(game_over_text)

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 1, columns - 1

    await explode(canvas, row, column)
    show_text(
        canvas,
        max_row // 2 - game_over_size_y // 2,
        max_column // 2 - game_over_size_x // 2,
        game_over_text,
    )


async def fly(canvas, row, column, frames):
    """Display animation of spaceship"""

    global coroutines, obstacles_in_last_collisions, year

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 1, columns - 1
    row_speed = column_speed = 0

    duplicated_frames = [item for item in frames for _ in range(2)]

    for frame in cycle(duplicated_frames):
        rows_direction, columns_direction, space_pressed = read_controls(canvas)
        size_y, size_x = get_frame_size(frame)

        for obstacle in obstacles:
            if has_collision(
                (obstacle.row, obstacle.column),
                (obstacle.rows_size, obstacle.columns_size),
                (row, column),
            ):
                obstacles_in_last_collisions.append(obstacle)
                await explode_spaceship(canvas, row, column)
                return

        if space_pressed and year >= 2020:
            coroutines.append(fire(canvas, row, column + size_x // 2))

        row_speed, column_speed = update_speed(
            row_speed, column_speed, rows_direction, 0
        )

        new_row = row + row_speed
        if 1 < new_row < max_row - size_y:
            row = new_row

        row_speed, column_speed = update_speed(
            row_speed, column_speed, 0, columns_direction
        )

        new_column = column + column_speed
        if 1 < new_column < max_column - size_x:
            column = new_column

        draw_frame(canvas, row, column, frame)
        await sleep(1)
        draw_frame(canvas, row, column, frame, True)


async def fly_garbage(canvas, column, garbage_frame, speed=0.5):
    """Animate garbage, flying from top to bottom. Сolumn position will stay same, as specified on start."""
    global obstacles, obstacles_in_last_collisions

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
        if obstacle in obstacles_in_last_collisions and obstacle in obstacles:
            obstacles.remove(obstacle)
            return


async def fill_orbit_with_garbage(canvas, max_x, garbage_frames):
    global coroutines, obstacles, year

    min_tics_for_new_garbage = 5
    tics = 15

    while True:
        column = random.randint(1, max_x)
        frame = random.choice(garbage_frames)

        coroutines.append(fly_garbage(canvas, column, frame))

        if tics < min_tics_for_new_garbage:
            tics -= year // 10 - 195

        await sleep(tics)


async def increase_year(canvas):
    global year

    while True:
        year += 1
        draw_frame(canvas, 1, 1, str(year))
        await sleep(2)


def draw(canvas):
    global coroutines, obstacles, obstacles_in_last_collisions, year

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
    obstacles_in_last_collisions = []
    year = 1957

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

    coroutines.append(fly(canvas, y, x - 2, frames["spaceship_frames"]))
    coroutines.append(fill_orbit_with_garbage(canvas, max_x, frames["garbage_frames"]))
    coroutines.append(increase_year(canvas))

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
