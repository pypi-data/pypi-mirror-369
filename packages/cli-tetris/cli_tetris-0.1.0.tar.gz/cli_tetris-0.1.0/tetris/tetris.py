import curses
import random
import time

from tetris.const import *


class Tetromino:
    """
    方块类，支持SRS旋转和类型判断优化
    """

    # 预生成所有类型的所有旋转形状
    _all_rotations = []
    _type_map = {}

    @staticmethod
    def _precompute_rotations():
        """
        预生成所有方块的4种旋转形状，并建立类型索引映射
        """
        Tetromino._all_rotations = []
        Tetromino._type_map = {}
        for idx, shape in enumerate(TETROMINOS):
            rots = [shape]
            s = shape
            for _ in range(3):
                s = Tetromino.rotate_clockwise_static(s)
                rots.append(s)
            Tetromino._all_rotations.append(rots)
            for rot_idx, rot_shape in enumerate(rots):
                # 用tuple(tuple)做hash，便于快速比对
                Tetromino._type_map[Tetromino._shape_hash(rot_shape)] = (idx, rot_idx)

    @staticmethod
    def _shape_hash(shape):
        return tuple(tuple(row) for row in shape)

    @staticmethod
    def rotate_clockwise_static(shape):
        """
        顺时针旋转二维数组
        """
        return [list(row) for row in zip(*shape[::-1])]

    @staticmethod
    def rotate_counterclockwise_static(shape):
        """
        逆时针旋转二维数组
        """
        return [list(row) for row in zip(*shape)][::-1]

    def __init__(self, type_idx, y, x, rotation=0):
        """
        :param type_idx: 方块类型索引
        :param y: 初始y坐标
        :param x: 初始x坐标
        :param rotation: 初始旋转状态
        """
        self.type_idx = type_idx
        self.y = y
        self.x = x
        self.rotation = rotation % 4
        self.color = TETROMINO_COLORS[type_idx]

    @property
    def shape(self):
        """
        当前旋转状态下的形状
        """
        return Tetromino._all_rotations[self.type_idx][self.rotation]

    def get_coords(self, y=None, x=None, rotation=None):
        """
        获取方块所有格子的坐标
        :param y: y坐标（可选，默认当前y）
        :param x: x坐标（可选，默认当前x）
        :param rotation: 旋转状态（可选，默认当前旋转）
        :return: 坐标列表
        """
        if y is None:
            y = self.y
        if x is None:
            x = self.x
        if rotation is None:
            rotation = self.rotation
        shape = Tetromino._all_rotations[self.type_idx][rotation]
        coords = []
        for dy, row in enumerate(shape):
            for dx, cell in enumerate(row):
                if cell:
                    coords.append((y + dy, x + dx))
        return coords

    def rotate(self, clockwise=True):
        """
        旋转方块（顺时针或逆时针）
        """
        self.rotation = (self.rotation + (1 if clockwise else -1)) % 4

    def get_rotated(self, clockwise=True):
        """
        获取旋转后的形状
        :param clockwise: 是否顺时针
        :return: 旋转后的二维数组
        """
        new_rot = (self.rotation + (1 if clockwise else -1)) % 4
        return Tetromino._all_rotations[self.type_idx][new_rot]

    def width(self):
        """
        :return: 方块宽度
        """
        return len(self.shape[0])

    def height(self):
        """
        :return: 方块高度
        """
        return len(self.shape)

    def is_I(self):
        """
        是否为I型方块
        :return: bool
        """
        return self.type_idx == 0

    def is_T(self):
        """
        是否为T型方块
        :return: bool
        """
        return self.type_idx == 2


# 初始化旋转表（只需一次）
Tetromino._precompute_rotations()


class SevenBag:
    """
    7-bag 随机系统
    """

    def __init__(self):
        self.bag = []

    def next(self):
        """
        获取下一个方块类型索引
        :return: int
        """
        if not self.bag:
            self.bag = list(range(len(TETROMINOS)))
            random.shuffle(self.bag)
        return self.bag.pop()


