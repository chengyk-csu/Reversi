import csv
from pathlib import Path

from config import BLACK, WHITE
from core.game import Game
from ai.minimax import MinimaxAI
from ai.alphabeta import AlphaBetaAI
from ai.mcts import MCTSAI
from utils.coordinates import position_to_notation


OUTPUT_DIR = Path(__file__).parent

GAME_CSV = (
    OUTPUT_DIR
    / "tournament_games.csv"
)

SUMMARY_CSV = (
    OUTPUT_DIR
    / "tournament_summary.csv"
)


def play_game(
    black_ai,
    white_ai,
    verbose=False,
):
    """
    让两个 AI 自动完成一局黑白棋。

    返回本局比赛结果。
    """

    game = Game()

    move_number = 0

    while not game.game_over:

        current_player = (
            game.current_player
        )

        if current_player == BLACK:
            ai = black_ai
        else:
            ai = white_ai

        move = ai.choose_move(
            game.board,
            current_player,
        )

        if move is None:
            raise RuntimeError(
                f"{ai.name} 没有返回合法动作，"
                "但当前 Game 尚未结束。"
            )

        row, col = move

        success = game.play_move(
            row,
            col,
            move_time=ai.move_time,
        )

        if not success:
            raise RuntimeError(
                f"{ai.name} 返回非法落子："
                f"{position_to_notation(row, col)}"
            )

        move_number += 1

        if verbose:
            print(
                f"第 {move_number:02d} 步 | "
                f"{game.get_player_name(current_player):<4} | "
                f"{ai.name:<10} | "
                f"{position_to_notation(row, col):<3} | "
                f"{ai.move_time:.6f}s | "
                f"nodes={ai.nodes_searched}"
            )

    black_count, white_count = (
        game.board.count_pieces()
    )

    winner = game.get_winner()

    return {
        "winner": winner,
        "black_score": black_count,
        "white_score": white_count,
        "black_time": game.black_time,
        "white_time": game.white_time,
        "moves": move_number,
    }


def play_series(
    label_a,
    label_b,
    ai_a_factory,
    ai_b_factory,
    games,
    base_seed,
):
    """
    A 与 B 进行多局系列赛。

    每局交换先后手，
    并使用不同随机种子。
    """

    if games < 1:
        raise ValueError(
            "比赛局数必须至少为 1"
        )

    game_records = []

    a_wins = 0
    b_wins = 0
    draws = 0

    a_total_score = 0
    b_total_score = 0

    a_total_time = 0.0
    b_total_time = 0.0

    for game_index in range(games):

        seed_a = (
            base_seed
            + game_index * 2
        )

        seed_b = (
            base_seed
            + game_index * 2
            + 1
        )

        ai_a = ai_a_factory(
            seed_a
        )

        ai_b = ai_b_factory(
            seed_b
        )

        # =========================
        # 交替交换黑白棋
        # =========================

        if game_index % 2 == 0:

            black_ai = ai_a
            white_ai = ai_b

            a_color = BLACK

        else:

            black_ai = ai_b
            white_ai = ai_a

            a_color = WHITE

        result = play_game(
            black_ai=black_ai,
            white_ai=white_ai,
            verbose=False,
        )

        # =========================
        # 转换成 A/B 视角
        # =========================

        if a_color == BLACK:

            a_score = (
                result["black_score"]
            )

            b_score = (
                result["white_score"]
            )

            a_time = (
                result["black_time"]
            )

            b_time = (
                result["white_time"]
            )

            a_color_name = "Black"

        else:

            a_score = (
                result["white_score"]
            )

            b_score = (
                result["black_score"]
            )

            a_time = (
                result["white_time"]
            )

            b_time = (
                result["black_time"]
            )

            a_color_name = "White"

        # =========================
        # 判断 A/B 胜负
        # =========================

        if a_score > b_score:

            a_wins += 1

            winner_name = label_a

        elif b_score > a_score:

            b_wins += 1

            winner_name = label_b

        else:

            draws += 1

            winner_name = "Draw"

        a_total_score += a_score
        b_total_score += b_score

        a_total_time += a_time
        b_total_time += b_time

        record = {
            "matchup": (
                f"{label_a} vs {label_b}"
            ),

            "game": (
                game_index + 1
            ),

            "algorithm_a": label_a,
            "algorithm_b": label_b,

            "a_color": a_color_name,

            "seed_a": seed_a,
            "seed_b": seed_b,

            "winner": winner_name,

            "a_score": a_score,
            "b_score": b_score,

            "score_diff": (
                a_score - b_score
            ),

            "a_time": a_time,
            "b_time": b_time,

            "moves": result["moves"],
        }

        game_records.append(
            record
        )

        print(
            f"[{label_a} vs {label_b}] "
            f"Game {game_index + 1}/{games} | "
            f"A={a_color_name:<5} | "
            f"{a_score:02d}:{b_score:02d} | "
            f"Winner={winner_name}"
        )

    # =========================
    # 系列赛汇总
    # =========================

    summary = {
        "algorithm_a": label_a,
        "algorithm_b": label_b,

        "games": games,

        "a_wins": a_wins,
        "b_wins": b_wins,
        "draws": draws,

        "a_win_rate": (
            a_wins / games
        ),

        "b_win_rate": (
            b_wins / games
        ),

        "draw_rate": (
            draws / games
        ),

        "a_avg_score": (
            a_total_score / games
        ),

        "b_avg_score": (
            b_total_score / games
        ),

        "a_avg_score_diff": (
            (
                a_total_score
                - b_total_score
            )
            / games
        ),

        "a_avg_time": (
            a_total_time / games
        ),

        "b_avg_time": (
            b_total_time / games
        ),
    }

    return (
        game_records,
        summary,
    )


