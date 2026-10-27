import csv
import random
from pathlib import Path

from config import (
    EMPTY,
    BLACK,
    WHITE,
)
from core.game import Game
from ai.alphabeta import AlphaBetaAI
from ai.evaluation import (
    evaluate_fixed,
    evaluate_dynamic,
    get_game_phase,
)


# ============================================================
# 输出文件
# ============================================================

OUTPUT_DIR = Path(__file__).parent

GAME_CSV = (
    OUTPUT_DIR
    / "evaluation_position_games.csv"
)

SUMMARY_CSV = (
    OUTPUT_DIR
    / "evaluation_position_summary.csv"
)


# ============================================================
# 棋盘序列化
# ============================================================

def serialize_board(board):
    """
    将棋盘压缩为 64 个字符，
    方便保存到 CSV 中并复现实验。

    B = 黑棋
    W = 白棋
    . = 空格
    """

    symbols = {
        EMPTY: ".",
        BLACK: "B",
        WHITE: "W",
    }

    result = []

    for row in board.grid:

        for piece in row:

            result.append(
                symbols[piece]
            )

    return "".join(result)


# ============================================================
# 生成随机局面
# ============================================================

def generate_position(
    seed,
    target_occupied,
):
    """
    从标准初始局面开始随机合法下棋，
    直到棋盘上的棋子数量达到目标值。

    返回：
        board
        current_player
        occupied
    """

    rng = random.Random(
        seed
    )

    game = Game()

    while not game.game_over:

        black_count, white_count = (
            game.board.count_pieces()
        )

        occupied = (
            black_count
            + white_count
        )

        if occupied >= target_occupied:

            return (
                game.board.copy(),
                game.current_player,
                occupied,
            )

        valid_moves = (
            game.get_valid_moves()
        )

        if not valid_moves:

            raise RuntimeError(
                "生成随机局面时出现异常："
                "当前玩家没有合法动作，"
                "但 Game 尚未正确结束或 Pass。"
            )

        move = rng.choice(
            valid_moves
        )

        row, col = move

        success = game.play_move(
            row,
            col,
        )

        if not success:

            raise RuntimeError(
                "生成随机局面时产生非法落子。"
            )

    raise RuntimeError(
        "棋局在达到目标阶段之前已经结束。"
    )


# ============================================================
# 批量生成三个阶段的局面
# ============================================================

def generate_positions(
    positions_per_phase,
    base_seed,
):
    """
    生成：
        opening
        midgame
        endgame

    三个阶段的随机合法局面。
    """

    phase_configs = [
        (
            "opening",
            16,
            0,
        ),
        (
            "midgame",
            34,
            10000,
        ),
        (
            "endgame",
            54,
            20000,
        ),
    ]

    positions = []

    for (
        expected_phase,
        target_occupied,
        seed_offset,
    ) in phase_configs:

        generated = 0

        attempt = 0

        while (
            generated
            < positions_per_phase
        ):

            seed = (
                base_seed
                + seed_offset
                + attempt
            )

            attempt += 1

            try:

                (
                    board,
                    current_player,
                    occupied,
                ) = generate_position(
                    seed=seed,
                    target_occupied=target_occupied,
                )

            except RuntimeError:

                continue

            actual_phase = (
                get_game_phase(
                    board
                )
            )

            # 阶段必须与目标一致
            if (
                actual_phase
                != expected_phase
            ):

                continue

            # 不能是已经结束的局面
            if board.is_game_over():

                continue

            # 当前玩家必须真的有合法棋
            if not board.has_valid_move(
                current_player
            ):

                continue

            positions.append({
                "position_id": (
                    f"{expected_phase}_"
                    f"{generated + 1}"
                ),

                "phase": (
                    expected_phase
                ),

                "seed": seed,

                "target_occupied": (
                    target_occupied
                ),

                "occupied": (
                    occupied
                ),

                "current_player": (
                    current_player
                ),

                "board": (
                    board
                ),
            })

            generated += 1

    return positions


# ============================================================
# 从任意局面创建 Game
# ============================================================

def create_game_from_position(
    board,
    current_player,
):
    """从指定棋盘局面开始比赛。"""

    game = Game()

    game.board = (
        board.copy()
    )

    game.current_player = (
        current_player
    )

    game.game_over = (
        game.board.is_game_over()
    )

    game.move_history = []

    game.black_time = 0.0
    game.white_time = 0.0

    game.end_reason = None
    game.timed_out_player = None
    game.forced_winner = None

    if game.game_over:

        game.end_reason = (
            "normal"
        )

    return game


