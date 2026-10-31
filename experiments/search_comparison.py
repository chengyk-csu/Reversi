
import csv
from pathlib import Path

from config import BLACK
from core.board import Board
from ai.minimax import MinimaxAI
from ai.alphabeta import AlphaBetaAI
from utils.coordinates import position_to_notation


def run_comparison():
    board = Board()
    depths = [2, 3, 4, 5]
    results = []

    print("=" * 75)
    print(
        f"{'Algorithm':<15}{'Depth':<10}{'Move':<10}"
        f"{'Nodes':<15}{'Time(s)':<15}"
    )
    print("=" * 75)

    for depth in depths:
        minimax = MinimaxAI(depth=depth)
        move = minimax.choose_move(board, BLACK)
        move_name = position_to_notation(*move) if move is not None else "None"

        print(
            f"{'Minimax':<15}{depth:<10}{move_name:<10}"
            f"{minimax.nodes_searched:<15}{minimax.move_time:<15.6f}"
        )

        results.append({
            "algorithm": "Minimax",
            "depth": depth,
            "move": move_name,
            "nodes": minimax.nodes_searched,
            "time": minimax.move_time,
        })

        alphabeta = AlphaBetaAI(depth=depth)
        move = alphabeta.choose_move(board, BLACK)
        move_name = position_to_notation(*move) if move is not None else "None"

        print(
            f"{'Alpha-Beta':<15}{depth:<10}{move_name:<10}"
            f"{alphabeta.nodes_searched:<15}{alphabeta.move_time:<15.6f}"
        )

        results.append({
            "algorithm": "Alpha-Beta",
            "depth": depth,
            "move": move_name,
            "nodes": alphabeta.nodes_searched,
            "time": alphabeta.move_time,
        })

        print("-" * 75)

    output_file = Path(__file__).parent / "search_comparison.csv"

    with open(output_file, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file, fieldnames=["algorithm", "depth", "move", "nodes", "time"]
        )
        writer.writeheader()
        writer.writerows(results)

    print()
    print("实验结果已保存到：", output_file)


if __name__ == "__main__":
    run_comparison()
