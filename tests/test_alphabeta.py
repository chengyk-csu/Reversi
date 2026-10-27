import unittest

from config import BLACK, WHITE
from core.board import Board
from ai.minimax import MinimaxAI
from ai.alphabeta import AlphaBetaAI


class TestAlphaBeta(unittest.TestCase):

    def setUp(self):
        self.board = Board()

    def test_choose_legal_move(self):
        """测试 Alpha-Beta 返回合法落子。"""

        ai = AlphaBetaAI(
            depth=3
        )

        move = ai.choose_move(
            self.board,
            BLACK
        )

        self.assertIn(
            move,
            self.board.get_valid_moves(
                BLACK
            )
        )

    def test_search_does_not_modify_board(self):
        """测试搜索不会修改真实棋盘。"""

        ai = AlphaBetaAI(
            depth=3
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
        """测试无合法落子时返回 None。"""

        self.board.grid = [
            [BLACK for _ in range(8)]
            for _ in range(8)
        ]

        ai = AlphaBetaAI(
            depth=3
        )

        move = ai.choose_move(
            self.board,
            WHITE
        )

        self.assertIsNone(
            move
        )

    def test_same_move_as_minimax(self):
        """测试与 Minimax 决策一致。"""

        minimax = MinimaxAI(
            depth=4
        )

        alphabeta = AlphaBetaAI(
            depth=4
        )

        minimax_move = minimax.choose_move(
            self.board,
            BLACK
        )

        alphabeta_move = alphabeta.choose_move(
            self.board,
            BLACK
        )

        self.assertEqual(
            alphabeta_move,
            minimax_move
        )

    def test_pruning_reduces_nodes(self):
        """测试剪枝减少搜索节点。"""

        minimax = MinimaxAI(
            depth=4
        )

        alphabeta = AlphaBetaAI(
            depth=4
        )

        minimax.choose_move(
            self.board,
            BLACK
        )

        alphabeta.choose_move(
            self.board,
            BLACK
        )

        self.assertLess(
            alphabeta.nodes_searched,
            minimax.nodes_searched
        )

    def test_choose_winning_endgame_move(self):
        """测试残局中选择获胜动作。"""

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

        ai = AlphaBetaAI(
            depth=3
        )

        move = ai.choose_move(
            self.board,
            BLACK
        )

        self.assertEqual(
            move,
            (0, 0)
        )

    def test_invalid_depth(self):
        """测试非法搜索深度。"""

        with self.assertRaises(
            ValueError
        ):
            AlphaBetaAI(
                depth=0
            )


if __name__ == "__main__":
    unittest.main()