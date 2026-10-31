import math
import random
import time

from config import BLACK
from ai.base import BaseAI


class MCTSNode:

    def __init__(self, board, player, parent=None, move=None):
        self.board = board
        self.player = player
        self.parent = parent
        self.move = move

        self.children = []
        self.untried_moves = board.get_valid_moves(player)
        self.visits = 0
        self.value = 0.0  # 从根玩家视角累计收益

    def is_fully_expanded(self):
        return len(self.untried_moves) == 0

    def is_terminal(self):
        return self.board.is_game_over()

    def expand(self, rng=None):
        if not self.untried_moves:
            return None

        if rng is None:
            move = self.untried_moves.pop()
        else:
            index = rng.randrange(len(self.untried_moves))
            move = self.untried_moves.pop(index)

        row, col = move
        next_board = self.board.copy()
        next_board.make_move(row, col, self.player)

        next_player = -self.player

        # 对手无合法动作时自动 Pass
        if not next_board.has_valid_move(next_player) and next_board.has_valid_move(self.player):
            next_player = self.player

        child = MCTSNode(next_board, next_player, parent=self, move=move)
        self.children.append(child)

        return child

    def best_child(self, exploration_constant, root_player):
        """根据 UCT 公式选择子节点。"""
        if not self.children:
            return None

        best_score = -math.inf
        best_child = None

        for child in self.children:
            if child.visits == 0:
                uct_score = math.inf
            else:
                average_value = child.value / child.visits

                # 对手回合需要反转收益方向
                if self.player == root_player:
                    exploitation = average_value
                else:
                    exploitation = -average_value

                if self.visits > 0:
                    exploration = exploration_constant * math.sqrt(
                        math.log(self.visits) / child.visits
                    )
                else:
                    exploration = 0.0

                uct_score = exploitation + exploration

            if uct_score > best_score:
                best_score = uct_score
                best_child = child

        return best_child


class MCTSAI(BaseAI):

    def __init__(self, simulations=1000, exploration_constant=math.sqrt(2), random_seed=None):
        super().__init__("MCTS")

        if simulations < 1:
            raise ValueError("MCTS 模拟次数必须至少为 1")

        if exploration_constant < 0:
            raise ValueError("探索常数不能小于 0")

        self.simulations = simulations
        self.exploration_constant = exploration_constant
        self.random_seed = random_seed
        self.rng = random.Random(random_seed)
        self.simulations_run = 0

    def choose_move(self, board, player):
        self.reset_stats()
        self.simulations_run = 0
        start_time = time.perf_counter()

        valid_moves = board.get_valid_moves(player)

        if not valid_moves:
            self.move_time = time.perf_counter() - start_time
            return None

        root = MCTSNode(board.copy(), player)

        for _ in range(self.simulations):
            # Selection + Expansion
            node = self._select_and_expand(root, player)

            # Simulation
            result = self._simulate(node.board, node.player, player)

            # Backpropagation
            self._backpropagate(node, result)
            self.simulations_run += 1

        self.nodes_searched = self._count_nodes(root)

        # Robust Child：优先选择访问次数最多的子节点
        best_child = max(
            root.children,
            key=lambda child: (
                child.visits,
                child.value / child.visits if child.visits > 0 else -math.inf
            )
        )

        self.move_time = time.perf_counter() - start_time
        return best_child.move

    def _select_and_expand(self, root, root_player):
        node = root

        while not node.is_terminal():
            if not node.is_fully_expanded():
                return node.expand(self.rng)

            node = node.best_child(self.exploration_constant, root_player)

            if node is None:
                break

        return node

    def _simulate(self, board, player, root_player):
        """随机模拟完整对局。"""
        simulation_board = board.copy()
        current_player = player

        while not simulation_board.is_game_over():
            valid_moves = simulation_board.get_valid_moves(current_player)

            if not valid_moves:
                current_player = -current_player
                continue

            row, col = self.rng.choice(valid_moves)
            simulation_board.make_move(row, col, current_player)
            current_player = -current_player

        return self._get_result(simulation_board, root_player)

    def _get_result(self, board, root_player):
        black_count, white_count = board.count_pieces()

        if root_player == BLACK:
            difference = black_count - white_count
        else:
            difference = white_count - black_count

        if difference > 0:
            return 1.0

        if difference < 0:
            return -1.0

        return 0.0

    def _backpropagate(self, node, result):
        current = node

        while current is not None:
            current.visits += 1
            current.value += result
            current = current.parent

    def _count_nodes(self, node):
        count = 1

        for child in node.children:
            count += self._count_nodes(child)

        return count