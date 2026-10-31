
import csv
from pathlib import Path

from experiments.evaluation_position_comparison import generate_positions
from experiments.evaluation_weight_tuning import (
    CANDIDATE_PROFILES, evaluate_profile, summarize_profile
)


OUTPUT_DIR = Path(__file__).parent
GAME_CSV = OUTPUT_DIR / "evaluation_weight_tuning_round2_games.csv"
SUMMARY_CSV = OUTPUT_DIR / "evaluation_weight_tuning_round2_summary.csv"

ROUND2_PROFILE_NAMES = ["endgame_piece_heavy", "current", "balanced"]


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


def print_phase_summary(summary):
    print(
        f"{summary['phase']:<9} | "
        f"W={summary['candidate_wins']:<2} "
        f"D={summary['draws']:<2} "
        f"L={summary['fixed_wins']:<2} | "
        f"points={summary['match_point_rate']:.3f} | "
        f"score diff={summary['avg_score_diff']:.2f}"
    )


def print_ranking(summaries):
    """根据总体积分率、平均棋子差和胜率进行排名。"""
    overall = [summary for summary in summaries if summary["phase"] == "overall"]

    overall.sort(
        key=lambda item: (
            item["match_point_rate"],
            item["avg_score_diff"],
            item["candidate_win_rate"],
        ),
        reverse=True
    )

    print()
    print("=" * 100)
    print("Round 2 Dynamic Evaluation Ranking")
    print("=" * 100)

    print(
        f"{'Rank':<7}{'Profile':<24}{'Points':<12}"
        f"{'WinRate':<12}{'ScoreDiff':<14}"
        f"{'AvgTime':<12}{'AvgNodes':<14}"
    )
    print("-" * 100)

    for rank, summary in enumerate(overall, start=1):
        print(
            f"{rank:<7}"
            f"{summary['profile']:<24}"
            f"{summary['match_point_rate']:<12.3f}"
            f"{summary['candidate_win_rate']:<12.3f}"
            f"{summary['avg_score_diff']:<14.2f}"
            f"{summary['candidate_avg_time']:<12.4f}"
            f"{summary['candidate_avg_nodes']:<14.1f}"
        )

    print("=" * 100)

    if overall:
        best = overall[0]

        print()
        print("第二轮排名第一：", best["profile"])
        print("比赛积分率：", f"{best['match_point_rate']:.2%}")
        print("胜率：", f"{best['candidate_win_rate']:.2%}")
        print("平均棋子优势：", f"{best['avg_score_diff']:.2f}")

    return overall


def print_phase_ranking(summaries, phase):
    selected = [summary for summary in summaries if summary["phase"] == phase]

    selected.sort(
        key=lambda item: (item["match_point_rate"], item["avg_score_diff"]),
        reverse=True
    )

    print()
    print("=" * 75)
    print(f"{phase.upper()} PHASE RANKING")
    print("=" * 75)

    for rank, summary in enumerate(selected, start=1):
        print(
            f"{rank}. {summary['profile']:<24} "
            f"points={summary['match_point_rate']:.3f}  "
            f"score_diff={summary['avg_score_diff']:.2f}"
        )


def main():
    # 第二轮采用更深的搜索和新的随机种子，避免重复使用第一轮测试局面
    depth = 4
    positions_per_phase = 3
    base_seed = 12026

    print("=" * 75)
    print("Dynamic Evaluation Weight Tuning - Round 2")
    print("=" * 75)
    print("搜索深度：", depth)
    print("每阶段局面数：", positions_per_phase)
    print("候选参数：", ", ".join(ROUND2_PROFILE_NAMES))
    print()

    print("正在生成第二轮未见测试局面……")
    positions = generate_positions(positions_per_phase, base_seed)

    print("生成完成：", len(positions), "个局面。")
    print()
    print("每个候选方案比赛局数：", len(positions) * 2)
    print("第二轮总比赛局数：", len(positions) * 2 * len(ROUND2_PROFILE_NAMES))

    all_records = []
    all_summaries = []

    # 所有候选方案使用同一批测试局面
    for profile_index, profile_name in enumerate(ROUND2_PROFILE_NAMES, start=1):
        print()
        print("=" * 75)
        print(f"[{profile_index}/{len(ROUND2_PROFILE_NAMES)}] {profile_name}")
        print("=" * 75)

        weights = CANDIDATE_PROFILES[profile_name]
        records = evaluate_profile(profile_name, weights, positions, depth)
        all_records.extend(records)

        for phase in ("opening", "midgame", "endgame", "overall"):
            summary = summarize_profile(records, profile_name, phase)

            if summary is None:
                continue

            all_summaries.append(summary)
            print_phase_summary(summary)

    for phase in ("opening", "midgame", "endgame"):
        print_phase_ranking(all_summaries, phase)

    print_ranking(all_summaries)

    save_game_records(all_records)
    save_summaries(all_summaries)

    print()
    print("逐局结果：")
    print(GAME_CSV)
    print()
    print("汇总结果：")
    print(SUMMARY_CSV)


if __name__ == "__main__":
    main()
