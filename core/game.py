from config import BLACK, WHITE, EMPTY
from core.board import Board


class Game:

    def __init__(self):

        self.board = Board()

        self.current_player = BLACK

        self.game_over = False

        self.move_history = []

        # 双方累计思考时间
        self.black_time = 0.0
        self.white_time = 0.0

        # 游戏结束原因：
        # None
        # "normal"
        # "timeout"
        self.end_reason = None

        # 超时玩家
        self.timed_out_player = None

        # 非正常结束时指定获胜方
        self.forced_winner = None

    def reset(self):
        """重新开始一局游戏。"""

        self.board.reset()

        self.current_player = BLACK

        self.game_over = False

        self.move_history = []

        self.black_time = 0.0
        self.white_time = 0.0

        self.end_reason = None

        self.timed_out_player = None

        self.forced_winner = None

    def get_valid_moves(self):
        """获取当前玩家所有合法动作。"""

        return self.board.get_valid_moves(
            self.current_player
        )

    def play_move(
        self,
        row,
        col,
        move_time=0.0,
    ):
        """当前玩家执行一次落子。"""

        if self.game_over:
            return False

        player = self.current_player

        flips = self.board.get_flips(
            row,
            col,
            player,
        )

        if not flips:
            return False

        self.board.make_move(
            row,
            col,
            player,
        )

        # =========================
        # 累计思考时间
        # =========================

        if player == BLACK:

            self.black_time += (
                move_time
            )

        elif player == WHITE:

            self.white_time += (
                move_time
            )

        # =========================
        # 保存历史记录
        # =========================

        self.move_history.append({
            "player": player,
            "move": (row, col),
            "flips": len(flips),
            "time": move_time,
        })

        self._advance_turn()

        return True

    def _advance_turn(self):
        """
        推进回合。

        如果对方无棋可下，
        自动 Pass。

        如果双方均无棋可下，
        游戏正常结束。
        """

        next_player = (
            -self.current_player
        )

        # 对方可以下
        if self.board.has_valid_move(
            next_player
        ):

            self.current_player = (
                next_player
            )

            return

        # 对方不能下，但当前玩家还能继续
        if self.board.has_valid_move(
            self.current_player
        ):

            return

        # 双方均无棋可下
        self.game_over = True

        self.end_reason = "normal"

    def declare_timeout(
        self,
        player,
    ):
        """
        宣布某一方思考超时。

        超时方立即判负。
        """

        if player not in (
            BLACK,
            WHITE,
        ):
            raise ValueError(
                "超时玩家必须是 BLACK 或 WHITE"
            )

        if self.game_over:
            return False

        self.game_over = True

        self.end_reason = "timeout"

        self.timed_out_player = (
            player
        )

        self.forced_winner = (
            -player
        )

        return True

    def get_winner(self):
        """获取获胜方。"""

        if not self.game_over:
            return None

        # 超时等特殊情况
        if self.forced_winner is not None:

            return self.forced_winner

        # 正常棋局结束
        black_count, white_count = (
            self.board.count_pieces()
        )

        if black_count > white_count:
            return BLACK

        if white_count > black_count:
            return WHITE

        return EMPTY

    def get_player_name(
        self,
        player,
    ):
        """获取玩家中文名称。"""

        if player == BLACK:
            return "黑棋"

        if player == WHITE:
            return "白棋"

        return "未知"