
import csv
import os
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties


BASE_DIR = Path(__file__).parent
SEARCH_CSV = BASE_DIR / "final_search_efficiency.csv"
TOURNAMENT_CSV = BASE_DIR / "final_tournament_summary.csv"
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


FONT_SMALL = get_chinese_font(10)
FONT_NORMAL = get_chinese_font(12)
FONT_TITLE = get_chinese_font(15, bold=True)


def read_csv(path):
    if not path.exists():
        raise FileNotFoundError(f"找不到实验数据：{path}")

    with open(path, "r", newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def save_figure(filename):
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    output_path = FIGURE_DIR / filename

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()

    print("已生成：", output_path)


def plot_search_nodes(rows):
    depths = [int(row["depth"]) for row in rows]
    minimax_nodes = [float(row["minimax_nodes"]) for row in rows]
    alphabeta_nodes = [float(row["alphabeta_nodes"]) for row in rows]

    plt.figure(figsize=(8, 5))
    plt.plot(depths, minimax_nodes, marker="o", linewidth=2, label="Minimax")
    plt.plot(depths, alphabeta_nodes, marker="o", linewidth=2, label="Alpha-Beta")

    plt.xlabel("搜索深度", fontproperties=FONT_NORMAL)
    plt.ylabel("平均搜索节点数", fontproperties=FONT_NORMAL)
    plt.title("Minimax 与 Alpha-Beta 搜索节点数对比", fontproperties=FONT_TITLE)

    plt.xticks(depths)
    plt.grid(alpha=0.3)
    plt.legend()

    save_figure("09_final_search_nodes.png")


def plot_search_time(rows):
    depths = [int(row["depth"]) for row in rows]
    minimax_times = [float(row["minimax_avg_time"]) for row in rows]
    alphabeta_times = [float(row["alphabeta_avg_time"]) for row in rows]

    plt.figure(figsize=(8, 5))
    plt.plot(depths, minimax_times, marker="o", linewidth=2, label="Minimax")
    plt.plot(depths, alphabeta_times, marker="o", linewidth=2, label="Alpha-Beta")

    plt.xlabel("搜索深度", fontproperties=FONT_NORMAL)
    plt.ylabel("平均单步搜索时间 / s", fontproperties=FONT_NORMAL)
    plt.title("Minimax 与 Alpha-Beta 搜索时间对比", fontproperties=FONT_TITLE)

    plt.xticks(depths)
    plt.grid(alpha=0.3)
    plt.legend()

    save_figure("10_final_search_time.png")


def plot_node_reduction(rows):
    depths = [str(row["depth"]) for row in rows]
    reductions = [float(row["node_reduction_percent"]) for row in rows]

    plt.figure(figsize=(8, 5))
    bars = plt.bar(depths, reductions)

    plt.xlabel("搜索深度", fontproperties=FONT_NORMAL)
    plt.ylabel("搜索节点削减比例 / %", fontproperties=FONT_NORMAL)
    plt.title("Alpha-Beta 相对 Minimax 的搜索节点削减比例", fontproperties=FONT_TITLE)
    plt.grid(axis="y", alpha=0.3)

    for bar, value in zip(bars, reductions):
        plt.text(
            bar.get_x() + bar.get_width() / 2, value + 1,
            f"{value:.1f}%", ha="center", va="bottom", fontsize=10
        )

    save_figure("11_alphabeta_node_reduction.png")


def plot_time_reduction(rows):
    depths = [str(row["depth"]) for row in rows]
    reductions = [float(row["time_reduction_percent"]) for row in rows]

    plt.figure(figsize=(8, 5))
    bars = plt.bar(depths, reductions)
    plt.axhline(0, linewidth=1)

    plt.xlabel("搜索深度", fontproperties=FONT_NORMAL)
    plt.ylabel("搜索时间削减比例 / %", fontproperties=FONT_NORMAL)
    plt.title("Alpha-Beta 相对 Minimax 的搜索时间变化", fontproperties=FONT_TITLE)
    plt.grid(axis="y", alpha=0.3)

    for bar, value in zip(bars, reductions):
        if value >= 0:
            y = value + 1
            va = "bottom"
        else:
            y = value - 1
            va = "top"

        plt.text(
            bar.get_x() + bar.get_width() / 2, y,
            f"{value:.1f}%", ha="center", va=va, fontsize=10
        )

    save_figure("12_alphabeta_time_reduction.png")


def plot_tournament_win_rate(rows):
    labels = []
    a_rates = []
    b_rates = []
    a_names = []
    b_names = []

    for row in rows:
        algorithm_a = row["algorithm_a"]
        algorithm_b = row["algorithm_b"]

        labels.append(f"{algorithm_a}\nvs\n{algorithm_b}")
        a_names.append(algorithm_a)
        b_names.append(algorithm_b)
        a_rates.append(float(row["a_win_rate"]) * 100)
        b_rates.append(float(row["b_win_rate"]) * 100)

    x = list(range(len(labels)))
    width = 0.34

    plt.figure(figsize=(9, 5.5))

    bars_a = plt.bar(
        [value - width / 2 for value in x],
        a_rates, width=width, label="算法 A"
    )
    bars_b = plt.bar(
        [value + width / 2 for value in x],
        b_rates, width=width, label="算法 B"
    )

    plt.xticks(x, labels)
    plt.ylabel("胜率 / %", fontproperties=FONT_NORMAL)
    plt.title("Minimax、Alpha-Beta 与 MCTS 两两对战胜率", fontproperties=FONT_TITLE)
    plt.ylim(0, 100)
    plt.grid(axis="y", alpha=0.3)
    plt.legend(prop=FONT_NORMAL)

    for index, bar in enumerate(bars_a):
        value = bar.get_height()

        plt.text(
            bar.get_x() + bar.get_width() / 2, value + 1.5,
            f"{a_names[index]}\n{value:.1f}%",
            ha="center", va="bottom", fontsize=8
        )

    for index, bar in enumerate(bars_b):
        value = bar.get_height()

        plt.text(
            bar.get_x() + bar.get_width() / 2, value + 1.5,
            f"{b_names[index]}\n{value:.1f}%",
            ha="center", va="bottom", fontsize=8
        )

    save_figure("13_final_tournament_win_rate.png")


def plot_tournament_score_difference(rows):
    labels = []
    differences = []

    for row in rows:
        algorithm_a = row["algorithm_a"]
        algorithm_b = row["algorithm_b"]

        labels.append(f"{algorithm_a}\nvs\n{algorithm_b}")
        differences.append(float(row["a_avg_score_diff"]))

    plt.figure(figsize=(9, 5.5))
    bars = plt.bar(labels, differences)
    plt.axhline(0, linewidth=1)

    plt.ylabel("算法 A 的平均棋子差", fontproperties=FONT_NORMAL)
    plt.title("三组算法对战的平均终局棋子差", fontproperties=FONT_TITLE)
    plt.grid(axis="y", alpha=0.3)

    for bar, value in zip(bars, differences):
        if value >= 0:
            y = value + 0.3
            va = "bottom"
        else:
            y = value - 0.3
            va = "top"

        plt.text(
            bar.get_x() + bar.get_width() / 2, y,
            f"{value:+.2f}", ha="center", va=va, fontsize=10
        )

    save_figure("14_final_tournament_score_diff.png")


def print_search_summary(rows):
    print()
    print("=" * 105)
    print("FINAL SEARCH EFFICIENCY SUMMARY")
    print("=" * 105)

    print(
        f"{'Depth':<8}{'SameMove':<12}{'MinimaxNodes':<16}"
        f"{'ABNodes':<16}{'NodeReduce':<15}"
        f"{'MinimaxTime':<15}{'ABTime':<15}"
    )
    print("-" * 105)

    for row in rows:
        print(
            f"{row['depth']:<8}"
            f"{row['same_move']:<12}"
            f"{float(row['minimax_nodes']):<16.0f}"
            f"{float(row['alphabeta_nodes']):<16.0f}"
            f"{float(row['node_reduction_percent']):<14.2f}%"
            f"{float(row['minimax_avg_time']):<15.4f}"
            f"{float(row['alphabeta_avg_time']):<15.4f}"
        )

    print("=" * 105)


def print_tournament_summary(rows):
    print()
    print("=" * 95)
    print("FINAL TOURNAMENT SUMMARY")
    print("=" * 95)

    for row in rows:
        print(f"{row['algorithm_a']} vs {row['algorithm_b']}")

        print(
            f"  胜负：{row['a_wins']} - {row['b_wins']}，"
            f"平局 {row['draws']}"
        )
        print(
            f"  胜率：{float(row['a_win_rate']):.2%} - "
            f"{float(row['b_win_rate']):.2%}"
        )
        print(
            f"  平均比分：{float(row['a_avg_score']):.2f} - "
            f"{float(row['b_avg_score']):.2f}"
        )
        print(f"  A 平均棋子差：{float(row['a_avg_score_diff']):+.2f}")
        print(
            f"  平均决策总时间：{float(row['a_avg_time']):.4f}s - "
            f"{float(row['b_avg_time']):.4f}s"
        )
        print()


def main():
    search_rows = read_csv(SEARCH_CSV)
    tournament_rows = read_csv(TOURNAMENT_CSV)

    FIGURE_DIR.mkdir(parents=True, exist_ok=True)

    print_search_summary(search_rows)
    print_tournament_summary(tournament_rows)

    print()
    print("开始生成正式算法实验图表……")

    plot_search_nodes(search_rows)
    plot_search_time(search_rows)
    plot_node_reduction(search_rows)
    plot_time_reduction(search_rows)
    plot_tournament_win_rate(tournament_rows)
    plot_tournament_score_difference(tournament_rows)

    print()
    print("正式算法实验图表生成完成。")
    print("输出目录：", FIGURE_DIR)


if __name__ == "__main__":
    main()
