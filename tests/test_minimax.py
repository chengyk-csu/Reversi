import unittest

from config import BLACK, WHITE
from core.board import Board
from ai.minimax import MinimaxAI


class TestMinimax(unittest.TestCase):

    def setUp(self):
        self.board = Board()

    def test_choose_legal_move(self):
        """测试 Minimax 返回合法落子。"""

        ai = MinimaxAI(
            depth=2
        )

        move = ai.choose_move(
            self.board,
            BLACK
        )

        valid_moves = (
            self.board.get_valid_moves(
                BLACK
            )
        )

        self.assertIn(
            move,
            valid_moves
        )

    def test_search_does_not_modify_board(self):
        """测试搜索不会修改原棋盘。"""

        ai = MinimaxAI(
            depth=2
        )

        original_grid = [
            row[:]
            for row in self.board.grid
        ]

        ai.choose_move(
            self.board,
            BLACK
        )

        self.assertEqual(
            self.board.grid,
            original_grid
        )

    def test_no_valid_move_returns_none(self):
        """测试没有合法棋时返回 None。"""

        ai = MinimaxAI(
            depth=2
        )

        self.board.grid = [
            [BLACK for _ in range(8)]
            for _ in range(8)
        ]

        move = ai.choose_move(
            self.board,
            WHITE
        )

        self.assertIsNone(
            move
        )

    def test_search_statistics(self):
        """测试搜索统计。"""

        ai = MinimaxAI(
            depth=2
        )

        ai.choose_move(
            self.board,
            BLACK
        )

        self.assertGreater(
            ai.nodes_searched,
            0
        )

        self.assertGreaterEqual(
            ai.move_time,
            0
        )

    def test_deeper_search_visits_more_nodes(self):
        """测试更深搜索访问更多节点。"""

        shallow_ai = MinimaxAI(
            depth=1
        )

        deep_ai = MinimaxAI(
            depth=3
        )

        shallow_ai.choose_move(
            self.board,
            BLACK
        )

        deep_ai.choose_move(
            self.board,
            BLACK
        )

        self.assertGreater(
            deep_ai.nodes_searched,
            shallow_ai.nodes_searched
        )

    def test_invalid_depth(self):
        """测试非法搜索深度。"""

        with self.assertRaises(
            ValueError
        ):
            MinimaxAI(
                depth=0
            )

    def test_choose_winning_endgame_move(self):
        """测试残局中选择最终获胜动作。"""

        self.board.grid = [
            [0,  1, -1, -1, -1, -1, -1,  1],
            [1, -1, -1, -1, -1,  1,  1,  1],
            [1, -1, -1, -1,  1, -1, -1, -1],
            [1, -1,  1, -1, -1, -1, -1, -1],
            [1,  1,  1,  1,  1, -1, -1, -1],
            [1,  1, -1,  1, -1,  1, -1, -1],
            [1, -1,  1,  1,  1,  1, -1,  0],
            [-1, -1, -1, -1, -1, -1,  1,  1],
        ]

        ai = MinimaxAI(
            depth=3
        )

        valid_moves = set(
            self.board.get_valid_moves(
                BLACK
            )
        )

        self.assertEqual(
            valid_moves,
            {
                (0, 0),
                (6, 7),
            }
        )

        move = ai.choose_move(
            self.board,
            BLACK
        )

        self.assertEqual(
            move,
            (0, 0)
        )


if __name__ == "__main__":
    unittest.main()