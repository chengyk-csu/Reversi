import unittest

from config import BOARD_SIZE, EMPTY, BLACK, WHITE, DIRECTIONS
from core.board import Board


class TestBoard(unittest.TestCase):

    def setUp(self):
        self.board = Board()

    def test_initial_board(self):
        """测试初始棋盘是否正确。"""

        black_count, white_count = (
            self.board.count_pieces()
        )

        self.assertEqual(black_count, 2)
        self.assertEqual(white_count, 2)

        self.assertEqual(
            self.board.grid[3][3],
            WHITE
        )

        self.assertEqual(
            self.board.grid[3][4],
            BLACK
        )

        self.assertEqual(
            self.board.grid[4][3],
            BLACK
        )

        self.assertEqual(
            self.board.grid[4][4],
            WHITE
        )

    def test_initial_valid_moves(self):
        """测试初始合法落子。"""

        black_moves = set(
            self.board.get_valid_moves(BLACK)
        )

        white_moves = set(
            self.board.get_valid_moves(WHITE)
        )

        expected_black_moves = {
            (2, 3),
            (3, 2),
            (4, 5),
            (5, 4),
        }

        expected_white_moves = {
            (2, 4),
            (3, 5),
            (4, 2),
            (5, 3),
        }

        self.assertEqual(
            black_moves,
            expected_black_moves
        )

        self.assertEqual(
            white_moves,
            expected_white_moves
        )

    def test_invalid_move(self):
        """测试非法落子。"""

        self.assertFalse(
            self.board.make_move(
                0,
                0,
                BLACK
            )
        )

        self.assertFalse(
            self.board.make_move(
                3,
                3,
                BLACK
            )
        )

    def test_make_move(self):
        """测试一次正常落子与翻转。"""

        result = self.board.make_move(
            2,
            3,
            BLACK
        )

        self.assertTrue(result)

        self.assertEqual(
            self.board.grid[2][3],
            BLACK
        )

        self.assertEqual(
            self.board.grid[3][3],
            BLACK
        )

        black_count, white_count = (
            self.board.count_pieces()
        )

        self.assertEqual(
            (black_count, white_count),
            (4, 1)
        )

    def test_multiple_direction_flips(self):
        """测试一次落子同时翻转八个方向。"""

        self.board.grid = [
            [EMPTY for _ in range(BOARD_SIZE)]
            for _ in range(BOARD_SIZE)
        ]

        center_row = 3
        center_col = 3

        for dr, dc in DIRECTIONS:

            white_row = center_row + dr
            white_col = center_col + dc

            black_row = center_row + 2 * dr
            black_col = center_col + 2 * dc

            self.board.grid[
                white_row
            ][
                white_col
            ] = WHITE

            self.board.grid[
                black_row
            ][
                black_col
            ] = BLACK

        flips = self.board.get_flips(
            center_row,
            center_col,
            BLACK
        )

        self.assertEqual(
            len(flips),
            8
        )

        result = self.board.make_move(
            center_row,
            center_col,
            BLACK
        )

        self.assertTrue(result)

        for dr, dc in DIRECTIONS:

            row = center_row + dr
            col = center_col + dc

            self.assertEqual(
                self.board.grid[row][col],
                BLACK
            )

    def test_board_copy(self):
        """测试副本是否独立。"""

        copied_board = self.board.copy()

        copied_board.make_move(
            2,
            3,
            BLACK
        )

        self.assertEqual(
            copied_board.grid[2][3],
            BLACK
        )

        self.assertEqual(
            self.board.grid[2][3],
            EMPTY
        )

        self.assertEqual(
            self.board.grid[3][3],
            WHITE
        )

    def test_piece_count(self):
        """测试棋子数量统计。"""

        black_count, white_count = (
            self.board.count_pieces()
        )

        self.assertEqual(
            (black_count, white_count),
            (2, 2)
        )

        self.board.make_move(
            2,
            3,
            BLACK
        )

        black_count, white_count = (
            self.board.count_pieces()
        )

        self.assertEqual(
            (black_count, white_count),
            (4, 1)
        )

    def test_game_over(self):
        """测试棋局结束判断。"""

        self.assertFalse(
            self.board.is_game_over()
        )

        self.board.grid = [
            [BLACK for _ in range(BOARD_SIZE)]
            for _ in range(BOARD_SIZE)
        ]

        self.assertTrue(
            self.board.is_game_over()
        )


if __name__ == "__main__":
    unittest.main()