# ============================================================
# 从指定局面进行一局比赛
# ============================================================

def play_from_position(
    board,
    current_player,
    fixed_color,
    depth,
):
    """
    从同一个指定局面开始：

    一方使用 Fixed Evaluation，
    另一方使用 Dynamic Evaluation。
    """

    fixed_ai = AlphaBetaAI(
        depth=depth,
        evaluator=evaluate_fixed,
    )

    dynamic_ai = AlphaBetaAI(
        depth=depth,
        evaluator=evaluate_dynamic,
    )

    if fixed_color == BLACK:

        black_ai = fixed_ai
        white_ai = dynamic_ai

    else:

        black_ai = dynamic_ai
        white_ai = fixed_ai

    game = create_game_from_position(
        board,
        current_player,
    )

    fixed_nodes = 0
    dynamic_nodes = 0

    moves = 0

    while not game.game_over:

        player = (
            game.current_player
        )

        if player == BLACK:

            ai = black_ai

        else:

            ai = white_ai

        move = ai.choose_move(
            game.board,
            player,
        )

        if move is None:

            raise RuntimeError(
                "AI 没有返回合法动作，"
                "但当前游戏尚未结束。"
            )

        row, col = move

        if ai is fixed_ai:

            fixed_nodes += (
                ai.nodes_searched
            )

        else:

            dynamic_nodes += (
                ai.nodes_searched
            )

        success = game.play_move(
            row,
            col,
            move_time=ai.move_time,
        )

        if not success:

            raise RuntimeError(
                f"{ai.name} 返回非法动作："
                f"{move}"
            )

        moves += 1

    black_score, white_score = (
        game.board.count_pieces()
    )

    if fixed_color == BLACK:

        fixed_score = (
            black_score
        )

        dynamic_score = (
            white_score
        )

        fixed_time = (
            game.black_time
        )

        dynamic_time = (
            game.white_time
        )

        fixed_color_name = (
            "Black"
        )

    else:

        fixed_score = (
            white_score
        )

        dynamic_score = (
            black_score
        )

        fixed_time = (
            game.white_time
        )

        dynamic_time = (
            game.black_time
        )

        fixed_color_name = (
            "White"
        )

    if fixed_score > dynamic_score:

        winner = (
            "Fixed"
        )

    elif dynamic_score > fixed_score:

        winner = (
            "Dynamic"
        )

    else:

        winner = (
            "Draw"
        )

    return {
        "fixed_color": (
            fixed_color_name
        ),

        "winner": (
            winner
        ),

        "fixed_score": (
            fixed_score
        ),

        "dynamic_score": (
            dynamic_score
        ),

        "score_diff_dynamic": (
            dynamic_score
            - fixed_score
        ),

        "fixed_time": (
            fixed_time
        ),

        "dynamic_time": (
            dynamic_time
        ),

        "fixed_nodes": (
            fixed_nodes
        ),

        "dynamic_nodes": (
            dynamic_nodes
        ),

        "moves": (
            moves
        ),
    }


# ============================================================
# 对单个局面交换颜色进行两局比赛
# ============================================================

def run_position_pair(
    position,
    depth,
):
    """
    同一个局面运行两局：

    第 1 局：
        Fixed = Black
        Dynamic = White

    第 2 局：
        Dynamic = Black
        Fixed = White
    """

    records = []

    for fixed_color in (
        BLACK,
        WHITE,
    ):

        result = (
            play_from_position(
                board=position["board"],
                current_player=position[
                    "current_player"
                ],
                fixed_color=fixed_color,
                depth=depth,
            )
        )

        current_player_name = (
            "Black"
            if (
                position[
                    "current_player"
                ]
                == BLACK
            )
            else "White"
        )

        record = {
            "position_id": (
                position[
                    "position_id"
                ]
            ),

            "phase": (
                position[
                    "phase"
                ]
            ),

            "seed": (
                position[
                    "seed"
                ]
            ),

            "depth": (
                depth
            ),

            "starting_occupied": (
                position[
                    "occupied"
                ]
            ),

            "starting_player": (
                current_player_name
            ),

            "starting_board": (
                serialize_board(
                    position[
                        "board"
                    ]
                )
            ),

            "fixed_color": (
                result[
                    "fixed_color"
                ]
            ),

            "winner": (
                result[
                    "winner"
                ]
            ),

            "fixed_score": (
                result[
                    "fixed_score"
                ]
            ),

            "dynamic_score": (
                result[
                    "dynamic_score"
                ]
            ),

            "score_diff_dynamic": (
                result[
                    "score_diff_dynamic"
                ]
            ),

            "fixed_time": (
                result[
                    "fixed_time"
                ]
            ),

            "dynamic_time": (
                result[
                    "dynamic_time"
                ]
            ),

            "fixed_nodes": (
                result[
                    "fixed_nodes"
                ]
            ),

            "dynamic_nodes": (
                result[
                    "dynamic_nodes"
                ]
            ),

            "moves": (
                result[
                    "moves"
                ]
            ),
        }

        records.append(
            record
        )

    return records