class Board:
    """
    游戏棋盘
    """

    def __init__(self, height, width):
        """
        :param height: 棋盘高度（含隐藏区）
        :param width: 棋盘宽度
        """
        self.height = height
        self.width = width
        # 存储颜色编号，0为无色，1~7为方块色
        self.grid = [[0 for _ in range(width)] for _ in range(height)]

    def check_collision(self, tetromino, y=None, x=None, rotation=None):
        """
        检查方块是否碰撞
        :param tetromino: 方块对象
        :param y: y坐标
        :param x: x坐标
        :param rotation: 旋转状态
        :return: 是否碰撞
        """
        for by, bx in tetromino.get_coords(y, x, rotation):
            if by < 0 or by >= self.height or bx < 0 or bx >= self.width or self.grid[by][bx]:
                return True
        return False

    def fix_tetromino(self, tetromino):
        """
        固定方块到棋盘
        :param tetromino: 方块对象
        """
        for y, x in tetromino.get_coords():
            if 0 <= y < self.height and 0 <= x < self.width:
                self.grid[y][x] = tetromino.color

    def remove_full_lines(self):
        """
        消除满行
        :return: 消除的行数
        """
        new_grid = [row for row in self.grid if any(cell == 0 for cell in row)]
        lines_cleared = self.height - len(new_grid)
        while len(new_grid) < self.height:
            new_grid.insert(0, [0 for _ in range(self.width)])
        self.grid = new_grid
        return lines_cleared

    def is_perfect_clear(self):
        """
        检查是否完美清除（整个棋盘为空）
        :return: bool
        """
        return all(cell == 0 for row in self.grid for cell in row)

    def draw(self, stdscr, offset_y=0, offset_x=0):
        """
        绘制棋盘（只显示底部20行）
        :param stdscr: curses窗口
        :param offset_y: y偏移
        :param offset_x: x偏移
        """
        stdscr.attron(curses.color_pair(COLOR_BORDER))
        stdscr.addstr(offset_y, offset_x, BORDER_TOP_LEFT + BORDER_HORIZONTAL * (self.width * 2 - 1) + BORDER_TOP_RIGHT)
        stdscr.attroff(curses.color_pair(COLOR_BORDER))
        for y in range(HIDDEN_ROWS, self.height):
            stdscr.attron(curses.color_pair(COLOR_BORDER))
            stdscr.addstr(offset_y + 1 + (y - HIDDEN_ROWS), offset_x, BORDER_VERTICAL)
            stdscr.attroff(curses.color_pair(COLOR_BORDER))
            for x in range(self.width):
                color = self.grid[y][x]
                if color:
                    stdscr.attron(curses.color_pair(color))
                    stdscr.addstr(offset_y + 1 + (y - HIDDEN_ROWS), offset_x + 1 + x * 2, SHAPE_CHAR)
                    stdscr.attroff(curses.color_pair(color))
                else:
                    stdscr.addstr(offset_y + 1 + (y - HIDDEN_ROWS), offset_x + 1 + x * 2, EMPTY_CHAR)
            stdscr.attron(curses.color_pair(COLOR_BORDER))
            stdscr.addstr(offset_y + 1 + (y - HIDDEN_ROWS), offset_x + 1 + (self.width * 2 - 1), BORDER_VERTICAL)
            stdscr.attroff(curses.color_pair(COLOR_BORDER))
        stdscr.attron(curses.color_pair(COLOR_BORDER))
        stdscr.addstr(
            offset_y + 1 + (self.height - HIDDEN_ROWS),
            offset_x,
            BORDER_BOTTOM_LEFT + BORDER_HORIZONTAL * (self.width * 2 - 1) + BORDER_BOTTOM_RIGHT,
        )
        stdscr.attroff(curses.color_pair(COLOR_BORDER))

    def draw_tetromino(self, stdscr, tetromino, char, offset_y=0, offset_x=0, ghost=False):
        """
        绘制活动方块或影子方块
        :param stdscr: curses窗口
        :param tetromino: 方块对象
        :param char: 显示字符
        :param offset_y: y偏移
        :param offset_x: x偏移
        :param ghost: 是否为影子方块
        """
        color = tetromino.color
        for y, x in tetromino.get_coords():
            if HIDDEN_ROWS <= y < self.height and 0 <= x < self.width:
                stdscr.attron(curses.color_pair(color))
                if ghost:
                    stdscr.attron(curses.A_DIM)
                stdscr.addstr(offset_y + 1 + (y - HIDDEN_ROWS), offset_x + 1 + x * 2, char)
                if ghost:
                    stdscr.attroff(curses.A_DIM)
                stdscr.attroff(curses.color_pair(color))

    def get_ghost_y(self, tetromino):
        """
        获取影子方块的y坐标
        :param tetromino: 方块对象
        :return: y坐标
        """
        ghost_y = tetromino.y
        while not self.check_collision(tetromino, y=ghost_y + 1, x=tetromino.x):
            ghost_y += 1
        return ghost_y

    def check_t_spin(self, tetromino):
        """
        检查是否为T-Spin
        :param tetromino: T型方块对象
        :return: 是否为T-Spin
        """
        if not tetromino.is_T():
            return False
        center_y = tetromino.y + len(tetromino.shape) // 2
        center_x = tetromino.x + len(tetromino.shape[0]) // 2
        corners = [
            (center_y - 1, center_x - 1),
            (center_y - 1, center_x + 1),
            (center_y + 1, center_x - 1),
            (center_y + 1, center_x + 1),
        ]
        occupied_corners = 0
        for y, x in corners:
            if y < 0 or y >= self.height or x < 0 or x >= self.width:
                occupied_corners += 1
            elif self.grid[y][x]:
                occupied_corners += 1
        return occupied_corners >= 3


