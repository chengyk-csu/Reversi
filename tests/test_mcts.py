import unittest

from config import BOARD_SIZE, EMPTY, BLACK, WHITE
from core.board import Board
from ai.mcts import MCTSNode, MCTSAI


class TestMCTSNode(unittest.TestCase):

    def setUp(self):
        self.board = Board()

    def test_root_node_initialization(self):
        """测试根节点初始化。"""

        root = MCTSNode(
            board=self.board,
            player=BLACK,
        )

        self.assertEqual(
            root.player,
            BLACK
        )

        self.assertIsNone(
            root.parent
        )

        self.assertIsNone(
            root.move
        )

        self.assertEqual(
            len(root.children),
            0
        )

        self.assertEqual(
            root.visits,
            0
        )

        self.assertEqual(
            root.value,
            0.0
        )

        self.assertEqual(
            len(root.untried_moves),
            4
        )

    def test_expand(self):
        """测试节点扩展。"""

        root = MCTSNode(
            board=self.board,
            player=BLACK,
        )

        original_grid = [
            row[:]
            for row in self.board.grid
        ]

        child = root.expand()

        self.assertIsNotNone(
            child
        )

        self.assertEqual(
            child.parent,
            root
        )

        self.assertIn(
            child,
            root.children
        )

        self.assertEqual(
            len(root.children),
            1
        )

        self.assertEqual(
            len(root.untried_moves),
            3
        )

        self.assertEqual(
            child.player,
            WHITE
        )

        # 原棋盘不能被修改
        self.assertEqual(
            self.board.grid,
            original_grid
        )

        # 子棋盘应发生变化
        self.assertNotEqual(
            child.board.grid,
            original_grid
        )

    def test_fully_expand_node(self):
        """测试所有合法动作全部扩展。"""

        root = MCTSNode(
            board=self.board,
            player=BLACK,
        )

        while not root.is_fully_expanded():
            root.expand()

        self.assertEqual(
            len(root.children),
            4
        )

        self.assertEqual(
            len(root.untried_moves),
            0
        )

        self.assertTrue(
            root.is_fully_expanded()
        )

    def test_terminal_node(self):
        """测试终局节点识别。"""

        self.board.grid = [
            [BLACK for _ in range(BOARD_SIZE)]
            for _ in range(BOARD_SIZE)
        ]

        node = MCTSNode(
            board=self.board,
            player=WHITE,
        )

        self.assertTrue(
            node.is_terminal()
        )

    def test_expand_handles_pass(self):
        """测试扩展后正确处理 Pass。"""

        self.board.grid = [
            [BLACK for _ in range(BOARD_SIZE)]
            for _ in range(BOARD_SIZE)
        ]

        # 第一行：
        # B W . B W . B B
        #
        # 黑棋走 C1 后，
        # 白棋无合法动作，
        # 黑棋仍可以走 F1。
        self.board.grid[0][1] = WHITE
        self.board.grid[0][2] = EMPTY

        self.board.grid[0][4] = WHITE
        self.board.grid[0][5] = EMPTY

        root = MCTSNode(
            board=self.board,
            player=BLACK,
        )

        # 强制只扩展 C1
        root.untried_moves = [
            (0, 2)
        ]

        child = root.expand()

        self.assertEqual(
            child.move,
            (0, 2)
        )

        # 白棋应被跳过，
        # 下一步仍然轮到黑棋
        self.assertEqual(
            child.player,
            BLACK
        )

    def test_best_child_for_root_player(self):
        """
        当前轮到根玩家时，
        应优先选择平均收益更大的节点。
        """

        root = MCTSNode(
            board=self.board,
            player=BLACK,
        )

        child_a = MCTSNode(
            board=self.board.copy(),
            player=WHITE,
            parent=root,
            move=(2, 3),
        )

        child_b = MCTSNode(
            board=self.board.copy(),
            player=WHITE,
            parent=root,
            move=(3, 2),
        )

        root.children = [
            child_a,
            child_b,
        ]

        root.visits = 20

        child_a.visits = 10
        child_a.value = 8.0

        child_b.visits = 10
        child_b.value = 2.0

        best = root.best_child(
            exploration_constant=0.0,
            root_player=BLACK,
        )

        self.assertEqual(
            best,
            child_a
        )

    def test_best_child_for_opponent(self):
        """
        当前轮到对手时，
        应优先选择让根玩家收益更小的节点。
        """

        node = MCTSNode(
            board=self.board,
            player=WHITE,
        )

        child_a = MCTSNode(
            board=self.board.copy(),
            player=BLACK,
            parent=node,
            move=(2, 4),
        )

        child_b = MCTSNode(
            board=self.board.copy(),
            player=BLACK,
            parent=node,
            move=(3, 5),
        )

        node.children = [
            child_a,
            child_b,
        ]

        node.visits = 20

        child_a.visits = 10
        child_a.value = 8.0

        child_b.visits = 10
        child_b.value = 2.0

        best = node.best_child(
            exploration_constant=0.0,
            root_player=BLACK,
        )

        # 对手应该选择让黑棋收益更低的 B
        self.assertEqual(
            best,
            child_b
        )


