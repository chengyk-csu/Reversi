import unittest

from config import (
    BOARD_SIZE,
    EMPTY,
    BLACK,
    WHITE,
)
from core.game import Game


class TestGame(unittest.TestCase):

    def setUp(self):

        self.game = Game()

    def test_black_moves_first(self):
        """测试黑棋先手。"""

        self.assertEqual(
            self.game.current_player,
            BLACK
        )

    def test_switch_player_after_move(self):
        """测试正常落子后切换玩家。"""

        success = self.game.play_move(
            2,
            3
        )

        self.assertTrue(
            success
        )

        self.assertEqual(
            self.game.current_player,
            WHITE
        )

    def test_invalid_move_does_not_switch_player(self):
        """测试非法落子不会切换玩家。"""

        success = self.game.play_move(
            0,
            0
        )

        self.assertFalse(
            success
        )

        self.assertEqual(
            self.game.current_player,
            BLACK
        )

    def test_invalid_move_not_recorded(self):
        """测试非法落子不会加入历史记录。"""

        self.game.play_move(
            0,
            0
        )

        self.assertEqual(
            len(self.game.move_history),
            0
        )

    def test_move_history(self):
        """测试落子历史记录。"""

        self.game.play_move(
            2,
            3
        )

        self.assertEqual(
            len(self.game.move_history),
            1
        )

        record = (
            self.game.move_history[0]
        )

        self.assertEqual(
            record["player"],
            BLACK
        )

        self.assertEqual(
            record["move"],
            (2, 3)
        )

        self.assertEqual(
            record["flips"],
            1
        )

    def test_move_time_recording(self):
        """测试单步时间和累计时间。"""

        self.game.play_move(
            2,
            3,
            move_time=1.5,
        )

        self.assertAlmostEqual(
            self.game.black_time,
            1.5
        )

        self.assertAlmostEqual(
            self.game.white_time,
            0.0
        )

        self.assertAlmostEqual(
            self.game.move_history[0][
                "time"
            ],
            1.5
        )

    def test_pass_turn(self):
        """测试无合法动作时自动 Pass。"""

        self.game.board.grid = [
            [
                BLACK
                for _ in range(
                    BOARD_SIZE
                )
            ]
            for _ in range(
                BOARD_SIZE
            )
        ]

        # 第一行：
        #
        # B W . B W . B B
        #
        # 黑棋走 C1 后，
        # 白棋无合法动作，
        # 黑棋仍然可以走 F1。
        self.game.board.grid[0][1] = (
            WHITE
        )

        self.game.board.grid[0][2] = (
            EMPTY
        )

        self.game.board.grid[0][4] = (
            WHITE
        )

        self.game.board.grid[0][5] = (
            EMPTY
        )

        self.game.current_player = BLACK

        success = self.game.play_move(
            0,
            2
        )

        self.assertTrue(
            success
        )

        self.assertFalse(
            self.game.game_over
        )

        # 白棋被 Pass，
        # 下一步仍然黑棋
        self.assertEqual(
            self.game.current_player,
            BLACK
        )

        self.assertTrue(
            self.game.board.is_valid_move(
                0,
                5,
                BLACK,
            )
        )

    def test_game_over_after_last_move(self):
        """测试最后一步结束棋局。"""

        self.game.board.grid = [
            [
                BLACK
                for _ in range(
                    BOARD_SIZE
                )
            ]
            for _ in range(
                BOARD_SIZE
            )
        ]

        self.game.board.grid[0][1] = (
            WHITE
        )

        self.game.board.grid[0][2] = (
            EMPTY
        )

        self.game.current_player = BLACK

        self.game.play_move(
            0,
            2
        )

        self.assertTrue(
            self.game.game_over
        )

        self.assertEqual(
            self.game.end_reason,
            "normal"
        )

    def test_black_winner(self):
        """测试正常结束后黑棋获胜。"""

        self.game.board.grid = [
            [
                BLACK
                for _ in range(
                    BOARD_SIZE
                )
            ]
            for _ in range(
                BOARD_SIZE
            )
        ]

        self.game.game_over = True
        self.game.end_reason = "normal"

        self.assertEqual(
            self.game.get_winner(),
            BLACK
        )

    def test_draw(self):
        """测试平局。"""

        self.game.board.grid = [
            [
                (
                    BLACK
                    if (
                        row + col
                    ) % 2 == 0
                    else WHITE
                )
                for col in range(
                    BOARD_SIZE
                )
            ]
            for row in range(
                BOARD_SIZE
            )
        ]

        self.game.game_over = True
        self.game.end_reason = "normal"

        black_count, white_count = (
            self.game.board.count_pieces()
        )

        self.assertEqual(
            black_count,
            32
        )

        self.assertEqual(
            white_count,
            32
        )

        self.assertEqual(
            self.game.get_winner(),
            EMPTY
        )

    def test_no_winner_before_game_over(self):
        """测试游戏未结束时没有获胜者。"""

        self.assertIsNone(
            self.game.get_winner()
        )

    def test_black_timeout(self):
        """测试黑棋超时后白棋获胜。"""

        success = (
            self.game.declare_timeout(
                BLACK
            )
        )

        self.assertTrue(
            success
        )

        self.assertTrue(
            self.game.game_over
        )

        self.assertEqual(
            self.game.end_reason,
            "timeout"
        )

        self.assertEqual(
            self.game.timed_out_player,
            BLACK
        )

        self.assertEqual(
            self.game.get_winner(),
            WHITE
        )

    def test_white_timeout(self):
        """测试白棋超时后黑棋获胜。"""

        success = (
            self.game.declare_timeout(
                WHITE
            )
        )

        self.assertTrue(
            success
        )

        self.assertEqual(
            self.game.get_winner(),
            BLACK
        )

    def test_timeout_overrides_piece_count(self):
        """
        测试超时胜负优先于棋子数量。
        """

        self.game.board.grid = [
            [
                BLACK
                for _ in range(
                    BOARD_SIZE
                )
            ]
            for _ in range(
                BOARD_SIZE
            )
        ]

        # 即使黑棋拥有全部棋子，
        # 黑棋超时仍然判负。
        self.game.declare_timeout(
            BLACK
        )

        self.assertEqual(
            self.game.get_winner(),
            WHITE
        )

    def test_invalid_timeout_player(self):
        """测试非法超时玩家。"""

        with self.assertRaises(
            ValueError
        ):

            self.game.declare_timeout(
                EMPTY
            )

    def test_timeout_after_game_over(self):
        """测试结束后不能再次宣布超时。"""

        self.game.declare_timeout(
            BLACK
        )

        success = (
            self.game.declare_timeout(
                WHITE
            )
        )

        self.assertFalse(
            success
        )

        self.assertEqual(
            self.game.get_winner(),
            WHITE
        )

    def test_reset_clears_game_state(self):
        """测试 reset 清除结束状态和计时。"""

        self.game.play_move(
            2,
            3,
            move_time=2.0,
        )

        self.game.declare_timeout(
            WHITE
        )

        self.game.reset()

        self.assertFalse(
            self.game.game_over
        )

        self.assertEqual(
            self.game.current_player,
            BLACK
        )

        self.assertEqual(
            self.game.black_time,
            0.0
        )

        self.assertEqual(
            self.game.white_time,
            0.0
        )

        self.assertIsNone(
            self.game.end_reason
        )

        self.assertIsNone(
            self.game.timed_out_player
        )

        self.assertIsNone(
            self.game.forced_winner
        )

        self.assertEqual(
            len(self.game.move_history),
            0
        )


if __name__ == "__main__":
    unittest.main()