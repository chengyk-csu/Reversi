
import csv
import os
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties


BASE_DIR = Path(__file__).parent
INPUT_CSV = BASE_DIR / "final_dynamic_validation_summary.csv"
FIGURE_DIR = BASE_DIR / "figures"


def get_chinese_font(size=12, bold=False):
    windows_dir = Path(os.environ.get("WINDIR", r"C:\Windows"))
    font_dir = windows_dir / "Fonts"

    if bold:
        candidates = ["msyhbd.ttc", "msyh.ttc", "simhei.ttf"]
    else:
        candidates = ["msyh.ttc", "msyhl.ttc", "simhei.ttf", "simsun.ttc"]

    for font_name in candidates:
        font_path = font_dir / font_name

        if font_path.exists():
            return FontProperties(fname=str(font_path), size=size)

    return FontProperties(size=size)


FONT_NORMAL = get_chinese_font(12)
FONT_TITLE = get_chinese_font(15, bold=True)


def read_summary():
    if not INPUT_CSV.exists():
        raise FileNotFoundError(f"找不到实验结果：{INPUT_CSV}")

    with open(INPUT_CSV, "r", newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def save_figure(filename):
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    output_path = FIGURE_DIR / filename

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()

    print("已生成：", output_path)


def plot_match_point_rate(rows):
    phase_names = {
        "opening": "开局",
        "midgame": "中局",
        "endgame": "残局",
        "overall": "总体",
    }

    order = ["opening", "midgame", "endgame", "overall"]
    row_map = {row["phase"]: row for row in rows}

    phases = []
    rates = []

    for phase in order:
        if phase not in row_map:
            continue

        phases.append(phase_names[phase])
        rates.append(float(row_map[phase]["match_point_rate"]) * 100)

    plt.figure(figsize=(8, 5))
    bars = plt.bar(phases, rates)

    plt.axhline(50, linewidth=1, linestyle="--", label="Fixed 基准 50%")
    plt.ylim(0, 100)

    plt.ylabel("比赛积分率 / %", fontproperties=FONT_NORMAL)
    plt.xlabel("游戏阶段", fontproperties=FONT_NORMAL)
    plt.title("动态阶段评价函数在不同阶段的比赛积分率", fontproperties=FONT_TITLE)

    plt.xticks(fontproperties=FONT_NORMAL)
    plt.grid(axis="y", alpha=0.3)
    plt.legend(prop=FONT_NORMAL)

    for bar, rate in zip(bars, rates):
        plt.text(
            bar.get_x() + bar.get_width() / 2, rate + 1.5,
            f"{rate:.1f}%", ha="center", va="bottom", fontsize=10
        )

    save_figure("06_final_dynamic_match_point_rate.png")


def plot_score_difference(rows):
    phase_names = {
        "opening": "开局",
        "midgame": "中局",
        "endgame": "残局",
        "overall": "总体",
    }

    order = ["opening", "midgame", "endgame", "overall"]
    row_map = {row["phase"]: row for row in rows}

    phases = []
    differences = []

    for phase in order:
        if phase not in row_map:
            continue

        phases.append(phase_names[phase])
        differences.append(float(row_map[phase]["avg_score_diff"]))

    plt.figure(figsize=(8, 5))
    bars = plt.bar(phases, differences)
    plt.axhline(0, linewidth=1)

    plt.ylabel("Dynamic 相对 Fixed 的平均棋子差", fontproperties=FONT_NORMAL)
    plt.xlabel("游戏阶段", fontproperties=FONT_NORMAL)
    plt.title("动态阶段评价函数的平均终局棋子优势", fontproperties=FONT_TITLE)

    plt.xticks(fontproperties=FONT_NORMAL)
    plt.grid(axis="y", alpha=0.3)

    for bar, difference in zip(bars, differences):
        if difference >= 0:
            y = difference + 0.3
            vertical = "bottom"
        else:
            y = difference - 0.3
            vertical = "top"

        plt.text(
            bar.get_x() + bar.get_width() / 2, y,
            f"{difference:+.2f}", ha="center", va=vertical, fontsize=10
        )

    save_figure("07_final_dynamic_score_difference.png")


def plot_final_record(rows):
    overall = None

    for row in rows:
        if row["phase"] == "overall":
            overall = row
            break

    if overall is None:
        raise RuntimeError("CSV 中没有 overall 数据")

    dynamic_wins = int(overall["candidate_wins"])
    fixed_wins = int(overall["fixed_wins"])
    draws = int(overall["draws"])

    labels = ["Dynamic 获胜", "平局", "Fixed 获胜"]
    values = [dynamic_wins, draws, fixed_wins]

    plt.figure(figsize=(7.5, 5))
    bars = plt.bar(labels, values)

    plt.ylabel("对局数量", fontproperties=FONT_NORMAL)
    plt.title("最终独立验证集胜负结果", fontproperties=FONT_TITLE)

    plt.xticks(fontproperties=FONT_NORMAL)
    plt.grid(axis="y", alpha=0.3)

    for bar, value in zip(bars, values):
        plt.text(
            bar.get_x() + bar.get_width() / 2, value + 0.4,
            str(value), ha="center", va="bottom", fontsize=11
        )

    save_figure("08_final_dynamic_record.png")


def print_overall_result(rows):
    overall = None

    for row in rows:
        if row["phase"] == "overall":
            overall = row
            break

    if overall is None:
        return

    print()
    print("=" * 70)
    print("Final Dynamic Evaluation Result")
    print("=" * 70)

    print("Games:", overall["games"])
    print("Dynamic wins:", overall["candidate_wins"])
    print("Draws:", overall["draws"])
    print("Fixed wins:", overall["fixed_wins"])
    print()

    print("Dynamic win rate:", f"{float(overall['candidate_win_rate']):.2%}")
    print("Match point rate:", f"{float(overall['match_point_rate']):.2%}")
    print("Average score difference:", f"{float(overall['avg_score_diff']):+.2f}")
    print("=" * 70)


def main():
    rows = read_summary()
    print_overall_result(rows)

    print()
    print("开始生成最终验证图表……")

    plot_match_point_rate(rows)
    plot_score_difference(rows)
    plot_final_record(rows)

    print()
    print("最终验证图表生成完成。")
    print("输出目录：", FIGURE_DIR)


if __name__ == "__main__":
    main()
