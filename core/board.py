from config import BOARD_SIZE, EMPTY, BLACK, WHITE, DIRECTIONS
import copy

class Board:
    def __init__(self):
        self.grid = []
        self.reset()

    def reset(self):
        """初始化黑白棋棋盘。"""

        # 创建 8 × 8 的空棋盘
        self.grid = [
            [EMPTY for _ in range(BOARD_SIZE)]
            for _ in range(BOARD_SIZE)
        ]

        # 黑白棋初始四颗棋子
        self.grid[3][3] = WHITE
        self.grid[3][4] = BLACK
        self.grid[4][3] = BLACK
        self.grid[4][4] = WHITE

    def is_on_board(self, row, col):
        """判断指定位置是否位于棋盘范围内。"""

        return (
            0 <= row < BOARD_SIZE
            and
            0 <= col < BOARD_SIZE
        )

    def get_flips(self, row, col, player):
        """
        获取 player 落子在 (row, col) 后，
        所有应该被翻转的对方棋子坐标。

        如果该位置不能形成任何翻转，则返回空列表。
        """

        # 落子位置必须位于棋盘内
        if not self.is_on_board(row, col):
            return []

        # 落子位置必须为空
        if self.grid[row][col] != EMPTY:
            return []

        opponent = -player

        all_flips = []

        # 分别检查八个方向
        for dr, dc in DIRECTIONS:
            current_row = row + dr
            current_col = col + dc

            direction_flips = []

            # 沿当前方向连续寻找对方棋子
            while (
                self.is_on_board(current_row, current_col)
                and
                self.grid[current_row][current_col] == opponent
            ):
                direction_flips.append(
                    (current_row, current_col)
                )

                current_row += dr
                current_col += dc

            # 如果前面确实遇到了对方棋子，
            # 并且最后被自己的棋子封住，
            # 这个方向上的对方棋子才可以翻转
            if (
                direction_flips
                and
                self.is_on_board(current_row, current_col)
                and
                self.grid[current_row][current_col] == player
            ):
                all_flips.extend(direction_flips)

        return all_flips

    def is_valid_move(self, row, col, player):
        """判断 player 是否可以落子在指定位置。"""

        return len(self.get_flips(row, col, player)) > 0

    def get_valid_moves(self, player):
        """获取 player 当前所有合法落子位置。"""

        valid_moves = []

        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):

                if self.is_valid_move(row, col, player):
                    valid_moves.append((row, col))

        return valid_moves

    def make_move(self, row, col, player):
        """
        执行一次落子。

        如果落子合法：
        1. 在 (row, col) 放置 player 的棋子
        2. 翻转所有被夹住的对方棋子
        3. 返回 True

        如果落子不合法：
        返回 False
        """

        flips = self.get_flips(row, col, player)

        if not flips:
            return False

        # 放置新棋子
        self.grid[row][col] = player

        # 翻转被夹住的棋子
        for flip_row, flip_col in flips:
            self.grid[flip_row][flip_col] = player

        return True

    def has_valid_move(self, player):
        """判断 player 当前是否至少存在一个合法落子。"""

        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if self.is_valid_move(row, col, player):
                    return True

        return False

    def is_game_over(self):
        """判断棋局是否已经结束。"""

        return (
            not self.has_valid_move(BLACK)
            and
            not self.has_valid_move(WHITE)
        )

    def count_pieces(self):
        """
        统计棋盘上的黑棋和白棋数量。

        返回：
        (black_count, white_count)
        """

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
        """返回当前棋盘的独立副本。"""

        new_board = Board()

        new_board.grid = copy.deepcopy(self.grid)

        return new_board

    def __str__(self):
        """将棋盘转换成便于调试的字符串。"""

        symbols = {
            EMPTY: ".",
            BLACK: "B",
            WHITE: "W",
        }

        lines = []

        # 列标
        lines.append("  A B C D E F G H")

        for row in range(BOARD_SIZE):
            line = [str(row + 1)]

            for col in range(BOARD_SIZE):
                piece = self.grid[row][col]
                line.append(symbols[piece])

            lines.append(" ".join(line))

        return "\n".join(lines)