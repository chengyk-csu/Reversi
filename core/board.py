
import copy

from config import BOARD_SIZE, EMPTY, BLACK, WHITE, DIRECTIONS


class Board:

    def __init__(self):
        self.grid = []
        self.reset()

    def reset(self):
        self.grid = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

        # 初始四颗棋子
        self.grid[3][3] = WHITE
        self.grid[3][4] = BLACK
        self.grid[4][3] = BLACK
        self.grid[4][4] = WHITE

    def is_on_board(self, row, col):
        return 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE

    def get_flips(self, row, col, player):
        """获取落子后需要翻转的棋子坐标。"""
        if not self.is_on_board(row, col):
            return []

        if self.grid[row][col] != EMPTY:
            return []

        opponent = -player
        all_flips = []

        for dr, dc in DIRECTIONS:
            current_row = row + dr
            current_col = col + dc
            direction_flips = []

            # 沿当前方向寻找连续的对方棋子
            while (self.is_on_board(current_row, current_col)
                   and self.grid[current_row][current_col] == opponent):
                direction_flips.append((current_row, current_col))
                current_row += dr
                current_col += dc

            # 只有被己方棋子封住时才能翻转
            if (direction_flips
                    and self.is_on_board(current_row, current_col)
                    and self.grid[current_row][current_col] == player):
                all_flips.extend(direction_flips)

        return all_flips

    def is_valid_move(self, row, col, player):
        return len(self.get_flips(row, col, player)) > 0

    def get_valid_moves(self, player):
        valid_moves = []

        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if self.is_valid_move(row, col, player):
                    valid_moves.append((row, col))

        return valid_moves

    def make_move(self, row, col, player):
        """执行合法落子并翻转棋子，非法落子返回 False。"""
        flips = self.get_flips(row, col, player)

        if not flips:
            return False

        self.grid[row][col] = player

        for flip_row, flip_col in flips:
            self.grid[flip_row][flip_col] = player

        return True

    def has_valid_move(self, player):
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if self.is_valid_move(row, col, player):
                    return True

        return False

    def is_game_over(self):
        return not self.has_valid_move(BLACK) and not self.has_valid_move(WHITE)

    def count_pieces(self):
        black_count = 0
        white_count = 0

        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if self.grid[row][col] == BLACK:
                    black_count += 1
                elif self.grid[row][col] == WHITE:
                    white_count += 1

        return black_count, white_count

    def copy(self):
        new_board = Board()
        new_board.grid = copy.deepcopy(self.grid)
        return new_board

    def __str__(self):
        symbols = {EMPTY: ".", BLACK: "B", WHITE: "W"}
        lines = ["  A B C D E F G H"]

        for row in range(BOARD_SIZE):
            line = [str(row + 1)]

            for col in range(BOARD_SIZE):
                piece = self.grid[row][col]
                line.append(symbols[piece])

            lines.append(" ".join(line))

        return "\n".join(lines)
