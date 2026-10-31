
import csv
from pathlib import Path

from config import BLACK
from core.board import Board
from ai.minimax import MinimaxAI
from ai.alphabeta import AlphaBetaAI
from ai.evaluation import evaluate_fixed
from utils.coordinates import position_to_notation


OUTPUT_DIR = Path(__file__).parent
OUTPUT_CSV = OUTPUT_DIR / "final_search_efficiency.csv"

SEARCH_DEPTHS = [2, 3, 4, 5]
SEARCH_REPEATS = 3


def benchmark_algorithm(ai_class, depth):
    """在相同初始局面下重复搜索，统计平均节点数和时间。"""
    board = Board()
    selected_move = None
    node_results = []
    time_results = []

    for repeat in range(SEARCH_REPEATS):
        ai = ai_class(depth=depth, evaluator=evaluate_fixed)
        move = ai.choose_move(board, BLACK)

        if selected_move is None:
            selected_move = move
        elif move != selected_move:
            raise RuntimeError("相同算法在相同棋盘和深度下产生了不同的确定性搜索结果。")

        node_results.append(ai.nodes_searched)
        time_results.append(ai.move_time)

        print(
            f"    Repeat {repeat + 1}/{SEARCH_REPEATS} | "
            f"nodes={ai.nodes_searched} | time={ai.move_time:.6f}s"
        )

    average_nodes = sum(node_results) / len(node_results)
    average_time = sum(time_results) / len(time_results)

    return selected_move, average_nodes, average_time


def run_experiment():
    records = []

    print("=" * 100)
    print("FINAL MINIMAX VS ALPHA-BETA SEARCH EFFICIENCY EXPERIMENT")
    print("=" * 100)
    print()

    for depth in SEARCH_DEPTHS:
        print("=" * 70)
        print(f"Depth = {depth}")
        print("=" * 70)

        print()
        print("Minimax:")
        minimax_move, minimax_nodes, minimax_time = benchmark_algorithm(MinimaxAI, depth)

        print()
        print("Alpha-Beta:")
        alphabeta_move, alphabeta_nodes, alphabeta_time = benchmark_algorithm(AlphaBetaAI, depth)

        minimax_notation = position_to_notation(*minimax_move) if minimax_move is not None else "PASS"
        alphabeta_notation = position_to_notation(*alphabeta_move) if alphabeta_move is not None else "PASS"

        same_move = minimax_move == alphabeta_move

        if minimax_nodes > 0:
            node_reduction_percent = (minimax_nodes - alphabeta_nodes) / minimax_nodes * 100
        else:
            node_reduction_percent = 0.0

        if minimax_time > 0:
            time_reduction_percent = (minimax_time - alphabeta_time) / minimax_time * 100
        else:
            time_reduction_percent = 0.0

        record = {
            "depth": depth,
            "minimax_move": minimax_notation,
            "alphabeta_move": alphabeta_notation,
            "same_move": same_move,
            "minimax_nodes": minimax_nodes,
            "alphabeta_nodes": alphabeta_nodes,
            "node_reduction_percent": node_reduction_percent,
            "minimax_avg_time": minimax_time,
            "alphabeta_avg_time": alphabeta_time,
            "time_reduction_percent": time_reduction_percent,
        }

        records.append(record)

        print()
        print(f"Move：{minimax_notation} / {alphabeta_notation}")
        print("Same move：", same_move)
        print("Minimax nodes：", f"{minimax_nodes:.0f}")
        print("Alpha-Beta nodes：", f"{alphabeta_nodes:.0f}")
        print("Node reduction：", f"{node_reduction_percent:.2f}%")
        print("Minimax time：", f"{minimax_time:.6f}s")
        print("Alpha-Beta time：", f"{alphabeta_time:.6f}s")
        print("Time reduction：", f"{time_reduction_percent:.2f}%")
        print()

    return records


def save_results(records):
    fieldnames = [
        "depth", "minimax_move", "alphabeta_move", "same_move",
        "minimax_nodes", "alphabeta_nodes", "node_reduction_percent",
        "minimax_avg_time", "alphabeta_avg_time", "time_reduction_percent",
    ]

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)


def print_final_summary(records):
    print()
    print("=" * 115)
    print("FINAL SEARCH EFFICIENCY SUMMARY")
    print("=" * 115)

    print(
        f"{'Depth':<8}{'Move':<10}{'Same':<8}"
        f"{'MinimaxNodes':<16}{'ABNodes':<14}{'NodeReduce':<15}"
        f"{'MinimaxTime':<16}{'ABTime':<16}{'TimeReduce':<14}"
    )
    print("-" * 115)

    for record in records:
        print(
            f"{record['depth']:<8}"
            f"{record['minimax_move']:<10}"
            f"{str(record['same_move']):<8}"
            f"{record['minimax_nodes']:<16.0f}"
            f"{record['alphabeta_nodes']:<14.0f}"
            f"{record['node_reduction_percent']:<14.2f}%"
            f"{record['minimax_avg_time']:<16.6f}"
            f"{record['alphabeta_avg_time']:<16.6f}"
            f"{record['time_reduction_percent']:<13.2f}%"
        )

    print("=" * 115)


def main():
    records = run_experiment()
    save_results(records)
    print_final_summary(records)

    print()
    print("结果已保存：")
    print(OUTPUT_CSV)


if __name__ == "__main__":
    main()
