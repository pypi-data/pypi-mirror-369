# tetris/cli.py
import curses

import typer

from tetris.const import *
from tetris.tetris import TetrisGame

app = typer.Typer(help="俄罗斯方块命令行游戏")


@app.callback(invoke_without_command=True)
def main(
    game_fps: float = typer.Option(GAME_FPS, "-f", "--game-fps", help="游戏帧率"),
    board_height: int = typer.Option(BOARD_HEIGHT, "-h", "--height", help="棋盘高度"),
    board_width: int = typer.Option(BOARD_WIDTH, "-w", "--width", help="棋盘宽度"),
    drop_time_base: float = typer.Option(DROP_TIME_BASE, "--drop-time-base", help="初始下落间隔（秒）"),
    drop_time_min: float = typer.Option(DROP_TIME_MIN, "--drop-time-min", help="最快下落间隔（秒）"),
    level_max: int = typer.Option(LEVEL_MAX, "-m", "--level-max", help="最高难度等级"),
    level: int = typer.Option(LEVEL_INIT, "-l", "--level", help="初始等级"),
    next_count: int = typer.Option(NEXT_COUNT, "-n", "--next-count", help="预告方块数量"),
):
    """
    直接运行 tetris 即可启动游戏。
    """
    config = {
        "game_fps": game_fps,
        "board_height": board_height,
        "board_width": board_width,
        "drop_time_base": drop_time_base,
        "drop_time_min": drop_time_min,
        "level_max": level_max,
        "level": level,
        "next_count": next_count,
    }

    def _main(stdscr):
        game = TetrisGame(stdscr, config)
        game.run()

    curses.wrapper(_main)


def run():
    app()
