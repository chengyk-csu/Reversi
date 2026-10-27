import math
import random
import time

from config import BLACK
from ai.base import BaseAI


class MCTSNode:
    """
    MCTS 搜索树中的一个节点。
    """

    def __init__(
        self,
        board,
        player,
        parent=None,
        move=None,
    ):
        self.board = board

        # 当前局面下一步轮到谁
        self.player = player

        # 父节点
        self.parent = parent

        # 从父节点来到当前节点的动作
        self.move = move

        # 已经扩展出的子节点
        self.children = []

        # 尚未尝试的合法动作
        self.untried_moves = (
            board.get_valid_moves(player)
        )

        # 访问次数
        self.visits = 0

        # 从根玩家视角统计的累计收益
        self.value = 0.0

    def is_fully_expanded(self):
        """是否已经扩展所有合法动作。"""

        return len(
            self.untried_moves
        ) == 0

    def is_terminal(self):
        """当前节点是否为终局。"""

        return self.board.is_game_over()

    def expand(self, rng=None):
        """
        扩展一个尚未尝试的动作。
        """

        if not self.untried_moves:
            return None

        if rng is None:
            move = self.untried_moves.pop()

        else:
            index = rng.randrange(
                len(self.untried_moves)
            )

            move = self.untried_moves.pop(
                index
            )

        row, col = move

        next_board = self.board.copy()

        next_board.make_move(
            row,
            col,
            self.player
        )

        next_player = -self.player

        # 自动处理 Pass
        if (
            not next_board.has_valid_move(
                next_player
            )
            and
            next_board.has_valid_move(
                self.player
            )
        ):
            next_player = self.player

        child = MCTSNode(
            board=next_board,
            player=next_player,
            parent=self,
            move=move,
        )

        self.children.append(
            child
        )

        return child

    def best_child(
        self,
        exploration_constant,
        root_player,
    ):
        """
        根据 UCT 选择最佳子节点。
        """

        if not self.children:
            return None

        best_score = -math.inf
        best_child = None

        for child in self.children:

            if child.visits == 0:
                uct_score = math.inf

            else:
                average_value = (
                    child.value
                    / child.visits
                )

                # 当前轮到根玩家
                if self.player == root_player:
                    exploitation = average_value

                # 当前轮到对手
                else:
                    exploitation = -average_value

                if self.visits > 0:
                    exploration = (
                        exploration_constant
                        * math.sqrt(
                            math.log(
                                self.visits
                            )
                            / child.visits
                        )
                    )

                else:
                    exploration = 0.0

                uct_score = (
                    exploitation
                    + exploration
                )

            if uct_score > best_score:
                best_score = uct_score
                best_child = child

        return best_child


class MCTSAI(BaseAI):

    def __init__(
        self,
        simulations=1000,
        exploration_constant=math.sqrt(2),
        random_seed=None,
    ):
        super().__init__("MCTS")

        if simulations < 1:
            raise ValueError(
                "MCTS 模拟次数必须至少为 1"
            )

        if exploration_constant < 0:
            raise ValueError(
                "探索常数不能小于 0"
            )

        self.simulations = simulations

        self.exploration_constant = (
            exploration_constant
        )

        self.random_seed = random_seed

        self.rng = random.Random(
            random_seed
        )

        self.simulations_run = 0

    def choose_move(
        self,
        board,
        player,
    ):
        """使用 MCTS 选择最佳落子。"""

        self.reset_stats()

        self.simulations_run = 0

        start_time = time.perf_counter()

        valid_moves = (
            board.get_valid_moves(
                player
            )
        )

        if not valid_moves:
            self.move_time = (
                time.perf_counter()
                - start_time
            )

            return None

        root = MCTSNode(
            board=board.copy(),
            player=player,
        )

        for _ in range(
            self.simulations
        ):

            # Selection + Expansion
            node = self._select_and_expand(
                root,
                player,
            )

            # Simulation
            result = self._simulate(
                node.board,
                node.player,
                player,
            )

            # Backpropagation
            self._backpropagate(
                node,
                result,
            )

            self.simulations_run += 1

        self.nodes_searched = (
            self._count_nodes(
                root
            )
        )

        # Robust Child：
        # 优先选择访问次数最多的动作
        best_child = max(
            root.children,
            key=lambda child: (
                child.visits,
                (
                    child.value
                    / child.visits
                    if child.visits > 0
                    else -math.inf
                ),
            ),
        )

        self.move_time = (
            time.perf_counter()
            - start_time
        )

        return best_child.move

    def _select_and_expand(
        self,
        root,
        root_player,
    ):
        """执行 Selection 和 Expansion。"""

        node = root

        while not node.is_terminal():

            if not node.is_fully_expanded():

                return node.expand(
                    self.rng
                )

            node = node.best_child(
                self.exploration_constant,
                root_player,
            )

            if node is None:
                break

        return node

    def _simulate(
        self,
        board,
        player,
        root_player,
    ):
        """
        随机模拟到终局。
        """

        simulation_board = (
            board.copy()
        )

        current_player = player

        while not simulation_board.is_game_over():

            valid_moves = (
                simulation_board.get_valid_moves(
                    current_player
                )
            )

            # Pass
            if not valid_moves:

                current_player = (
                    -current_player
                )

                continue

            move = self.rng.choice(
                valid_moves
            )

            row, col = move

            simulation_board.make_move(
                row,
                col,
                current_player
            )

            current_player = (
                -current_player
            )

        return self._get_result(
            simulation_board,
            root_player,
        )

    def _get_result(
        self,
        board,
        root_player,
    ):
        """计算终局收益。"""

        black_count, white_count = (
            board.count_pieces()
        )

        if root_player == BLACK:

            difference = (
                black_count
                - white_count
            )

        else:

            difference = (
                white_count
                - black_count
            )

        if difference > 0:
            return 1.0

        if difference < 0:
            return -1.0

        return 0.0

    def _backpropagate(
        self,
        node,
        result,
    ):
        """将模拟结果反向传播到根节点。"""

        current = node

        while current is not None:

            current.visits += 1
            current.value += result

            current = current.parent

    def _count_nodes(
        self,
        node,
    ):
        """统计搜索树实际节点数量。"""

        count = 1

        for child in node.children:

            count += self._count_nodes(
                child
            )

        return count