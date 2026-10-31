from config import BOARD_SIZE, BLACK, WHITE


# 棋盘位置权重
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

CORNERS = [(0, 0), (0, 7), (7, 0), (7, 7)]

# 开局、中局、残局的动态评价权重
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


def piece_difference(board, player):
    black_count, white_count = board.count_pieces()

    if player == BLACK:
        return black_count - white_count

    if player == WHITE:
        return white_count - black_count

    return 0


def positional_score(board, player):
    score = 0

    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            piece = board.grid[row][col]

            if piece == player:
                score += POSITION_WEIGHTS[row][col]
            elif piece == -player:
                score -= POSITION_WEIGHTS[row][col]

    return score


def mobility_score(board, player):
    player_moves = len(board.get_valid_moves(player))
    opponent_moves = len(board.get_valid_moves(-player))

    return player_moves - opponent_moves


def corner_score(board, player):
    score = 0

    for row, col in CORNERS:
        if board.grid[row][col] == player:
            score += 1
        elif board.grid[row][col] == -player:
            score -= 1

    return score


def get_game_phase(board):
    """根据已占据格数划分开局(≤20)、中局(≤50)和残局。"""
    black_count, white_count = board.count_pieces()
    occupied = black_count + white_count

    if occupied <= 20:
        return "opening"

    if occupied <= 50:
        return "midgame"

    return "endgame"


def evaluate_fixed(board, player):
    piece = piece_difference(board, player)
    position = positional_score(board, player)
    mobility = mobility_score(board, player)
    corner = corner_score(board, player)

    return piece + position + 10 * mobility + 25 * corner


def evaluate_with_weights(board, player, weights):
    phase = get_game_phase(board)
    phase_weights = weights[phase]

    piece = piece_difference(board, player)
    position = positional_score(board, player)
    mobility = mobility_score(board, player)
    corner = corner_score(board, player)

    return (
        phase_weights["piece"] * piece
        + phase_weights["position"] * position
        + phase_weights["mobility"] * mobility
        + phase_weights["corner"] * corner
    )


def evaluate_dynamic(board, player):
    return evaluate_with_weights(board, player, DYNAMIC_WEIGHTS)


def make_dynamic_evaluator(weights):
    """复制权重并生成独立评价函数，用于参数调优实验。"""
    copied_weights = {phase: values.copy() for phase, values in weights.items()}

    def evaluator(board, player):
        return evaluate_with_weights(board, player, copied_weights)

    return evaluator


def evaluate(board, player):
    # 默认使用固定评价函数，保持旧接口兼容
    return evaluate_fixed(board, player)