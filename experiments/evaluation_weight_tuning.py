
import csv
from pathlib import Path

from config import BLACK, WHITE
from ai.alphabeta import AlphaBetaAI
from ai.evaluation import evaluate_fixed, make_dynamic_evaluator
from experiments.evaluation_position_comparison import (
    generate_positions, create_game_from_position, serialize_board
)


OUTPUT_DIR = Path(__file__).parent
GAME_CSV = OUTPUT_DIR / "evaluation_weight_tuning_games.csv"
SUMMARY_CSV = OUTPUT_DIR / "evaluation_weight_tuning_summary.csv"


# 候选动态评价权重
CANDIDATE_PROFILES = {
    "current": {
        "opening": {
            "piece": -1.0, "position": 1.0,
            "mobility": 12.0, "corner": 30.0,
        },
        "midgame": {
            "piece": 1.0, "position": 1.0,
            "mobility": 15.0, "corner": 40.0,
        },
        "endgame": {
            "piece": 10.0, "position": 0.5,
            "mobility": 5.0, "corner": 50.0,
        },
    },

    "mobility_heavy": {
        "opening": {
            "piece": -1.0, "position": 1.0,
            "mobility": 16.0, "corner": 30.0,
        },
        "midgame": {
            "piece": 1.0, "position": 1.0,
            "mobility": 18.0, "corner": 40.0,
        },
        "endgame": {
            "piece": 10.0, "position": 0.5,
            "mobility": 4.0, "corner": 50.0,
        },
    },

    "corner_heavy": {
        "opening": {
            "piece": -1.0, "position": 1.0,
            "mobility": 12.0, "corner": 40.0,
        },
        "midgame": {
            "piece": 1.0, "position": 1.0,
            "mobility": 14.0, "corner": 55.0,
        },
        "endgame": {
            "piece": 10.0, "position": 0.5,
            "mobility": 4.0, "corner": 65.0,
        },
    },

    "endgame_piece_heavy": {
        "opening": {
            "piece": -1.0, "position": 1.0,
            "mobility": 12.0, "corner": 30.0,
        },
        "midgame": {
            "piece": 1.0, "position": 1.0,
            "mobility": 15.0, "corner": 40.0,
        },
        "endgame": {
            "piece": 15.0, "position": 0.5,
            "mobility": 3.0, "corner": 50.0,
        },
    },

    "balanced": {
        "opening": {
            "piece": -0.5, "position": 1.0,
            "mobility": 14.0, "corner": 35.0,
        },
        "midgame": {
            "piece": 2.0, "position": 1.0,
            "mobility": 14.0, "corner": 45.0,
        },
        "endgame": {
            "piece": 12.0, "position": 0.5,
            "mobility": 4.0, "corner": 55.0,
        },
    },
}


def play_game_from_position(board, current_player, candidate_evaluator, candidate_color, depth):
    """从指定局面开始，完成候选评价函数与固定评价函数的对战。"""
    fixed_ai = AlphaBetaAI(depth=depth, evaluator=evaluate_fixed)
    candidate_ai = AlphaBetaAI(depth=depth, evaluator=candidate_evaluator)

    if candidate_color == BLACK:
        black_ai = candidate_ai
        white_ai = fixed_ai
    else:
        black_ai = fixed_ai
        white_ai = candidate_ai

    game = create_game_from_position(board, current_player)

    candidate_nodes = 0
    fixed_nodes = 0
    moves = 0

    while not game.game_over:
        player = game.current_player
        ai = black_ai if player == BLACK else white_ai

        move = ai.choose_move(game.board, player)

        if move is None:
            raise RuntimeError("AI 没有返回合法落子，但比赛尚未结束。")

        row, col = move

        if ai is candidate_ai:
            candidate_nodes += ai.nodes_searched
        else:
            fixed_nodes += ai.nodes_searched

        success = game.play_move(row, col, move_time=ai.move_time)

        if not success:
            raise RuntimeError(f"AI 返回非法动作：{move}")

        moves += 1

    black_score, white_score = game.board.count_pieces()

    if candidate_color == BLACK:
        candidate_score = black_score
        fixed_score = white_score
        candidate_time = game.black_time
        fixed_time = game.white_time
        candidate_color_name = "Black"
    else:
        candidate_score = white_score
        fixed_score = black_score
        candidate_time = game.white_time
        fixed_time = game.black_time
        candidate_color_name = "White"

    if candidate_score > fixed_score:
        winner = "Candidate"
    elif fixed_score > candidate_score:
        winner = "Fixed"
    else:
        winner = "Draw"

    return {
        "candidate_color": candidate_color_name,
        "winner": winner,
        "candidate_score": candidate_score,
        "fixed_score": fixed_score,
        "score_diff": candidate_score - fixed_score,
        "candidate_time": candidate_time,
        "fixed_time": fixed_time,
        "candidate_nodes": candidate_nodes,
        "fixed_nodes": fixed_nodes,
        "moves": moves,
    }