def save_game_records(
    records,
):
    """保存逐局比赛数据。"""

    fieldnames = [
        "matchup",
        "game",

        "algorithm_a",
        "algorithm_b",

        "a_color",

        "seed_a",
        "seed_b",

        "winner",

        "a_score",
        "b_score",
        "score_diff",

        "a_time",
        "b_time",

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


def save_summaries(
    summaries,
):
    """保存系列赛汇总数据。"""

    fieldnames = [
        "algorithm_a",
        "algorithm_b",

        "games",

        "a_wins",
        "b_wins",
        "draws",

        "a_win_rate",
        "b_win_rate",
        "draw_rate",

        "a_avg_score",
        "b_avg_score",
        "a_avg_score_diff",

        "a_avg_time",
        "b_avg_time",
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


def print_summary(
    summary,
):
    """终端显示系列赛汇总。"""

    label_a = (
        summary["algorithm_a"]
    )

    label_b = (
        summary["algorithm_b"]
    )

    print()
    print("=" * 60)

    print(
        f"{label_a} vs {label_b}"
    )

    print("-" * 60)

    print(
        f"{label_a} wins: "
        f"{summary['a_wins']}"
    )

    print(
        f"{label_b} wins: "
        f"{summary['b_wins']}"
    )

    print(
        f"Draws: "
        f"{summary['draws']}"
    )

    print()

    print(
        f"{label_a} win rate: "
        f"{summary['a_win_rate']:.2%}"
    )

    print(
        f"{label_b} win rate: "
        f"{summary['b_win_rate']:.2%}"
    )

    print()

    print(
        f"{label_a} avg score: "
        f"{summary['a_avg_score']:.2f}"
    )

    print(
        f"{label_b} avg score: "
        f"{summary['b_avg_score']:.2f}"
    )

    print()

    print(
        f"{label_a} avg time: "
        f"{summary['a_avg_time']:.6f}s"
    )

    print(
        f"{label_b} avg time: "
        f"{summary['b_avg_time']:.6f}s"
    )

    print("=" * 60)


def main():

    # =========================
    # 当前先使用较小参数验证框架
    # =========================

    games_per_matchup = 4

    minimax_depth = 3

    alphabeta_depth = 3

    mcts_simulations = 100

    base_seed = 42

    all_records = []

    all_summaries = []

    # =========================
    # 1. Minimax vs Alpha-Beta
    # =========================

    records, summary = play_series(

        label_a="Minimax",

        label_b="Alpha-Beta",

        ai_a_factory=lambda seed: MinimaxAI(
            depth=minimax_depth
        ),

        ai_b_factory=lambda seed: AlphaBetaAI(
            depth=alphabeta_depth
        ),

        games=games_per_matchup,

        base_seed=base_seed,
    )

    all_records.extend(
        records
    )

    all_summaries.append(
        summary
    )

    print_summary(
        summary
    )

    # =========================
    # 2. Minimax vs MCTS
    # =========================

    records, summary = play_series(

        label_a="Minimax",

        label_b="MCTS",

        ai_a_factory=lambda seed: MinimaxAI(
            depth=minimax_depth
        ),

        ai_b_factory=lambda seed: MCTSAI(
            simulations=mcts_simulations,
            random_seed=seed,
        ),

        games=games_per_matchup,

        base_seed=base_seed + 1000,
    )

    all_records.extend(
        records
    )

    all_summaries.append(
        summary
    )

    print_summary(
        summary
    )

    # =========================
    # 3. Alpha-Beta vs MCTS
    # =========================

    records, summary = play_series(

        label_a="Alpha-Beta",

        label_b="MCTS",

        ai_a_factory=lambda seed: AlphaBetaAI(
            depth=alphabeta_depth
        ),

        ai_b_factory=lambda seed: MCTSAI(
            simulations=mcts_simulations,
            random_seed=seed,
        ),

        games=games_per_matchup,

        base_seed=base_seed + 2000,
    )

    all_records.extend(
        records
    )

    all_summaries.append(
        summary
    )

    print_summary(
        summary
    )

    # =========================
    # 保存 CSV
    # =========================

    save_game_records(
        all_records
    )

    save_summaries(
        all_summaries
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
        "汇总数据已保存到："
    )

    print(
        SUMMARY_CSV
    )


if __name__ == "__main__":
    main()