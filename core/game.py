
from config import BLACK, WHITE, EMPTY
from core.board import Board


class Game:

    def __init__(self):
        self.board = Board()
        self.current_player = BLACK
        self.game_over = False
        self.move_history = []

        self.black_time = 0.0
        self.white_time = 0.0

        self.end_reason = None
        self.timed_out_player = None
        self.forced_winner = None

    def reset(self):
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
        return self.board.get_valid_moves(self.current_player)

    def play_move(self, row, col, move_time=0.0):
        if self.game_over:
            return False

        player = self.current_player
        flips = self.board.get_flips(row, col, player)

        if not flips:
            return False

        self.board.make_move(row, col, player)

        if player == BLACK:
            self.black_time += move_time
        elif player == WHITE:
            self.white_time += move_time

        self.move_history.append({
            "player": player,
            "move": (row, col),
            "flips": len(flips),
            "time": move_time,
        })

        self._advance_turn()
        return True

    def _advance_turn(self):
        """切换回合，自动处理 Pass 和正常终局。"""
        next_player = -self.current_player

        if self.board.has_valid_move(next_player):
            self.current_player = next_player
            return

        # 对方无合法动作，当前玩家继续落子
        if self.board.has_valid_move(self.current_player):
            return

        # 双方均无合法动作，游戏结束
        self.game_over = True
        self.end_reason = "normal"

    def declare_timeout(self, player):
        """超时玩家立即判负。"""
        if player not in (BLACK, WHITE):
            raise ValueError("超时玩家必须是 BLACK 或 WHITE")

        if self.game_over:
            return False

        self.game_over = True
        self.end_reason = "timeout"
        self.timed_out_player = player
        self.forced_winner = -player

        return True

    def get_winner(self):
        if not self.game_over:
            return None

        # 超时判负优先于棋子数量
        if self.forced_winner is not None:
            return self.forced_winner

        black_count, white_count = self.board.count_pieces()

        if black_count > white_count:
            return BLACK

        if white_count > black_count:
            return WHITE

        return EMPTY

    def get_player_name(self, player):
        if player == BLACK:
            return "黑棋"

        if player == WHITE:
            return "白棋"

        return "未知"
