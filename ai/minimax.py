import time
import math

from config import BLACK
from ai.base import BaseAI
from ai.evaluation import evaluate

class MinimaxAI(BaseAI):

    def __init__(self, depth=3,evaluator=evaluate):
        super().__init__("Minimax")

        if depth < 1:
            raise ValueError(
                "Minimax 搜索深度必须至少为 1"
            )

        self.depth = depth
        self.evaluator = evaluator
    def choose_move(self, board, player):
        """
        使用 Minimax 为 player 选择最佳落子。
        """

        self.reset_stats()

        start_time = time.perf_counter()

        valid_moves = board.get_valid_moves(player)

        # 当前没有棋可下
        if not valid_moves:
            self.move_time = (
                time.perf_counter()
                - start_time
            )

            return None

        best_score = -math.inf
        best_move = None

        for row, col in valid_moves:

            next_board = board.copy()

            next_board.make_move(
                row,
                col,
                player
            )

            score = self._minimax(
                board=next_board,
                depth=self.depth - 1,
                current_player=-player,
                root_player=player,
            )

            if score > best_score:
                best_score = score
                best_move = (row, col)

        self.move_time = (
            time.perf_counter()
            - start_time
        )
        return best_move

    def _minimax(
            self,
            board,
            depth,
            current_player,
            root_player,
    ):
        """
        Minimax 递归搜索。

        current_player：
        当前轮到谁。

        root_player：
        最开始调用 AI 的玩家，也就是
        整棵搜索树始终站在哪一方视角评价。
        """

        self.nodes_searched += 1

        # 先判断游戏是否真正结束
        if board.is_game_over():
            return self._terminal_score(
                board,
                root_player
            )

        # 到达搜索深度限制
        if depth <= 0:
            return self.evaluator(
                board,
                root_player,
            )

        valid_moves = board.get_valid_moves(
            current_player
        )

        # 当前玩家没有棋可下：
        # Pass，换另一方继续搜索
        if not valid_moves:
            return self._minimax(
                board=board,
                depth=depth,
                current_player=-current_player,
                root_player=root_player,
            )

        # 当前轮到 AI 自己：
        # MAX 层
        if current_player == root_player:

            best_score = -math.inf

            for row, col in valid_moves:
                next_board = board.copy()

                next_board.make_move(
                    row,
                    col,
                    current_player
                )

                score = self._minimax(
                    board=next_board,
                    depth=depth - 1,
                    current_player=-current_player,
                    root_player=root_player,
                )

                best_score = max(
                    best_score,
                    score
                )

            return best_score

        # 当前轮到对手：
        # MIN 层
        else:

            best_score = math.inf

            for row, col in valid_moves:
                next_board = board.copy()

                next_board.make_move(
                    row,
                    col,
                    current_player
                )

                score = self._minimax(
                    board=next_board,
                    depth=depth - 1,
                    current_player=-current_player,
                    root_player=root_player,
                )

                best_score = min(
                    best_score,
                    score
                )

            return best_score

    def _terminal_score(
            self,
            board,
            root_player,
    ):
        """对已经结束的棋局进行评分。"""

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
            return 100000 + difference

        if difference < 0:
            return -100000 + difference

        return 0