# ============================================================
# 汇总某一阶段
# ============================================================

def summarize_records(
    records,
    phase,
):
    """汇总指定阶段的实验数据。"""

    if phase == "overall":

        selected = (
            records
        )

    else:

        selected = [
            record
            for record in records
            if (
                record["phase"]
                == phase
            )
        ]

    games = len(
        selected
    )

    if games == 0:

        return None

    fixed_wins = sum(
        1
        for record in selected
        if (
            record["winner"]
            == "Fixed"
        )
    )

    dynamic_wins = sum(
        1
        for record in selected
        if (
            record["winner"]
            == "Dynamic"
        )
    )

    draws = (
        games
        - fixed_wins
        - dynamic_wins
    )

    fixed_score_sum = sum(
        record["fixed_score"]
        for record in selected
    )

    dynamic_score_sum = sum(
        record["dynamic_score"]
        for record in selected
    )

    fixed_time_sum = sum(
        record["fixed_time"]
        for record in selected
    )

    dynamic_time_sum = sum(
        record["dynamic_time"]
        for record in selected
    )

    fixed_nodes_sum = sum(
        record["fixed_nodes"]
        for record in selected
    )

    dynamic_nodes_sum = sum(
        record["dynamic_nodes"]
        for record in selected
    )

    unique_positions = len(
        {
            record["position_id"]
            for record in selected
        }
    )

    return {
        "phase": phase,

        "positions": (
            unique_positions
        ),

        "games": (
            games
        ),

        "fixed_wins": (
            fixed_wins
        ),

        "dynamic_wins": (
            dynamic_wins
        ),

        "draws": (
            draws
        ),

        "fixed_win_rate": (
            fixed_wins
            / games
        ),

        "dynamic_win_rate": (
            dynamic_wins
            / games
        ),

        "draw_rate": (
            draws
            / games
        ),

        "fixed_avg_score": (
            fixed_score_sum
            / games
        ),

        "dynamic_avg_score": (
            dynamic_score_sum
            / games
        ),

        "dynamic_avg_score_diff": (
            (
                dynamic_score_sum
                - fixed_score_sum
            )
            / games
        ),

        "fixed_avg_time": (
            fixed_time_sum
            / games
        ),

        "dynamic_avg_time": (
            dynamic_time_sum
            / games
        ),

        "fixed_avg_nodes": (
            fixed_nodes_sum
            / games
        ),

        "dynamic_avg_nodes": (
            dynamic_nodes_sum
            / games
        ),
    }


# ============================================================
# 保存逐局数据
# ============================================================