def evaluate_profile(profile_name, weights, positions, depth):
    """在相同测试局面上评估一套候选权重。"""
    candidate_evaluator = make_dynamic_evaluator(weights)
    records = []

    for position in positions:
        # 每个局面交换黑白棋，减少先后手影响
        for candidate_color in (BLACK, WHITE):
            result = play_game_from_position(
                board=position["board"],
                current_player=position["current_player"],
                candidate_evaluator=candidate_evaluator,
                candidate_color=candidate_color,
                depth=depth
            )

            starting_player = "Black" if position["current_player"] == BLACK else "White"

            record = {
                "profile": profile_name,
                "position_id": position["position_id"],
                "phase": position["phase"],
                "seed": position["seed"],
                "depth": depth,
                "starting_occupied": position["occupied"],
                "starting_player": starting_player,
                "starting_board": serialize_board(position["board"]),
                "candidate_color": result["candidate_color"],
                "winner": result["winner"],
                "candidate_score": result["candidate_score"],
                "fixed_score": result["fixed_score"],
                "score_diff": result["score_diff"],
                "candidate_time": result["candidate_time"],
                "fixed_time": result["fixed_time"],
                "candidate_nodes": result["candidate_nodes"],
                "fixed_nodes": result["fixed_nodes"],
                "moves": result["moves"],
            }

            records.append(record)

    return records


def summarize_profile(records, profile_name, phase):
    """按阶段汇总候选权重的对战表现。"""
    selected = [
        record for record in records
        if record["profile"] == profile_name
        and (phase == "overall" or record["phase"] == phase)
    ]

    games = len(selected)

    if games == 0:
        return None

    candidate_wins = sum(1 for record in selected if record["winner"] == "Candidate")
    fixed_wins = sum(1 for record in selected if record["winner"] == "Fixed")
    draws = games - candidate_wins - fixed_wins

    candidate_score_sum = sum(record["candidate_score"] for record in selected)
    fixed_score_sum = sum(record["fixed_score"] for record in selected)

    candidate_time_sum = sum(record["candidate_time"] for record in selected)
    fixed_time_sum = sum(record["fixed_time"] for record in selected)

    candidate_nodes_sum = sum(record["candidate_nodes"] for record in selected)
    fixed_nodes_sum = sum(record["fixed_nodes"] for record in selected)

    # 比赛积分：胜 1 分，平 0.5 分，负 0 分
    match_points = candidate_wins + 0.5 * draws

    return {
        "profile": profile_name,
        "phase": phase,
        "games": games,
        "candidate_wins": candidate_wins,
        "fixed_wins": fixed_wins,
        "draws": draws,
        "candidate_win_rate": candidate_wins / games,
        "fixed_win_rate": fixed_wins / games,
        "draw_rate": draws / games,
        "match_point_rate": match_points / games,
        "candidate_avg_score": candidate_score_sum / games,
        "fixed_avg_score": fixed_score_sum / games,
        "avg_score_diff": (candidate_score_sum - fixed_score_sum) / games,
        "candidate_avg_time": candidate_time_sum / games,
        "fixed_avg_time": fixed_time_sum / games,
        "candidate_avg_nodes": candidate_nodes_sum / games,
        "fixed_avg_nodes": fixed_nodes_sum / games,
    }


