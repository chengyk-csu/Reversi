
import csv
from pathlib import Path

from config import BLACK, WHITE
from core.game import Game
from ai.alphabeta import AlphaBetaAI
from ai.evaluation import evaluate_fixed, evaluate_dynamic


OUTPUT_DIR = Path(__file__).parent
GAME_CSV = OUTPUT_DIR / "evaluation_comparison_games.csv"
SUMMARY_CSV = OUTPUT_DIR / "evaluation_comparison_summary.csv"


def play_game(black_ai, white_ai):
    game = Game()
    move_count = 0

    while not game.game_over:
        current_player = game.current_player
        ai = black_ai if current_player == BLACK else white_ai

        move = ai.choose_move(game.board, current_player)

        if move is None:
            raise RuntimeError(f"{ai.name} 没有返回合法动作，但当前游戏尚未结束。")

        row, col = move
        success = game.play_move(row, col, move_time=ai.move_time)

        if not success:
            raise RuntimeError(f"{ai.name} 返回了非法动作：{move}")

        move_count += 1

    black_score, white_score = game.board.count_pieces()

    return {
        "winner": game.get_winner(),
        "black_score": black_score,
        "white_score": white_score,
        "black_time": game.black_time,
        "white_time": game.white_time,
        "moves": move_count,
    }


def run_series(games, depth):
    """比较固定评价和动态评价，每局交替交换黑白棋。"""
    if games < 1:
        raise ValueError("比赛局数必须至少为 1")

    if depth < 1:
        raise ValueError("搜索深度必须至少为 1")

    game_records = []

    fixed_wins = 0
    dynamic_wins = 0
    draws = 0

    fixed_total_score = 0
    dynamic_total_score = 0
    fixed_total_time = 0.0
    dynamic_total_time = 0.0
    fixed_total_nodes = 0
    dynamic_total_nodes = 0

    for game_index in range(games):
        fixed_ai = AlphaBetaAI(depth=depth, evaluator=evaluate_fixed)
        dynamic_ai = AlphaBetaAI(depth=depth, evaluator=evaluate_dynamic)

        # 交替交换先后手
        if game_index % 2 == 0:
            black_ai = fixed_ai
            white_ai = dynamic_ai
            fixed_color = BLACK
        else:
            black_ai = dynamic_ai
            white_ai = fixed_ai
            fixed_color = WHITE

        game = Game()
        move_count = 0
        fixed_game_nodes = 0
        dynamic_game_nodes = 0

        while not game.game_over:
            current_player = game.current_player
            ai = black_ai if current_player == BLACK else white_ai

            move = ai.choose_move(game.board, current_player)

            if move is None:
                raise RuntimeError(f"{ai.name} 没有返回合法动作，但游戏尚未结束。")

            row, col = move

            # 累计整局搜索节点数
            if ai is fixed_ai:
                fixed_game_nodes += ai.nodes_searched
            else:
                dynamic_game_nodes += ai.nodes_searched

            success = game.play_move(row, col, move_time=ai.move_time)

            if not success:
                raise RuntimeError(f"{ai.name} 返回非法动作：{move}")

            move_count += 1

        black_score, white_score = game.board.count_pieces()

        if fixed_color == BLACK:
            fixed_score = black_score
            dynamic_score = white_score
            fixed_time = game.black_time
            dynamic_time = game.white_time
            fixed_color_name = "Black"
        else:
            fixed_score = white_score
            dynamic_score = black_score
            fixed_time = game.white_time
            dynamic_time = game.black_time
            fixed_color_name = "White"

        if fixed_score > dynamic_score:
            fixed_wins += 1
            winner = "Fixed"
        elif dynamic_score > fixed_score:
            dynamic_wins += 1
            winner = "Dynamic"
        else:
            draws += 1
            winner = "Draw"

        fixed_total_score += fixed_score
        dynamic_total_score += dynamic_score
        fixed_total_time += fixed_time
        dynamic_total_time += dynamic_time
        fixed_total_nodes += fixed_game_nodes
        dynamic_total_nodes += dynamic_game_nodes

        record = {
            "game": game_index + 1,
            "depth": depth,
            "fixed_color": fixed_color_name,
            "winner": winner,
            "fixed_score": fixed_score,
            "dynamic_score": dynamic_score,
            "score_diff_dynamic": dynamic_score - fixed_score,
            "fixed_time": fixed_time,
            "dynamic_time": dynamic_time,
            "fixed_nodes": fixed_game_nodes,
            "dynamic_nodes": dynamic_game_nodes,
            "moves": move_count,
        }

        game_records.append(record)

        print(
            f"Game {game_index + 1}/{games} | "
            f"Fixed={fixed_color_name:<5} | "
            f"Fixed {fixed_score:02d} : {dynamic_score:02d} Dynamic | "
            f"Winner={winner}"
        )

    summary = {
        "depth": depth,
        "games": games,
        "fixed_wins": fixed_wins,
        "dynamic_wins": dynamic_wins,
        "draws": draws,
        "fixed_win_rate": fixed_wins / games,
        "dynamic_win_rate": dynamic_wins / games,
        "draw_rate": draws / games,
        "fixed_avg_score": fixed_total_score / games,
        "dynamic_avg_score": dynamic_total_score / games,
        "dynamic_avg_score_diff": (dynamic_total_score - fixed_total_score) / games,
        "fixed_avg_time": fixed_total_time / games,
        "dynamic_avg_time": dynamic_total_time / games,
        "fixed_avg_nodes": fixed_total_nodes / games,
        "dynamic_avg_nodes": dynamic_total_nodes / games,
    }

    return game_records, summary


