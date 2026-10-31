
import csv
import os
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties


BASE_DIR = Path(__file__).parent
FIGURE_DIR = BASE_DIR / "figures"

SEARCH_CSV = BASE_DIR / "search_comparison.csv"
TOURNAMENT_CSV = BASE_DIR / "tournament_summary.csv"
EVALUATION_CSV = BASE_DIR / "evaluation_position_summary.csv"


def get_chinese_font(size=12, bold=False):
    """使用 Windows 字体文件，避免 matplotlib 中文字体匹配问题。"""
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
    with open(path, "r", newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def save_figure(filename):
    output_path = FIGURE_DIR / filename

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()

    print("已生成：", output_path)


def plot_search_nodes():
    if not SEARCH_CSV.exists():
        print("跳过搜索节点图：", SEARCH_CSV, "不存在")
        return

    rows = read_csv(SEARCH_CSV)

    minimax_depths = []
    minimax_nodes = []
    alphabeta_depths = []
    alphabeta_nodes = []

    for row in rows:
        algorithm = row["algorithm"]
        depth = int(row["depth"])
        nodes = int(row["nodes"])

        if algorithm == "Minimax":
            minimax_depths.append(depth)
            minimax_nodes.append(nodes)
        elif algorithm == "Alpha-Beta":
            alphabeta_depths.append(depth)
            alphabeta_nodes.append(nodes)

    plt.figure(figsize=(7.5, 5))
    plt.plot(minimax_depths, minimax_nodes, marker="o", label="Minimax")
    plt.plot(alphabeta_depths, alphabeta_nodes, marker="o", label="Alpha-Beta")

    plt.xlabel("搜索深度", fontproperties=FONT_NORMAL)
    plt.ylabel("搜索节点数", fontproperties=FONT_NORMAL)
    plt.title("Minimax 与 Alpha-Beta 搜索节点数对比", fontproperties=FONT_TITLE)

    plt.xticks(sorted(set(minimax_depths + alphabeta_depths)))
    plt.grid(alpha=0.3)
    plt.legend()

    save_figure("01_search_nodes.png")


def plot_search_time():
    if not SEARCH_CSV.exists():
        print("跳过搜索时间图：", SEARCH_CSV, "不存在")
        return

    rows = read_csv(SEARCH_CSV)

    minimax_depths = []
    minimax_times = []
    alphabeta_depths = []
    alphabeta_times = []

    for row in rows:
        algorithm = row["algorithm"]
        depth = int(row["depth"])
        move_time = float(row["time"])

        if algorithm == "Minimax":
            minimax_depths.append(depth)
            minimax_times.append(move_time)
        elif algorithm == "Alpha-Beta":
            alphabeta_depths.append(depth)
            alphabeta_times.append(move_time)

    plt.figure(figsize=(7.5, 5))
    plt.plot(minimax_depths, minimax_times, marker="o", label="Minimax")
    plt.plot(alphabeta_depths, alphabeta_times, marker="o", label="Alpha-Beta")

    plt.xlabel("搜索深度", fontproperties=FONT_NORMAL)
    plt.ylabel("单步搜索时间 / s", fontproperties=FONT_NORMAL)
    plt.title("Minimax 与 Alpha-Beta 搜索时间对比", fontproperties=FONT_TITLE)

    plt.xticks(sorted(set(minimax_depths + alphabeta_depths)))
    plt.grid(alpha=0.3)
    plt.legend()

    save_figure("02_search_time.png")


def plot_tournament_win_rate():
    if not TOURNAMENT_CSV.exists():
        print("跳过三算法胜率图：", TOURNAMENT_CSV, "不存在")
        return

    rows = read_csv(TOURNAMENT_CSV)

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
    width = 0.35

    plt.figure(figsize=(9, 5.5))

    bars_a = plt.bar(
        [value - width / 2 for value in x],
        a_rates, width=width, label="Algorithm A"
    )
    bars_b = plt.bar(
        [value + width / 2 for value in x],
        b_rates, width=width, label="Algorithm B"
    )

    plt.xticks(x, labels)
    plt.ylabel("胜率 / %", fontproperties=FONT_NORMAL)
    plt.title("三种搜索算法系列赛胜率对比", fontproperties=FONT_TITLE)

    plt.ylim(0, 100)
    plt.grid(axis="y", alpha=0.3)
    plt.legend()

    for index, bar in enumerate(bars_a):
        height = bar.get_height()

        plt.text(
            bar.get_x() + bar.get_width() / 2, height + 1,
            f"{a_names[index]}\n{height:.1f}%",
            ha="center", va="bottom", fontsize=8
        )

    for index, bar in enumerate(bars_b):
        height = bar.get_height()

        plt.text(
            bar.get_x() + bar.get_width() / 2, height + 1,
            f"{b_names[index]}\n{height:.1f}%",
            ha="center", va="bottom", fontsize=8
        )

    save_figure("03_tournament_win_rate.png")


def plot_dynamic_win_rate():
    if not EVALUATION_CSV.exists():
        print("跳过动态评价胜率图：", EVALUATION_CSV, "不存在")
        return

    rows = read_csv(EVALUATION_CSV)

    phase_order = ["opening", "midgame", "endgame", "overall"]
    phase_names = {
        "opening": "开局",
        "midgame": "中局",
        "endgame": "残局",
        "overall": "总体",
    }

    row_map = {row["phase"]: row for row in rows}

    phases = []
    fixed_rates = []
    dynamic_rates = []

    for phase in phase_order:
        if phase not in row_map:
            continue

        row = row_map[phase]
        phases.append(phase_names[phase])
        fixed_rates.append(float(row["fixed_win_rate"]) * 100)
        dynamic_rates.append(float(row["dynamic_win_rate"]) * 100)

    x = list(range(len(phases)))
    width = 0.36

    plt.figure(figsize=(8.5, 5.5))

    fixed_bars = plt.bar(
        [value - width / 2 for value in x],
        fixed_rates, width=width, label="Fixed"
    )
    dynamic_bars = plt.bar(
        [value + width / 2 for value in x],
        dynamic_rates, width=width, label="Dynamic"
    )

    plt.xticks(x, phases, fontproperties=FONT_NORMAL)
    plt.ylabel("胜率 / %", fontproperties=FONT_NORMAL)
    plt.title("固定评价与动态阶段评价的胜率对比", fontproperties=FONT_TITLE)

    plt.ylim(0, 100)
    plt.grid(axis="y", alpha=0.3)
    plt.legend()

    for bar in list(fixed_bars) + list(dynamic_bars):
        height = bar.get_height()

        plt.text(
            bar.get_x() + bar.get_width() / 2, height + 1,
            f"{height:.1f}%", ha="center", va="bottom", fontsize=9
        )

    save_figure("04_dynamic_win_rate_by_phase.png")


def plot_dynamic_score_difference():
    if not EVALUATION_CSV.exists():
        print("跳过动态评价棋子差图：", EVALUATION_CSV, "不存在")
        return

    rows = read_csv(EVALUATION_CSV)

    phase_order = ["opening", "midgame", "endgame", "overall"]
    phase_names = {
        "opening": "开局",
        "midgame": "中局",
        "endgame": "残局",
        "overall": "总体",
    }

    row_map = {row["phase"]: row for row in rows}

    phases = []
    differences = []

    for phase in phase_order:
        if phase not in row_map:
            continue

        phases.append(phase_names[phase])
        differences.append(float(row_map[phase]["dynamic_avg_score_diff"]))

    plt.figure(figsize=(8, 5))
    bars = plt.bar(phases, differences)
    plt.axhline(y=0, linewidth=1)

    plt.xlabel("游戏阶段", fontproperties=FONT_NORMAL)
    plt.ylabel("Dynamic 平均棋子优势", fontproperties=FONT_NORMAL)
    plt.title("动态阶段评价相对固定评价的平均棋子优势", fontproperties=FONT_TITLE)

    plt.xticks(fontproperties=FONT_NORMAL)
    plt.grid(axis="y", alpha=0.3)

    for bar in bars:
        height = bar.get_height()

        if height >= 0:
            vertical = "bottom"
            y = height + 0.2
        else:
            vertical = "top"
            y = height - 0.2

        plt.text(
            bar.get_x() + bar.get_width() / 2, y,
            f"{height:.2f}", ha="center", va=vertical, fontsize=10
        )

    save_figure("05_dynamic_score_diff_by_phase.png")


def main():
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)

    print("开始生成实验图表……")
    print()

    plot_search_nodes()
    plot_search_time()
    plot_tournament_win_rate()
    plot_dynamic_win_rate()
    plot_dynamic_score_difference()

    print()
    print("图表生成完成。")
    print("输出目录：")
    print(FIGURE_DIR)


if __name__ == "__main__":
    main()
