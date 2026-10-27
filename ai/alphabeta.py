import time
import math

from config import BLACK
from ai.base import BaseAI
from ai.evaluation import evaluate


class AlphaBetaAI(BaseAI):

    def __init__(
        self,
        depth=3,
        evaluator=evaluate,
    ):
        super().__init__(
            "Alpha-Beta"
        )

        if depth < 1:
            raise ValueError(
                "Alpha-Beta 搜索深度必须至少为 1"
            )

        self.depth = depth

        self.evaluator = evaluator

    def choose_move(
        self,
        board,
        player,
    ):
        """使用 Alpha-Beta 剪枝选择最佳落子。"""

        self.reset_stats()

        start_time = (
            time.perf_counter()
        )

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

        best_score = (
            -math.inf
        )

        best_move = None

        alpha = (
            -math.inf
        )

        beta = (
            math.inf
        )

        for row, col in valid_moves:

            next_board = (
                board.copy()
            )

            next_board.make_move(
                row,
                col,
                player,
            )

            score = (
                self._alphabeta(
                    board=next_board,
                    depth=self.depth - 1,
                    current_player=-player,
                    root_player=player,
                    alpha=alpha,
                    beta=beta,
                )
            )

            if score > best_score:

                best_score = (
                    score
                )

                best_move = (
                    row,
                    col,
                )

            alpha = max(
                alpha,
                best_score,
            )

        self.move_time = (
            time.perf_counter()
            - start_time
        )

        return best_move

    def _alphabeta(
        self,
        board,
        depth,
        current_player,
        root_player,
        alpha,
        beta,
    ):
        """Alpha-Beta 递归搜索。"""

        self.nodes_searched += 1

        # ====================================================
        # 终局
        # ====================================================

        if board.is_game_over():

            return self._terminal_score(
                board,
                root_player,
            )

        # ====================================================
        # 搜索深度到达 0
        # ====================================================

        if depth <= 0:

            return self.evaluator(
                board,
                root_player,
            )

        # ====================================================
        # 当前玩家所有合法动作
        # ====================================================

        valid_moves = (
            board.get_valid_moves(
                current_player
            )
        )

        # ====================================================
        # Pass
        # ====================================================

        if not valid_moves:

            return self._alphabeta(
                board=board,
                depth=depth,
                current_player=-current_player,
                root_player=root_player,
                alpha=alpha,
                beta=beta,
            )

        # ====================================================
        # MAX 层
        # ====================================================

        if (
            current_player
            == root_player
        ):

            best_score = (
                -math.inf
            )

            for row, col in valid_moves:

                next_board = (
                    board.copy()
                )

                next_board.make_move(
                    row,
                    col,
                    current_player,
                )

                score = (
                    self._alphabeta(
                        board=next_board,
                        depth=depth - 1,
                        current_player=-current_player,
                        root_player=root_player,
                        alpha=alpha,
                        beta=beta,
                    )
                )

                best_score = max(
                    best_score,
                    score,
                )

                alpha = max(
                    alpha,
                    best_score,
                )

                # Alpha-Beta 剪枝
                if alpha >= beta:
                    break

            return best_score

        # ====================================================
        # MIN 层
        # ====================================================

        else:

            best_score = (
                math.inf
            )

            for row, col in valid_moves:

                next_board = (
                    board.copy()
                )

                next_board.make_move(
                    row,
                    col,
                    current_player,
                )

                score = (
                    self._alphabeta(
                        board=next_board,
                        depth=depth - 1,
                        current_player=-current_player,
                        root_player=root_player,
                        alpha=alpha,
                        beta=beta,
                    )
                )

                best_score = min(
                    best_score,
                    score,
                )

                beta = min(
                    beta,
                    best_score,
                )

                # Alpha-Beta 剪枝
                if alpha >= beta:
                    break

            return best_score

    def _terminal_score(
        self,
        board,
        root_player,
    ):
        """对终局进行评分。"""

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

            return (
                100000
                + difference
            )

        if difference < 0:

            return (
                -100000
                + difference
            )

        return 0