def save_game_records(records):
    fieldnames = [
        "profile", "position_id", "phase", "seed", "depth",
        "starting_occupied", "starting_player", "starting_board",
        "candidate_color", "winner",
        "candidate_score", "fixed_score", "score_diff",
        "candidate_time", "fixed_time",
        "candidate_nodes", "fixed_nodes", "moves",
    ]

    with open(GAME_CSV, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)


def save_summaries(summaries):
    fieldnames = [
        "profile", "phase", "games",
        "candidate_wins", "fixed_wins", "draws",
        "candidate_win_rate", "fixed_win_rate", "draw_rate",
        "match_point_rate",
        "candidate_avg_score", "fixed_avg_score", "avg_score_diff",
        "candidate_avg_time", "fixed_avg_time",
        "candidate_avg_nodes", "fixed_avg_nodes",
    ]

    with open(SUMMARY_CSV, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(summaries)


def print_ranking(summaries):
    """按总体积分率和平均棋子差对候选参数排序。"""
    overall = [summary for summary in summaries if summary["phase"] == "overall"]

    overall.sort(
        key=lambda item: (item["match_point_rate"], item["avg_score_diff"]),
        reverse=True
    )

    print()
    print("=" * 90)
    print("Dynamic Evaluation Weight Tuning Ranking")
    print("=" * 90)

    print(
        f"{'Rank':<7}{'Profile':<24}{'Points':<12}"
        f"{'WinRate':<12}{'ScoreDiff':<14}{'AvgTime':<12}"
    )
    print("-" * 90)

    for rank, summary in enumerate(overall, start=1):
        print(
            f"{rank:<7}"
            f"{summary['profile']:<24}"
            f"{summary['match_point_rate']:<12.3f}"
            f"{summary['candidate_win_rate']:<12.3f}"
            f"{summary['avg_score_diff']:<14.2f}"
            f"{summary['candidate_avg_time']:<12.4f}"
        )

    print("=" * 90)

    if overall:
        best = overall[0]

        print()
        print("当前表现最好的候选权重：")
        print(best["profile"])
        print("Match point rate:", f"{best['match_point_rate']:.2%}")
        print("Average score difference:", f"{best['avg_score_diff']:.2f}")


def main():
    # 第一轮参数筛选：3 个阶段，每阶段 2 个局面，交换颜色各对战一次
    positions_per_phase = 2
    depth = 3
    base_seed = 2026

    print("正在生成统一测试局面……")
    positions = generate_positions(positions_per_phase, base_seed)
    print("生成完成，共", len(positions), "个局面。")

    all_records = []
    all_summaries = []

    # 所有候选参数使用完全相同的测试局面
    for profile_index, (profile_name, weights) in enumerate(CANDIDATE_PROFILES.items(), start=1):
        print()
        print("=" * 70)
        print(f"[{profile_index}/{len(CANDIDATE_PROFILES)}] Testing profile: {profile_name}")
        print("=" * 70)

        records = evaluate_profile(profile_name, weights, positions, depth)
        all_records.extend(records)

        for phase in ("opening", "midgame", "endgame", "overall"):
            summary = summarize_profile(records, profile_name, phase)

            if summary is not None:
                all_summaries.append(summary)

                print(
                    f"{phase:<9} | "
                    f"wins={summary['candidate_wins']:<2} | "
                    f"draws={summary['draws']:<2} | "
                    f"losses={summary['fixed_wins']:<2} | "
                    f"score diff={summary['avg_score_diff']:.2f}"
                )

    save_game_records(all_records)
    save_summaries(all_summaries)
    print_ranking(all_summaries)

    print()
    print("逐局实验数据：")
    print(GAME_CSV)
    print()
    print("汇总实验数据：")
    print(SUMMARY_CSV)


if __name__ == "__main__":
    main()