class TetrisGame:
    """
    俄罗斯方块游戏主类
    """

    @staticmethod
    def init_colors():
        """
        初始化curses颜色对
        """
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(COLOR_I, curses.COLOR_CYAN, -1)
        curses.init_pair(COLOR_O, curses.COLOR_YELLOW, -1)
        curses.init_pair(COLOR_T, curses.COLOR_MAGENTA, -1)
        curses.init_pair(COLOR_J, curses.COLOR_BLUE, -1)
        curses.init_pair(COLOR_L, curses.COLOR_WHITE, -1)
        curses.init_pair(COLOR_S, curses.COLOR_GREEN, -1)
        curses.init_pair(COLOR_Z, curses.COLOR_RED, -1)
        curses.init_pair(COLOR_GHOST, curses.COLOR_WHITE, -1)
        curses.init_pair(COLOR_BORDER, curses.COLOR_WHITE, -1)
        curses.init_pair(COLOR_TEXT, curses.COLOR_WHITE, -1)
        curses.init_pair(COLOR_HIGHLIGHT, curses.COLOR_YELLOW, curses.COLOR_BLUE)

    def __init__(self, stdscr, config=None):
        """
        :param stdscr: curses窗口
        :param config: 配置字典
        """
        self.stdscr = stdscr
        self.config = config or {}
        self.frame_time = 1.0 / self.config.get("game_fps", GAME_FPS)
        self.board = Board(BOARD_HEIGHT + HIDDEN_ROWS, BOARD_WIDTH)
        self.score = 0
        self.level = self.config.get("level", LEVEL_INIT)
        self.level_thresholds = self._precompute_level_thresholds()
        self.seven_bag = SevenBag()
        self.current = self._new_tetromino()
        self.next_count = self.config.get("next_count", NEXT_COUNT)
        self.next_list = [self._new_tetromino() for _ in range(self.next_count)]
        self.hold = None
        self.hold_used = False
        self.last_drop = time.time()
        self.game_over = False
        self.last_clear_type = None
        self.combo_count = 0
        self.current_rotated = False

    def _precompute_level_thresholds(self):
        """
        预计算所有等级升级所需的分数门槛
        """
        thresholds = [0]
        for level in range(2, LEVEL_MAX + 2):
            exponent = level - 2
            threshold = LEVEL_UP_BASE * (LEVEL_UP_FACTOR**exponent)
            thresholds.append(round(threshold))
        return thresholds

    def _new_tetromino(self):
        """
        生成新方块（7-bag 随机）
        :return: Tetromino对象
        """
        type_idx = self.seven_bag.next()
        return Tetromino(type_idx, 0, 3, rotation=0)

    def wall_kick(self, tetromino, clockwise=True):
        """
        SRS墙踢/地踢（完整版）
        :param tetromino: 方块对象
        :param clockwise: 是否顺时针旋转
        :return: (new_y, new_x, new_rotation) 或 (None, None, None)
        """
        from_rot = tetromino.rotation
        to_rot = (from_rot + (1 if clockwise else -1)) % 4
        is_I = tetromino.is_I()
        kicks = SRS_KICKS_I if is_I else SRS_KICKS
        key = (from_rot, to_rot)
        if key not in kicks:
            return None, None, None
        for dx, dy in kicks[key]:
            new_x = tetromino.x + dx
            new_y = tetromino.y + dy
            if not self.board.check_collision(tetromino, y=new_y, x=new_x, rotation=to_rot):
                return new_y, new_x, to_rot
        return None, None, None

    def get_drop_time(self):
        """
        根据当前等级获取下落时间间隔（指数衰减，平滑递减）
        """
        drop_time = DROP_TIME_BASE * (DROP_TIME_DECAY ** (self.level - 1))
        return max(drop_time, DROP_TIME_MIN)

    def try_level_up(self):
        """
        检查升级，支持跨级升级
        基于指数增长的门槛分数系统
        """
        if self.level >= LEVEL_MAX:
            return
        new_level = self.level
        for level in range(self.level + 1, LEVEL_MAX + 1):
            if self.score >= self.level_thresholds[level]:
                new_level = level
            else:
                break
        if new_level > self.level:
            self.level = new_level

    def draw(self):
        """
        绘制游戏界面（局中居中显示，Hold区在分数/等级下方，Next区上方，适配任意next_count）
        """
        self.stdscr.clear()
        max_y, max_x = self.stdscr.getmaxyx()
        board_width_px = self.board.width * 2 + 1  # 棋盘宽度（含边框）
        board_height_px = BOARD_HEIGHT + 2  # 只显示底部20行
        # 计算居中偏移
        offset_y = (max_y - board_height_px) // 2
        offset_x = (max_x - board_width_px) // 2

        # 绘制棋盘
        self.board.draw(self.stdscr, offset_y, offset_x)
        # 影子
        ghost_y = self.board.get_ghost_y(self.current)
        if ghost_y != self.current.y:
            ghost = Tetromino(self.current.type_idx, ghost_y, self.current.x, self.current.rotation)
            self.board.draw_tetromino(self.stdscr, ghost, GHOST_CHAR, offset_y, offset_x, ghost=True)
        # 当前方块
        self.board.draw_tetromino(self.stdscr, self.current, SHAPE_CHAR, offset_y, offset_x)

        # 分数、等级和Hold、Next，显示在棋盘右侧
        info_x = offset_x + board_width_px + 4
        info_y = offset_y

        # 分数和等级
        self.stdscr.attron(curses.color_pair(COLOR_TEXT))
        self.stdscr.addstr(info_y, info_x, f"Score: {self.score}")
        self.stdscr.addstr(info_y + 1, info_x, f"Level: {self.level}")
        self.stdscr.addstr(info_y + 2, info_x, f"Combo: {self.combo_count}")
        self.stdscr.attroff(curses.color_pair(COLOR_TEXT))

        # Hold区
        hold_y = info_y + 4
        self.stdscr.attron(curses.color_pair(COLOR_BORDER))
        self.stdscr.addstr(hold_y, info_x, "Hold:")
        self.stdscr.attroff(curses.color_pair(COLOR_BORDER))
        hold_content_y = hold_y + 1
        if self.hold:
            for y, row in enumerate(self.hold.shape):
                for x, cell in enumerate(row):
                    if cell:
                        self.stdscr.attron(curses.color_pair(self.hold.color))
                        self.stdscr.addstr(hold_content_y + y, info_x + x * 2, SHAPE_CHAR)
                        self.stdscr.attroff(curses.color_pair(self.hold.color))
            hold_height = len(self.hold.shape)
        else:
            hold_height = 4

        # Next区
        next_y = hold_content_y + hold_height + 1
        self.stdscr.attron(curses.color_pair(COLOR_BORDER))
        self.stdscr.addstr(next_y, info_x, f"Next {self.next_count}:")
        self.stdscr.attroff(curses.color_pair(COLOR_BORDER))
        next_content_y = next_y + 1
        for idx, tetro in enumerate(self.next_list):
            for y, row in enumerate(tetro.shape):
                for x, cell in enumerate(row):
                    if cell:
                        self.stdscr.attron(curses.color_pair(tetro.color))
                        self.stdscr.addstr(next_content_y + y, info_x + x * 2, SHAPE_CHAR)
                        self.stdscr.attroff(curses.color_pair(tetro.color))
            next_content_y += len(tetro.shape) + 1

        # 显示当前状态（T-Spin, Back-to-Back等）
        status_y = next_content_y + 2
        if self.last_clear_type == "t-spin":
            self.stdscr.attron(curses.color_pair(COLOR_HIGHLIGHT))
            self.stdscr.addstr(status_y, info_x, "T-Spin!")
            self.stdscr.attroff(curses.color_pair(COLOR_HIGHLIGHT))
        elif self.last_clear_type == "back-to-back":
            self.stdscr.attron(curses.color_pair(COLOR_HIGHLIGHT))
            self.stdscr.addstr(status_y, info_x, "Back-to-Back!")
            self.stdscr.attroff(curses.color_pair(COLOR_HIGHLIGHT))

        self.stdscr.refresh()

    def pause_and_help(self):
        """
        暂停游戏并显示帮助信息，按ESC或空格恢复
        """
        self.stdscr.clear()
        max_y, max_x = self.stdscr.getmaxyx()
        help_lines = [
            "游戏已暂停",
            "",
            "操作说明：",
            "  ←/→           左右移动",
            "  ↑/x           顺时针旋转",
            "  z             逆时针旋转",
            "  ↓             快速下落",
            "  空格          硬降到底",
            "  C             Hold/切换方块",
            "  ESC           暂停并显示本帮助",
            "",
            "特殊玩法：",
            "  T-Spin        旋转T型方块到角落",
            "  Back-to-Back  连续T-Spin或消四",
            "  Combo         连续消除行",
            "  Perfect Clear 清空整个棋盘",
            "",
            "按 ESC 或 空格 继续游戏",
        ]
        max_line_len = max(len(line) for line in help_lines)
        block_x = max_x // 2 - max_line_len // 2
        block_y = max_y // 2 - len(help_lines) // 2
        for i, line in enumerate(help_lines):
            if i == 0 or line.startswith("按 ESC") or line.startswith("游戏已暂停"):
                self.stdscr.attron(curses.color_pair(COLOR_HIGHLIGHT))
                self.stdscr.addstr(block_y + i, block_x, line)
                self.stdscr.attroff(curses.color_pair(COLOR_HIGHLIGHT))
            else:
                self.stdscr.attron(curses.color_pair(COLOR_TEXT))
                self.stdscr.addstr(block_y + i, block_x, line)
                self.stdscr.attroff(curses.color_pair(COLOR_TEXT))
        self.stdscr.refresh()
        while True:
            key = self.stdscr.getch()
            if key in (27, ord(" ")):
                break

    def run(self):
        """
        游戏主循环
        """
        self.init_colors()
        curses.curs_set(0)
        self.stdscr.nodelay(1)
        while True:
            self.draw()
            if self.game_over:
                max_y, max_x = self.stdscr.getmaxyx()
                game_over_y = max_y // 2
                game_over_x = max_x // 2 - 5
                self.stdscr.attron(curses.color_pair(COLOR_HIGHLIGHT))
                self.stdscr.addstr(game_over_y, game_over_x, "游戏结束!")
                self.stdscr.addstr(game_over_y + 1, game_over_x - 5, "按 q 退出, r 重新开始")
                self.stdscr.attroff(curses.color_pair(COLOR_HIGHLIGHT))
                self.stdscr.refresh()
                while True:
                    key = self.stdscr.getch()
                    if key == ord("q"):
                        return
                    elif key == ord("r"):
                        self.__init__(self.stdscr, self.config)
                        break
                    time.sleep(0.1)
                continue

            key = self.stdscr.getch()
            force_fix = False
            # 控制
            if key == ord("q"):
                break
            elif key == curses.KEY_LEFT:
                if not self.board.check_collision(self.current, y=self.current.y, x=self.current.x - 1):
                    self.current.x -= 1
            elif key == curses.KEY_RIGHT:
                if not self.board.check_collision(self.current, y=self.current.y, x=self.current.x + 1):
                    self.current.x += 1
            elif key == curses.KEY_DOWN:
                # 下方向键：只加速下落，不触发固定
                if not self.board.check_collision(self.current, y=self.current.y + 1, x=self.current.x):
                    self.current.y += 1
            elif key == curses.KEY_UP or key == ord("x"):  # 顺时针旋转
                new_y, new_x, new_rot = self.wall_kick(self.current, clockwise=True)
                if new_y is not None:
                    self.current.y = new_y
                    self.current.x = new_x
                    self.current.rotation = new_rot
                    self.current_rotated = True
            elif key == ord("z"):  # 逆时针旋转
                new_y, new_x, new_rot = self.wall_kick(self.current, clockwise=False)
                if new_y is not None:
                    self.current.y = new_y
                    self.current.x = new_x
                    self.current.rotation = new_rot
                    self.current_rotated = True
            elif key == ord(" "):
                # 空格：硬降到底并立即固定
                while not self.board.check_collision(self.current, y=self.current.y + 1, x=self.current.x):
                    self.current.y += 1
                force_fix = True
            elif key == ord("c"):
                # Hold功能
                if not self.hold_used:
                    if self.hold is None:
                        self.hold = Tetromino(self.current.type_idx, 0, 3, rotation=0)
                        self.current = self.next_list.pop(0)
                        self.next_list.append(self._new_tetromino())
                    else:
                        self.current, self.hold = Tetromino(self.hold.type_idx, 0, 3, rotation=0), Tetromino(
                            self.current.type_idx, 0, 3, rotation=0
                        )
                    self.hold_used = True
                    self.current_rotated = False
            elif key == 27:  # ESC
                self.pause_and_help()

            drop_time = self.get_drop_time()
            if time.time() - self.last_drop > drop_time or force_fix:
                if (
                    not self.board.check_collision(self.current, y=self.current.y + 1, x=self.current.x)
                    and not force_fix
                ):
                    self.current.y += 1
                    self.last_drop = time.time()
                else:
                    if force_fix:
                        fixed = True
                    else:
                        touch_time = time.time()
                        fixed = False
                        while not fixed:
                            self.draw()
                            wait_key = self.stdscr.getch()
                            if wait_key == ord("q"):
                                return
                            elif wait_key == curses.KEY_LEFT:
                                if not self.board.check_collision(self.current, y=self.current.y, x=self.current.x - 1):
                                    self.current.x -= 1
                                    # touch_time = time.time()
                            elif wait_key == curses.KEY_RIGHT:
                                if not self.board.check_collision(self.current, y=self.current.y, x=self.current.x + 1):
                                    self.current.x += 1
                                    # touch_time = time.time()
                            elif wait_key == curses.KEY_UP or wait_key == ord("x"):
                                new_y, new_x, new_rot = self.wall_kick(self.current, clockwise=True)
                                if new_y is not None:
                                    self.current.y = new_y
                                    self.current.x = new_x
                                    self.current.rotation = new_rot
                                    self.current_rotated = True
                                    # touch_time = time.time()
                            elif wait_key == ord("z"):
                                new_y, new_x, new_rot = self.wall_kick(self.current, clockwise=False)
                                if new_y is not None:
                                    self.current.y = new_y
                                    self.current.x = new_x
                                    self.current.rotation = new_rot
                                    self.current_rotated = True
                                    # touch_time = time.time()
                            elif wait_key == ord(" "):
                                while not self.board.check_collision(
                                    self.current, y=self.current.y + 1, x=self.current.x
                                ):
                                    self.current.y += 1
                                fixed = True
                                break
                            if not self.board.check_collision(self.current, y=self.current.y + 1, x=self.current.x):
                                self.current.y += 1
                                break
                            if time.time() - touch_time > LOCK_DELAY:
                                fixed = True
                                break
                            time.sleep(self.frame_time)
                    if fixed:
                        # 检查是否为T-Spin（只有T型且最后一次有旋转才判定）
                        is_t_spin = False
                        if self.current.is_T() and self.current_rotated:
                            is_t_spin = self.board.check_t_spin(self.current)

                        # 固定方块到棋盘
                        self.board.fix_tetromino(self.current)

                        # 消除行
                        lines = self.board.remove_full_lines()

                        # 检查是否为完美清除
                        is_perfect_clear = self.board.is_perfect_clear()

                        # 计算得分
                        base_score = 0
                        spin_bonus = 0
                        back_to_back_bonus = 0
                        perfect_clear_bonus = 0
                        combo_bonus = 0

                        # 基础行消除得分
                        if lines == 1:
                            base_score = 100 * self.level
                        elif lines == 2:
                            base_score = 300 * self.level
                        elif lines == 3:
                            base_score = 500 * self.level
                        elif lines == 4:
                            base_score = 800 * self.level

                        # T-Spin奖励
                        if is_t_spin:
                            if lines == 0:
                                spin_bonus = 400 * self.level  # T-Spin无消除
                            elif lines == 1:
                                spin_bonus = 800 * self.level  # T-Spin Single
                            elif lines == 2:
                                spin_bonus = 1200 * self.level  # T-Spin Double
                            elif lines == 3:
                                spin_bonus = 1600 * self.level  # T-Spin Triple

                        # Back-to-Back奖励（连续T-Spin消除或Tetris）
                        is_b2b = False
                        if (is_t_spin and lines > 0) or lines == 4:
                            if self.last_clear_type in ["t-spin", "back-to-back", "tetris"]:
                                is_b2b = True
                                back_to_back_bonus = int((base_score + spin_bonus) * 0.5)  # 50%额外奖励

                        # 完美清除奖励
                        if is_perfect_clear:
                            if lines == 1:
                                perfect_clear_bonus = 800 * self.level
                            elif lines == 2:
                                perfect_clear_bonus = 1200 * self.level
                            elif lines == 3:
                                perfect_clear_bonus = 1800 * self.level
                            elif lines == 4:
                                perfect_clear_bonus = 2000 * self.level

                        # 连击奖励（combo）：连续多次消除行
                        if lines > 0:
                            combo_bonus = 50 * self.combo_count * self.level
                            self.combo_count += 1
                        else:
                            self.combo_count = 0

                        # 总得分
                        total_score = base_score + spin_bonus + back_to_back_bonus + perfect_clear_bonus + combo_bonus
                        self.score += total_score

                        # 更新消除类型状态
                        if is_t_spin and lines > 0:
                            if is_b2b:
                                self.last_clear_type = "back-to-back"
                            else:
                                self.last_clear_type = "t-spin"
                        elif lines == 4:
                            if is_b2b:
                                self.last_clear_type = "back-to-back"
                            else:
                                self.last_clear_type = "tetris"
                        elif lines > 0:
                            self.last_clear_type = "normal"
                        else:
                            pass

                        # 升级检查
                        self.try_level_up()

                        # 生成新方块
                        self.current = self.next_list.pop(0)
                        self.next_list.append(self._new_tetromino())
                        self.hold_used = False
                        self.current_rotated = False

                        # 顶部4行有方块则Game Over
                        if self.board.check_collision(self.current):
                            self.game_over = True
                        self.last_drop = time.time()
                        continue
                self.last_drop = time.time()
            time.sleep(self.frame_time)
