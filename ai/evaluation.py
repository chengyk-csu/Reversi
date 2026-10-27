from config import (
    BOARD_SIZE,
    BLACK,
    WHITE,
)


# ============================================================
# 位置权重表
# ============================================================

POSITION_WEIGHTS = [
    [120, -20, 20, 5, 5, 20, -20, 120],
    [-20, -40, -5, -5, -5, -5, -40, -20],
    [20, -5, 15, 3, 3, 15, -5, 20],
    [5, -5, 3, 3, 3, 3, -5, 5],
    [5, -5, 3, 3, 3, 3, -5, 5],
    [20, -5, 15, 3, 3, 15, -5, 20],
    [-20, -40, -5, -5, -5, -5, -40, -20],
    [120, -20, 20, 5, 5, 20, -20, 120],
]


# ============================================================
# 四个角
# ============================================================

CORNERS = [
    (0, 0),
    (0, 7),
    (7, 0),
    (7, 7),
]


# ============================================================
# 当前默认动态评价权重
# ============================================================

DYNAMIC_WEIGHTS = {

    "opening": {
        "piece": -1.0,
        "position": 1.0,
        "mobility": 12.0,
        "corner": 30.0,
    },

    "midgame": {
        "piece": 1.0,
        "position": 1.0,
        "mobility": 15.0,
        "corner": 40.0,
    },

    "endgame": {
        "piece": 10.0,
        "position": 0.5,
        "mobility": 5.0,
        "corner": 50.0,
    },
}


# ============================================================
# 基础评价项
# ============================================================

def piece_difference(
    board,
    player,
):
    """计算当前玩家与对手的棋子数量差。"""

    black_count, white_count = (
        board.count_pieces()
    )

    if player == BLACK:

        return (
            black_count
            - white_count
        )

    if player == WHITE:

        return (
            white_count
            - black_count
        )

    return 0


def positional_score(
    board,
    player,
):
    """根据位置权重表计算位置得分。"""

    score = 0

    for row in range(
        BOARD_SIZE
    ):

        for col in range(
            BOARD_SIZE
        ):

            piece = (
                board.grid[row][col]
            )

            if piece == player:

                score += (
                    POSITION_WEIGHTS[
                        row
                    ][
                        col
                    ]
                )

            elif piece == -player:

                score -= (
                    POSITION_WEIGHTS[
                        row
                    ][
                        col
                    ]
                )

    return score


def mobility_score(
    board,
    player,
):
    """计算双方合法动作数量差。"""

    player_moves = len(
        board.get_valid_moves(
            player
        )
    )

    opponent_moves = len(
        board.get_valid_moves(
            -player
        )
    )

    return (
        player_moves
        - opponent_moves
    )


def corner_score(
    board,
    player,
):
    """计算四个角的占有差。"""

    score = 0

    for row, col in CORNERS:

        if (
            board.grid[row][col]
            == player
        ):

            score += 1

        elif (
            board.grid[row][col]
            == -player
        ):

            score -= 1

    return score


# ============================================================
# 阶段判断
# ============================================================

def get_game_phase(
    board,
):
    """
    根据当前棋盘已占据格数判断阶段。

    opening:
        4 ~ 20

    midgame:
        21 ~ 50

    endgame:
        51 ~ 64
    """

    black_count, white_count = (
        board.count_pieces()
    )

    occupied = (
        black_count
        + white_count
    )

    if occupied <= 20:

        return "opening"

    if occupied <= 50:

        return "midgame"

    return "endgame"


# ============================================================
# 固定评价
# ============================================================

def evaluate_fixed(
    board,
    player,
):
    """原始固定权重评价函数。"""

    piece = piece_difference(
        board,
        player,
    )

    position = positional_score(
        board,
        player,
    )

    mobility = mobility_score(
        board,
        player,
    )

    corner = corner_score(
        board,
        player,
    )

    return (
        piece
        + position
        + 10 * mobility
        + 25 * corner
    )


# ============================================================
# 通用动态评价
# ============================================================

def evaluate_with_weights(
    board,
    player,
    weights,
):
    """
    使用指定的阶段权重进行评价。

    weights 格式：

    {
        "opening": {...},
        "midgame": {...},
        "endgame": {...},
    }
    """

    phase = get_game_phase(
        board
    )

    phase_weights = (
        weights[phase]
    )

    piece = piece_difference(
        board,
        player,
    )

    position = positional_score(
        board,
        player,
    )

    mobility = mobility_score(
        board,
        player,
    )

    corner = corner_score(
        board,
        player,
    )

    return (
        phase_weights["piece"]
        * piece

        + phase_weights["position"]
        * position

        + phase_weights["mobility"]
        * mobility

        + phase_weights["corner"]
        * corner
    )


# ============================================================
# 默认动态评价
# ============================================================

def evaluate_dynamic(
    board,
    player,
):
    """使用当前默认动态阶段权重。"""

    return evaluate_with_weights(
        board,
        player,
        DYNAMIC_WEIGHTS,
    )


# ============================================================
# 动态 evaluator 工厂
# ============================================================

def make_dynamic_evaluator(
    weights,
):
    """
    根据一套权重生成独立评价函数。

    用于自动调参实验。
    """

    copied_weights = {
        phase: values.copy()
        for phase, values in (
            weights.items()
        )
    }

    def evaluator(
        board,
        player,
    ):

        return evaluate_with_weights(
            board,
            player,
            copied_weights,
        )

    return evaluator


# ============================================================
# 默认评价函数
# ============================================================

def evaluate(
    board,
    player,
):
    """
    默认仍使用 Fixed Evaluation。

    保证旧代码与旧测试兼容。
    """

    return evaluate_fixed(
        board,
        player,
    )