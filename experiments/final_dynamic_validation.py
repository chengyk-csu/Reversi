
import csv
from pathlib import Path

from experiments.evaluation_position_comparison import generate_positions
from experiments.evaluation_weight_tuning import (
    CANDIDATE_PROFILES, evaluate_profile, summarize_profile
)


OUTPUT_DIR = Path(__file__).parent
GAME_CSV = OUTPUT_DIR / "final_dynamic_validation_games.csv"
SUMMARY_CSV = OUTPUT_DIR / "final_dynamic_validation_summary.csv"

FINAL_PROFILE_NAME = "current"
FINAL_WEIGHTS = CANDIDATE_PROFILES[FINAL_PROFILE_NAME]


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


def print_summary(summary):
    print()
    print("=" * 80)
    print("Phase:", summary["phase"])
    print("=" * 80)
    print("Games:", summary["games"])
    print()

    print("Dynamic wins:", summary["candidate_wins"])
    print("Fixed wins:", summary["fixed_wins"])
    print("Draws:", summary["draws"])
    print()

    print("Dynamic win rate:", f"{summary['candidate_win_rate']:.2%}")
    print("Fixed win rate:", f"{summary['fixed_win_rate']:.2%}")
    print("Draw rate:", f"{summary['draw_rate']:.2%}")
    print()

    print("Dynamic match point rate:", f"{summary['match_point_rate']:.2%}")
    print()

    print("Dynamic average score:", f"{summary['candidate_avg_score']:.2f}")
    print("Fixed average score:", f"{summary['fixed_avg_score']:.2f}")
    print("Dynamic average score difference:", f"{summary['avg_score_diff']:.2f}")
    print()

    print("Dynamic average decision time:", f"{summary['candidate_avg_time']:.4f}s")
    print("Fixed average decision time:", f"{summary['fixed_avg_time']:.4f}s")
    print()

    print("Dynamic average nodes:", f"{summary['candidate_avg_nodes']:.1f}")
    print("Fixed average nodes:", f"{summary['fixed_avg_nodes']:.1f}")


def print_final_conclusion(overall):
    print()
    print("=" * 90)
    print("FINAL DYNAMIC EVALUATION VALIDATION")
    print("=" * 90)
    print("Final profile:", FINAL_PROFILE_NAME)
    print()

    print("Match point rate:", f"{overall['match_point_rate']:.2%}")
    print("Win rate:", f"{overall['candidate_win_rate']:.2%}")
    print("Average score difference:", f"{overall['avg_score_diff']:.2f}")
    print("Average decision time:", f"{overall['candidate_avg_time']:.4f}s")
    print("Average searched nodes:", f"{overall['candidate_avg_nodes']:.1f}")
    print()

    if overall["match_point_rate"] > 0.5:
        print(
            "Result: Dynamic Evaluation outperformed Fixed Evaluation "
            "on the final unseen test set."
        )
    elif overall["match_point_rate"] == 0.5:
        print(
            "Result: Dynamic Evaluation and Fixed Evaluation achieved "
            "the same match-point performance."
        )
    else:
        print(
            "Result: Dynamic Evaluation did not outperform Fixed Evaluation "
            "on the final unseen test set."
        )

    print("=" * 90)


def main():
    # 使用独立随机种子生成最终测试集，与前两轮调参数据分离
    # 三个阶段各 10 个局面，每个局面交换颜色对战两次，共 60 局
    depth = 4
    positions_per_phase = 10
    base_seed = 32026

    print("=" * 90)
    print("Final Dynamic Evaluation Validation")
    print("=" * 90)
    print("Depth:", depth)
    print("Positions per phase:", positions_per_phase)
    print("Final profile:", FINAL_PROFILE_NAME)
    print()

    print("Generating final unseen positions...")
    positions = generate_positions(positions_per_phase, base_seed)

    print("Generated positions:", len(positions))
    print("Total games:", len(positions) * 2)
    print()

    print("Running final validation...")
    records = evaluate_profile(FINAL_PROFILE_NAME, FINAL_WEIGHTS, positions, depth)

    summaries = []
    overall = None

    for phase in ("opening", "midgame", "endgame", "overall"):
        summary = summarize_profile(records, FINAL_PROFILE_NAME, phase)

        if summary is None:
            continue

        summaries.append(summary)
        print_summary(summary)

        if phase == "overall":
            overall = summary

    save_game_records(records)
    save_summaries(summaries)

    if overall is not None:
        print_final_conclusion(overall)

    print()
    print("Game records:")
    print(GAME_CSV)
    print()
    print("Summary:")
    print(SUMMARY_CSV)


if __name__ == "__main__":
    main()