class TestMCTSAI(unittest.TestCase):

    def setUp(self):
        self.board = Board()

    def test_choose_legal_move(self):
        """测试 MCTS 返回合法动作。"""

        ai = MCTSAI(
            simulations=50,
            random_seed=42,
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
        """测试 MCTS 不修改真实棋盘。"""

        ai = MCTSAI(
            simulations=50,
            random_seed=42,
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
        """测试没有合法动作时返回 None。"""

        self.board.grid = [
            [BLACK for _ in range(BOARD_SIZE)]
            for _ in range(BOARD_SIZE)
        ]

        ai = MCTSAI(
            simulations=20,
            random_seed=42,
        )

        move = ai.choose_move(
            self.board,
            WHITE
        )

        self.assertIsNone(
            move
        )

    def test_simulation_count(self):
        """测试实际模拟次数。"""

        ai = MCTSAI(
            simulations=30,
            random_seed=42,
        )

        ai.choose_move(
            self.board,
            BLACK
        )

        self.assertEqual(
            ai.simulations_run,
            30
        )

        self.assertGreater(
            ai.nodes_searched,
            0
        )

        self.assertGreaterEqual(
            ai.move_time,
            0.0
        )

    def test_choose_only_legal_move(self):
        """测试只有一个合法动作时必然选择该动作。"""

        self.board.grid = [
            [BLACK for _ in range(BOARD_SIZE)]
            for _ in range(BOARD_SIZE)
        ]

        # B W . B B B B B
        self.board.grid[0][1] = WHITE
        self.board.grid[0][2] = EMPTY

        valid_moves = (
            self.board.get_valid_moves(
                BLACK
            )
        )

        self.assertEqual(
            valid_moves,
            [(0, 2)]
        )

        ai = MCTSAI(
            simulations=20,
            random_seed=42,
        )

        move = ai.choose_move(
            self.board,
            BLACK
        )

        self.assertEqual(
            move,
            (0, 2)
        )

    def test_reproducible_with_same_seed(self):
        """测试相同随机种子能够复现实验。"""

        ai_a = MCTSAI(
            simulations=100,
            random_seed=42,
        )

        ai_b = MCTSAI(
            simulations=100,
            random_seed=42,
        )

        move_a = ai_a.choose_move(
            self.board,
            BLACK
        )

        move_b = ai_b.choose_move(
            self.board,
            BLACK
        )

        self.assertEqual(
            move_a,
            move_b
        )

    def test_invalid_simulation_count(self):
        """测试非法模拟次数。"""

        with self.assertRaises(
            ValueError
        ):
            MCTSAI(
                simulations=0
            )

    def test_invalid_exploration_constant(self):
        """测试非法探索常数。"""

        with self.assertRaises(
            ValueError
        ):
            MCTSAI(
                simulations=10,
                exploration_constant=-1.0,
            )


if __name__ == "__main__":
    unittest.main()