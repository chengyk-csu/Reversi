import unittest

from config import (
    BOARD_SIZE,
    EMPTY,
    BLACK,
    WHITE,
)
from core.board import Board
from ai.evaluation import (
    piece_difference,
    positional_score,
    mobility_score,
    corner_score,
    get_game_phase,
    evaluate_fixed,
    evaluate_dynamic,
    evaluate,
)


class TestEvaluation(unittest.TestCase):

    def setUp(self):

        self.board = Board()

    def test_initial_piece_difference(self):
        """测试初始棋子差。"""

        self.assertEqual(
            piece_difference(
                self.board,
                BLACK,
            ),
            0
        )

        self.assertEqual(
            piece_difference(
                self.board,
                WHITE,
            ),
            0
        )

    def test_piece_difference_after_move(self):
        """测试落子后的棋子差。"""

        self.board.make_move(
            2,
            3,
            BLACK,
        )

        self.assertEqual(
            piece_difference(
                self.board,
                BLACK,
            ),
            3
        )

        self.assertEqual(
            piece_difference(
                self.board,
                WHITE,
            ),
            -3
        )

    def test_initial_mobility(self):
        """测试初始机动性差。"""

        self.assertEqual(
            mobility_score(
                self.board,
                BLACK,
            ),
            0
        )

        self.assertEqual(
            mobility_score(
                self.board,
                WHITE,
            ),
            0
        )

    def test_corner_score(self):
        """测试角点评价。"""

        self.board.grid[0][0] = (
            BLACK
        )

        self.assertEqual(
            corner_score(
                self.board,
                BLACK,
            ),
            1
        )

        self.assertEqual(
            corner_score(
                self.board,
                WHITE,
            ),
            -1
        )

    def test_fixed_evaluation_symmetry(self):
        """测试固定评价函数黑白视角对称。"""

        self.board.make_move(
            2,
            3,
            BLACK,
        )

        black_score = (
            evaluate_fixed(
                self.board,
                BLACK,
            )
        )

        white_score = (
            evaluate_fixed(
                self.board,
                WHITE,
            )
        )

        self.assertEqual(
            black_score,
            -white_score
        )

    def test_dynamic_evaluation_symmetry(self):
        """测试动态评价函数黑白视角对称。"""

        self.board.make_move(
            2,
            3,
            BLACK,
        )

        black_score = (
            evaluate_dynamic(
                self.board,
                BLACK,
            )
        )

        white_score = (
            evaluate_dynamic(
                self.board,
                WHITE,
            )
        )

        self.assertEqual(
            black_score,
            -white_score
        )

    def test_default_evaluation_is_fixed(self):
        """测试默认 evaluate 仍使用固定评价。"""

        self.board.make_move(
            2,
            3,
            BLACK,
        )

        self.assertEqual(
            evaluate(
                self.board,
                BLACK,
            ),
            evaluate_fixed(
                self.board,
                BLACK,
            )
        )

    def test_opening_phase(self):
        """测试开局阶段判断。"""

        self.assertEqual(
            get_game_phase(
                self.board
            ),
            "opening"
        )

    def test_midgame_phase(self):
        """测试中局阶段判断。"""

        self.board.grid = [
            [
                EMPTY
                for _ in range(
                    BOARD_SIZE
                )
            ]
            for _ in range(
                BOARD_SIZE
            )
        ]

        # 放置 30 个棋子
        count = 0

        for row in range(
            BOARD_SIZE
        ):

            for col in range(
                BOARD_SIZE
            ):

                if count >= 30:
                    break

                if count % 2 == 0:
                    piece = BLACK
                else:
                    piece = WHITE

                self.board.grid[row][col] = (
                    piece
                )

                count += 1

            if count >= 30:
                break

        self.assertEqual(
            get_game_phase(
                self.board
            ),
            "midgame"
        )

    def test_endgame_phase(self):
        """测试残局阶段判断。"""

        self.board.grid = [
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

        # 保留少量空格，
        # 确保棋子总数大于 50。
        for col in range(8):

            self.board.grid[0][col] = (
                EMPTY
            )

        self.assertEqual(
            get_game_phase(
                self.board
            ),
            "endgame"
        )

    def test_positional_score_symmetry(self):
        """测试位置评价黑白视角对称。"""

        self.board.grid[0][0] = (
            BLACK
        )

        black_score = (
            positional_score(
                self.board,
                BLACK,
            )
        )

        white_score = (
            positional_score(
                self.board,
                WHITE,
            )
        )

        self.assertEqual(
            black_score,
            -white_score
        )


if __name__ == "__main__":
    unittest.main()