def save_game_records(records):
    fieldnames = [
        "game", "depth", "fixed_color", "winner",
        "fixed_score", "dynamic_score", "score_diff_dynamic",
        "fixed_time", "dynamic_time",
        "fixed_nodes", "dynamic_nodes", "moves",
    ]

    with open(GAME_CSV, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)


def save_summary(summary):
    fieldnames = [
        "depth", "games",
        "fixed_wins", "dynamic_wins", "draws",
        "fixed_win_rate", "dynamic_win_rate", "draw_rate",
        "fixed_avg_score", "dynamic_avg_score", "dynamic_avg_score_diff",
        "fixed_avg_time", "dynamic_avg_time",
        "fixed_avg_nodes", "dynamic_avg_nodes",
    ]

    with open(SUMMARY_CSV, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow(summary)


def print_summary(summary):
    print()
    print("=" * 65)
    print("Fixed Evaluation vs Dynamic Evaluation")
    print("=" * 65)
    print("搜索深度：", summary["depth"])
    print("比赛局数：", summary["games"])
    print()

    print("Fixed wins：", summary["fixed_wins"])
    print("Dynamic wins：", summary["dynamic_wins"])
    print("Draws：", summary["draws"])
    print()

    print(f"Fixed win rate：{summary['fixed_win_rate']:.2%}")
    print(f"Dynamic win rate：{summary['dynamic_win_rate']:.2%}")
    print(f"Draw rate：{summary['draw_rate']:.2%}")
    print()

    print(f"Fixed 平均得分：{summary['fixed_avg_score']:.2f}")
    print(f"Dynamic 平均得分：{summary['dynamic_avg_score']:.2f}")
    print(f"Dynamic 平均棋子优势：{summary['dynamic_avg_score_diff']:.2f}")
    print()

    print(f"Fixed 平均总决策时间：{summary['fixed_avg_time']:.6f}s")
    print(f"Dynamic 平均总决策时间：{summary['dynamic_avg_time']:.6f}s")
    print()

    print(f"Fixed 平均搜索节点：{summary['fixed_avg_nodes']:.2f}")
    print(f"Dynamic 平均搜索节点：{summary['dynamic_avg_nodes']:.2f}")
    print("=" * 65)


def main():
    games = 10
    depth = 4

    records, summary = run_series(games=games, depth=depth)

    save_game_records(records)
    save_summary(summary)
    print_summary(summary)

    print()
    print("逐局实验数据：")
    print(GAME_CSV)
    print()
    print("汇总实验数据：")
    print(SUMMARY_CSV)


if __name__ == "__main__":
    main()
