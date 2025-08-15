import unittest

from tetris.tetris import Board, TetrisGame, Tetromino


class TestScoreComboB2B(unittest.TestCase):
    def setUp(self):
        self.game = TetrisGame(None)
        self.game.level = 1  # 固定等级
        self.game.board = Board(24, 10)
        self.game.combo_count = 0
        self.game.last_clear_type = None

    def simulate_clear(self, lines, t_spin=False, perfect_clear=False):
        level = self.game.level
        combo_bonus = 0
        back_to_back_bonus = 0
        perfect_clear_bonus = 0

        # 1. 基础分数
        if t_spin:
            if lines == 0:
                base_score = 400 * level
            elif lines == 1:
                base_score = 800 * level
            elif lines == 2:
                base_score = 1200 * level
            elif lines == 3:
                base_score = 1600 * level
            else:
                base_score = 0
        else:
            if lines == 1:
                base_score = 100 * level
            elif lines == 2:
                base_score = 300 * level
            elif lines == 3:
                base_score = 500 * level
            elif lines == 4:
                base_score = 800 * level
            else:
                base_score = 0

        # 2. combo分数
        if lines > 0:
            self.game.combo_count += 1
            combo_bonus = 50 * (self.game.combo_count - 1) * level
        else:
            self.game.combo_count = 0

        # 3. B2B分数
        is_b2b = False
        if (t_spin and lines > 0) or lines == 4:
            if self.game.last_clear_type in ["t-spin", "back-to-back", "tetris"]:
                is_b2b = True
                back_to_back_bonus = int(base_score * 0.5)

        # 4. 完美消除
        if perfect_clear:
            if lines == 1:
                perfect_clear_bonus = 800 * level
            elif lines == 2:
                perfect_clear_bonus = 1200 * level
            elif lines == 3:
                perfect_clear_bonus = 1800 * level
            elif lines == 4:
                perfect_clear_bonus = 2000 * level

        total_score = base_score + back_to_back_bonus + perfect_clear_bonus + combo_bonus
        self.game.score += total_score

        # 更新last_clear_type
        if t_spin and lines > 0:
            if is_b2b:
                self.game.last_clear_type = "back-to-back"
            else:
                self.game.last_clear_type = "t-spin"
        elif lines == 4:
            if is_b2b:
                self.game.last_clear_type = "back-to-back"
            else:
                self.game.last_clear_type = "tetris"
        elif lines > 0:
            self.game.last_clear_type = "normal"

    def test_single_double_triple_tetris(self):
        self.game.score = 0
        # combo=0
        self.simulate_clear(1)  # 100
        # combo=1
        self.simulate_clear(2)  # 300+50=350
        # combo=2
        self.simulate_clear(3)  # 500+100=600
        # combo=3
        self.simulate_clear(4)  # 800+150=950
        self.assertEqual(self.game.score, 100 + 350 + 600 + 950)  # 2000

    def test_combo(self):
        self.game.score = 0
        self.simulate_clear(1)  # combo=0, 100
        self.simulate_clear(1)  # combo=1, 100+50=150
        self.simulate_clear(1)  # combo=2, 100+100=200
        self.assertEqual(self.game.score, 100 + 150 + 200)  # 450
        self.simulate_clear(0)  # combo断
        self.assertEqual(self.game.combo_count, 0)

    def test_b2b_tetris(self):
        self.game.score = 0
        # combo=0
        self.simulate_clear(4)  # 800
        # combo=1, B2B
        self.simulate_clear(4)  # 800+400+50=1250
        # combo=2, B2B
        self.simulate_clear(4)  # 800+400+100=1300
        self.assertEqual(self.game.score, 800 + 1250 + 1300)  # 3350
        # 非Tetris，B2B断开
        self.simulate_clear(1)  # combo=3, 100+150=250
        self.assertEqual(self.game.last_clear_type, "normal")
        # combo=4
        self.simulate_clear(4)  # 800+200=1000
        self.assertEqual(self.game.score, 800 + 1250 + 1300 + 250 + 1000)  # 4600

    def test_t_spin_single_double_triple(self):
        self.game.score = 0
        self.simulate_clear(1, t_spin=True)  # combo=0, 800
        self.simulate_clear(2, t_spin=True)  # combo=1, 1200+600+50=1850
        self.simulate_clear(3, t_spin=True)  # combo=2, 1600+800+100=2500
        self.simulate_clear(0, t_spin=True)  # combo断, 400
        self.assertEqual(self.game.score, 800 + 1850 + 2500 + 400)  # 5550

    def test_b2b_t_spin(self):
        self.game.score = 0
        self.simulate_clear(2, t_spin=True)  # combo=0, 1200
        self.simulate_clear(2, t_spin=True)  # combo=1, 1200+600+50=1850
        self.assertEqual(self.game.score, 1200 + 1850)  # 3050
        self.simulate_clear(1)  # combo=2, 100+100=200
        self.assertEqual(self.game.last_clear_type, "normal")
        self.simulate_clear(2, t_spin=True)  # combo=3, 1200+150=1350
        self.assertEqual(self.game.score, 1200 + 1850 + 200 + 1350)  # 4600

    def test_perfect_clear(self):
        self.game.score = 0
        # combo=0
        self.simulate_clear(1, perfect_clear=True)  # 100+800=900
        # combo=1
        self.simulate_clear(2, perfect_clear=True)  # 300+1200+50=1550
        self.assertEqual(self.game.score, 900 + 1550)  # 2450
        # combo=2
        self.simulate_clear(3, perfect_clear=True)  # 500+1800+100=2400
        self.assertEqual(self.game.score, 900 + 1550 + 2400)  # 4850
        # combo=3
        self.simulate_clear(4, perfect_clear=True)  # 800+2000+150=2950
        self.assertEqual(self.game.score, 900 + 1550 + 2400 + 2950)  # 7800

    def test_combo_and_b2b(self):
        self.game.score = 0
        # combo=0
        self.simulate_clear(4)  # 800
        # combo=1, B2B
        self.simulate_clear(4)  # 800+400+50=1250
        # combo=2, B2B
        self.simulate_clear(4)  # 800+400+100=1300
        self.assertEqual(self.game.score, 800 + 1250 + 1300)  # 3350

    def test_combo_reset(self):
        self.game.combo_count = 2
        self.simulate_clear(0)
        self.assertEqual(self.game.combo_count, 0)

    def test_b2b_reset(self):
        self.simulate_clear(4)
        self.simulate_clear(1)
        self.assertNotIn(self.game.last_clear_type, ["t-spin", "back-to-back", "tetris"])


if __name__ == "__main__":
    unittest.main()
