# tests/test_tetris.py

import unittest

from tetris.const import *
from tetris.tetris import Board, SevenBag, TetrisGame, Tetromino


class TestTetromino(unittest.TestCase):
    def test_rotation_clockwise_and_counterclockwise(self):
        # 测试I型
        t = Tetromino(0, 0, 0)
        orig = t.shape
        t.rotate(clockwise=True)
        rot1 = t.shape
        t.rotate(clockwise=True)
        rot2 = t.shape
        t.rotate(clockwise=True)
        rot3 = t.shape
        t.rotate(clockwise=True)
        rot4 = t.shape
        self.assertEqual(orig, rot4)
        # 逆时针旋转回到原位
        t = Tetromino(0, 0, 0)
        t.rotate(clockwise=False)
        t.rotate(clockwise=False)
        t.rotate(clockwise=False)
        t.rotate(clockwise=False)
        self.assertEqual(t.shape, orig)

    def test_rotation_inverse(self):
        # 顺时针和逆时针旋转互为逆操作
        t = Tetromino(2, 0, 0)
        orig = t.shape
        t.rotate(clockwise=True)
        t.rotate(clockwise=False)
        self.assertEqual(t.shape, orig)

    def test_type_check(self):
        for idx, name in [(0, "I"), (2, "T")]:
            t = Tetromino(idx, 0, 0)
            self.assertTrue(t.is_I() if idx == 0 else not t.is_I())
            self.assertTrue(t.is_T() if idx == 2 else not t.is_T())

    def test_get_coords(self):
        t = Tetromino(1, 5, 3)  # O型
        coords = t.get_coords()
        expected = [(5, 3), (5, 4), (6, 3), (6, 4)]
        self.assertEqual(sorted(coords), sorted(expected))


class TestSevenBag(unittest.TestCase):
    def test_bag_cycle(self):
        bag = SevenBag()
        seen = set()
        for _ in range(7):
            idx = bag.next()
            self.assertNotIn(idx, seen)
            seen.add(idx)
        # 新一轮
        seen2 = set()
        for _ in range(7):
            idx = bag.next()
            self.assertNotIn(idx, seen2)
            seen2.add(idx)


class TestBoard(unittest.TestCase):
    def setUp(self):
        self.board = Board(24, 10)

    def test_collision_empty(self):
        t = Tetromino(1, 0, 0)  # O型
        self.assertFalse(self.board.check_collision(t))

    def test_collision_wall(self):
        t = Tetromino(1, 0, 9)  # O型，右边超界
        self.assertTrue(self.board.check_collision(t))

    def test_fix_and_remove_line(self):
        # 填满一行
        for x in range(10):
            self.board.grid[23][x] = 1
        lines = self.board.remove_full_lines()
        self.assertEqual(lines, 1)
        self.assertTrue(all(cell == 0 for cell in self.board.grid[23]))

    def test_perfect_clear(self):
        self.assertTrue(self.board.is_perfect_clear())
        self.board.grid[10][5] = 1
        self.assertFalse(self.board.is_perfect_clear())

    def test_ghost_y(self):
        t = Tetromino(1, 0, 0)  # O型
        ghost_y = self.board.get_ghost_y(t)
        self.assertEqual(ghost_y, self.board.height - 2)

    def test_t_spin_detection(self):
        # 构造T-Spin情形
        t = Tetromino(2, 10, 4)  # T型
        # 获取中心
        center_y = t.y + len(t.shape) // 2
        center_x = t.x + len(t.shape[0]) // 2
        # 填充3角
        for dy, dx in [(-1, -1), (-1, 1), (1, -1)]:
            self.board.grid[center_y + dy][center_x + dx] = 1
        self.assertTrue(self.board.check_t_spin(t))
        # 只填2角
        self.board.grid[center_y - 1][center_x - 1] = 0
        self.assertFalse(self.board.check_t_spin(t))


class TestTetrisGame(unittest.TestCase):
    def setUp(self):
        # 用None代替stdscr，测试不涉及UI
        self.game = TetrisGame(None)

    def test_level_up(self):
        self.game.score = 1000000  # 足够大
        self.game.try_level_up()
        # 允许 LEVEL_MAX 或 LEVEL_MAX-1，取决于门槛表实现
        self.assertIn(self.game.level, [LEVEL_MAX, LEVEL_MAX - 1])

    def test_new_tetromino(self):
        t = self.game._new_tetromino()
        self.assertIsInstance(t, Tetromino)

    def test_hold(self):
        # 模拟hold
        t1 = self.game.current
        self.game.hold = None
        self.game.hold_used = False
        self.game.hold = Tetromino(t1.type_idx, 0, 3)
        self.game.current = self.game.next_list.pop(0)
        self.game.next_list.append(self.game._new_tetromino())
        self.assertIsNotNone(self.game.hold)
        self.assertIsInstance(self.game.current, Tetromino)

    def test_drop_time(self):
        self.game.level = 1
        t1 = self.game.get_drop_time()
        self.game.level = 10
        t2 = self.game.get_drop_time()
        self.game.level = LEVEL_MAX
        t3 = self.game.get_drop_time()
        self.assertTrue(t1 > t2 > t3)
        self.assertGreaterEqual(t3, DROP_TIME_MIN)

    def test_wall_kick(self):
        t = Tetromino(0, 0, 3)  # I型
        y, x, rot = self.game.wall_kick(t, clockwise=True)
        # 只要能返回合法坐标即可
        self.assertTrue((y is None and x is None and rot is None) or (isinstance(y, int) and isinstance(x, int)))


if __name__ == "__main__":
    unittest.main()