def save_game_records(
    records,
):
    """保存每一局原始实验数据。"""

    fieldnames = [
        "position_id",
        "phase",
        "seed",
        "depth",

        "starting_occupied",
        "starting_player",
        "starting_board",

        "fixed_color",
        "winner",

        "fixed_score",
        "dynamic_score",
        "score_diff_dynamic",

        "fixed_time",
        "dynamic_time",

        "fixed_nodes",
        "dynamic_nodes",

        "moves",
    ]

    with open(
        GAME_CSV,
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        writer.writerows(
            records
        )


# ============================================================
# 保存汇总数据
# ============================================================

def save_summaries(
    summaries,
):
    """保存阶段汇总数据。"""

    fieldnames = [
        "phase",

        "positions",
        "games",

        "fixed_wins",
        "dynamic_wins",
        "draws",

        "fixed_win_rate",
        "dynamic_win_rate",
        "draw_rate",

        "fixed_avg_score",
        "dynamic_avg_score",
        "dynamic_avg_score_diff",

        "fixed_avg_time",
        "dynamic_avg_time",

        "fixed_avg_nodes",
        "dynamic_avg_nodes",
    ]

    with open(
        SUMMARY_CSV,
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        writer.writerows(
            summaries
        )


# ============================================================
# 打印汇总
# ============================================================

def print_summary(
    summary,
):
    """打印单个阶段汇总结果。"""

    print()
    print("=" * 70)

    print(
        "Phase:",
        summary["phase"]
    )

    print(
        "Positions:",
        summary["positions"]
    )

    print(
        "Games:",
        summary["games"]
    )

    print("-" * 70)

    print(
        "Fixed wins:",
        summary["fixed_wins"]
    )

    print(
        "Dynamic wins:",
        summary["dynamic_wins"]
    )

    print(
        "Draws:",
        summary["draws"]
    )

    print()

    print(
        "Fixed win rate:",
        f"{summary['fixed_win_rate']:.2%}"
    )

    print(
        "Dynamic win rate:",
        f"{summary['dynamic_win_rate']:.2%}"
    )

    print()

    print(
        "Fixed avg score:",
        f"{summary['fixed_avg_score']:.2f}"
    )

    print(
        "Dynamic avg score:",
        f"{summary['dynamic_avg_score']:.2f}"
    )

    print(
        "Dynamic avg score diff:",
        f"{summary['dynamic_avg_score_diff']:.2f}"
    )

    print()

    print(
        "Fixed avg time:",
        f"{summary['fixed_avg_time']:.6f}s"
    )

    print(
        "Dynamic avg time:",
        f"{summary['dynamic_avg_time']:.6f}s"
    )

    print()

    print(
        "Fixed avg nodes:",
        f"{summary['fixed_avg_nodes']:.2f}"
    )

    print(
        "Dynamic avg nodes:",
        f"{summary['dynamic_avg_nodes']:.2f}"
    )

    print("=" * 70)


# ============================================================
# 主实验
# ============================================================

def main():

    # ========================================================
    # 功能验证参数
    #
    # 三个阶段各生成 3 个局面。
    # 每个局面交换颜色各比赛一次。
    #
    # 总比赛数：
    #
    # 3 phases
    # × 3 positions
    # × 2 games
    # = 18 games
    # ========================================================

    positions_per_phase = 3

    depth = 3

    base_seed = 2026

    print(
        "正在生成随机合法局面……"
    )

    positions = (
        generate_positions(
            positions_per_phase=(
                positions_per_phase
            ),
            base_seed=base_seed,
        )
    )

    print(
        f"共生成 "
        f"{len(positions)} "
        f"个局面。"
    )

    print()

    all_records = []

    for index, position in enumerate(
        positions,
        start=1,
    ):

        player_name = (
            "Black"
            if (
                position[
                    "current_player"
                ]
                == BLACK
            )
            else "White"
        )

        print(
            f"[{index}/{len(positions)}] "
            f"{position['position_id']} | "
            f"phase={position['phase']} | "
            f"occupied={position['occupied']} | "
            f"to_move={player_name}"
        )

        records = (
            run_position_pair(
                position=position,
                depth=depth,
            )
        )

        for record in records:

            print(
                f"    Fixed="
                f"{record['fixed_color']:<5} | "
                f"{record['fixed_score']:02d}:"
                f"{record['dynamic_score']:02d} | "
                f"Winner={record['winner']}"
            )

        all_records.extend(
            records
        )

    # ========================================================
    # 按阶段汇总
    # ========================================================

    summaries = []

    for phase in (
        "opening",
        "midgame",
        "endgame",
        "overall",
    ):

        summary = (
            summarize_records(
                all_records,
                phase,
            )
        )

        if summary is not None:

            summaries.append(
                summary
            )

            print_summary(
                summary
            )

    # ========================================================
    # CSV
    # ========================================================

    save_game_records(
        all_records
    )

    save_summaries(
        summaries
    )

    print()
    print(
        "逐局数据已保存到："
    )

    print(
        GAME_CSV
    )

    print()

    print(
        "阶段汇总已保存到："
    )

    print(
        SUMMARY_CSV
    )


if __name__ == "__main__":
    main()