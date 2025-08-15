import pytest


class DummyGame:
    def __init__(self, level=1):
        self.level = level
        self.score = 0
        self.combo_count = 0
        self.last_clear_type = None


def simulate_clear(game, lines, t_spin=False, perfect_clear=False):
    level = game.level
    base_score = 0
    spin_bonus = 0
    back_to_back_bonus = 0
    perfect_clear_bonus = 0
    combo_bonus = 0

    # 基础行消除得分
    if not t_spin:
        if lines == 1:
            base_score = 100 * level
        elif lines == 2:
            base_score = 300 * level
        elif lines == 3:
            base_score = 500 * level
        elif lines == 4:
            base_score = 800 * level

    # T-Spin奖励
    if t_spin:
        if lines == 0:
            spin_bonus = 400 * level
        elif lines == 1:
            spin_bonus = 800 * level
        elif lines == 2:
            spin_bonus = 1200 * level
        elif lines == 3:
            spin_bonus = 1600 * level

    # Back-to-Back奖励
    is_b2b = False
    if (t_spin and lines > 0) or lines == 4:
        if game.last_clear_type in ["t-spin", "back-to-back", "tetris"]:
            is_b2b = True
            back_to_back_bonus = int((base_score + spin_bonus) * 0.5)

    # 完美清除奖励
    if perfect_clear:
        if lines == 1:
            perfect_clear_bonus = 800 * level
        elif lines == 2:
            perfect_clear_bonus = 1200 * level
        elif lines == 3:
            perfect_clear_bonus = 1800 * level
        elif lines == 4:
            perfect_clear_bonus = 2000 * level

    # Combo奖励
    if lines > 0:
        combo_bonus = 50 * game.combo_count * level
        game.combo_count += 1
    else:
        game.combo_count = 0

    total_score = base_score + spin_bonus + back_to_back_bonus + perfect_clear_bonus + combo_bonus
    game.score += total_score

    # 更新last_clear_type
    if t_spin and lines > 0:
        if is_b2b:
            game.last_clear_type = "back-to-back"
        else:
            game.last_clear_type = "t-spin"
    elif lines == 4:
        if is_b2b:
            game.last_clear_type = "back-to-back"
        else:
            game.last_clear_type = "tetris"
    elif lines > 0:
        game.last_clear_type = "normal"

    return total_score


def test_single_double_triple_tetris():
    game = DummyGame()
    assert simulate_clear(game, 1) == 100
    assert simulate_clear(game, 2) == 350  # 300 + 50(combo)
    assert simulate_clear(game, 3) == 600  # 500 + 100(combo)
    assert simulate_clear(game, 4) == 950  # 800 + 150(combo)
    assert game.score == 100 + 350 + 600 + 950


def test_combo_reset():
    game = DummyGame()
    simulate_clear(game, 1)  # combo=0
    simulate_clear(game, 1)  # combo=1
    simulate_clear(game, 1)  # combo=2
    simulate_clear(game, 0)  # combo断
    assert game.combo_count == 0
    assert game.score == 100 + 150 + 200 + 0


def test_t_spin_single_double_triple():
    game = DummyGame()
    assert simulate_clear(game, 1, t_spin=True) == 800
    assert simulate_clear(game, 2, t_spin=True) == 1850  # 1200+600(B2B)+50(combo)
    assert simulate_clear(game, 3, t_spin=True) == 2500  # 1600+800(B2B)+100(combo)
    assert simulate_clear(game, 0, t_spin=True) == 400
    assert game.score == 800 + 1850 + 2500 + 400


def test_t_spin_no_clear():
    game = DummyGame()
    assert simulate_clear(game, 0, t_spin=True) == 400
    assert game.score == 400


def test_b2b_tetris():
    game = DummyGame()
    assert simulate_clear(game, 4) == 800
    assert simulate_clear(game, 4) == 1250  # 800+400(B2B)+50(combo)
    assert simulate_clear(game, 4) == 1300  # 800+400(B2B)+100(combo)
    assert game.score == 800 + 1250 + 1300


def test_perfect_clear():
    game = DummyGame()
    assert simulate_clear(game, 4, perfect_clear=True) == 2800  # 800+2000
    assert simulate_clear(game, 1, perfect_clear=True) == 950  # 100+800+50(combo)
    assert game.score == 2800 + 950


def test_combo_with_t_spin_and_tetris():
    game = DummyGame()
    assert simulate_clear(game, 1) == 100
    assert simulate_clear(game, 4) == 850  # 800+50(combo)
    assert simulate_clear(game, 1, t_spin=True) == 1300  # 800+400(B2B)+100(combo)
    assert simulate_clear(game, 2, t_spin=True) == 1950  # 1200+600(B2B)+150(combo)
    assert game.score == 100 + 850 + 1300 + 1950


def test_combo_reset_after_no_clear():
    game = DummyGame()
    simulate_clear(game, 1)
    simulate_clear(game, 1)
    simulate_clear(game, 0)
    simulate_clear(game, 1)
    assert game.combo_count == 1
    assert game.score == 100 + 150 + 0 + 100


def test_b2b_chain():
    game = DummyGame()
    assert simulate_clear(game, 4) == 800
    assert simulate_clear(game, 4) == 1250
    assert simulate_clear(game, 1, t_spin=True) == 1300  # 800+400(B2B)+100(combo)
    assert simulate_clear(game, 4) == 1350  # 800+400(B2B)+150(combo)
    assert game.score == 800 + 1250 + 1300 + 1350


def test_combo_only():
    game = DummyGame()
    for i in range(1, 6):
        simulate_clear(game, 1)
    assert game.combo_count == 5
    # 100 + 150 + 200 + 250 + 300 = 1000
    assert game.score == 100 + 150 + 200 + 250 + 300


def test_t_spin_and_perfect_clear():
    game = DummyGame()
    assert simulate_clear(game, 2, t_spin=True, perfect_clear=True) == 2400  # 1200+1200
    assert game.score == 2400


def test_t_spin_b2b_chain_with_combo():
    game = DummyGame()
    assert simulate_clear(game, 1, t_spin=True) == 800
    assert simulate_clear(game, 2, t_spin=True) == 1850
    assert simulate_clear(game, 2, t_spin=True) == 1900  # 1200+600(B2B)+100(combo)
    assert game.score == 800 + 1850 + 1900


def test_no_clear():
    game = DummyGame()
    assert simulate_clear(game, 0) == 0
    assert game.score == 0
    assert game.combo_count == 0
