
import csv
from pathlib import Path

from config import BLACK, EMPTY
from core.board import Board
from core.game import Game
from ai.minimax import MinimaxAI
from ai.alphabeta import AlphaBetaAI
from ai.mcts import MCTSAI
from ai.evaluation import evaluate_fixed
from utils.coordinates import position_to_notation


OUTPUT_DIR = Path(__file__).parent
SEARCH_CSV = OUTPUT_DIR / "final_search_efficiency.csv"
TOURNAMENT_GAME_CSV = OUTPUT_DIR / "final_tournament_games.csv"
TOURNAMENT_SUMMARY_CSV = OUTPUT_DIR / "final_tournament_summary.csv"

SEARCH_DEPTHS = [2, 3, 4, 5]
SEARCH_REPEATS = 3

TOURNAMENT_GAMES = 10
MINIMAX_DEPTH = 3
ALPHABETA_DEPTH = 3
MCTS_SIMULATIONS = 500
BASE_SEED = 52026

MOVE_TIME_LIMIT = 60.0


def create_ai(algorithm, seed=None):
    if algorithm == "Minimax":
        return MinimaxAI(depth=MINIMAX_DEPTH, evaluator=evaluate_fixed)

    if algorithm == "Alpha-Beta":
        return AlphaBetaAI(depth=ALPHABETA_DEPTH, evaluator=evaluate_fixed)

    if algorithm == "MCTS":
        return MCTSAI(simulations=MCTS_SIMULATIONS, random_seed=seed)

    raise ValueError(f"未知算法：{algorithm}")


def benchmark_single_search(ai_class, depth):
    """在相同初始棋盘上重复搜索，统计平均时间和节点数。"""
    board = Board()
    times = []
    nodes = []
    selected_move = None

    for _ in range(SEARCH_REPEATS):
        ai = ai_class(depth=depth, evaluator=evaluate_fixed)
        move = ai.choose_move(board, BLACK)

        if selected_move is None:
            selected_move = move
        elif move != selected_move:
            raise RuntimeError("确定性搜索算法在相同局面下返回了不同结果。")

        times.append(ai.move_time)
        nodes.append(ai.nodes_searched)

    avg_time = sum(times) / len(times)
    avg_nodes = sum(nodes) / len(nodes)

    return selected_move, avg_nodes, avg_time


def run_search_efficiency():
    """比较 Minimax 和 Alpha-Beta 在不同深度下的搜索效率。"""
    records = []

    print()
    print("=" * 90)
    print("PART 1 - Minimax vs Alpha-Beta Search Efficiency")
    print("=" * 90)

    for depth in SEARCH_DEPTHS:
        minimax_move, minimax_nodes, minimax_time = benchmark_single_search(MinimaxAI, depth)
        alphabeta_move, alphabeta_nodes, alphabeta_time = benchmark_single_search(AlphaBetaAI, depth)

        same_move = minimax_move == alphabeta_move

        if minimax_nodes > 0:
            node_reduction = (minimax_nodes - alphabeta_nodes) / minimax_nodes * 100
        else:
            node_reduction = 0.0

        if minimax_time > 0:
            time_reduction = (minimax_time - alphabeta_time) / minimax_time * 100
        else:
            time_reduction = 0.0

        minimax_notation = position_to_notation(*minimax_move) if minimax_move is not None else "PASS"
        alphabeta_notation = position_to_notation(*alphabeta_move) if alphabeta_move is not None else "PASS"

        record = {
            "depth": depth,
            "minimax_move": minimax_notation,
            "alphabeta_move": alphabeta_notation,
            "same_move": same_move,
            "minimax_nodes": minimax_nodes,
            "alphabeta_nodes": alphabeta_nodes,
            "node_reduction_percent": node_reduction,
            "minimax_avg_time": minimax_time,
            "alphabeta_avg_time": alphabeta_time,
            "time_reduction_percent": time_reduction,
        }

        records.append(record)

        print(
            f"Depth {depth} | "
            f"Move {minimax_notation}/{alphabeta_notation} | "
            f"Nodes {minimax_nodes:.0f} -> {alphabeta_nodes:.0f} | "
            f"Reduction {node_reduction:.2f}% | "
            f"Time {minimax_time:.4f}s -> {alphabeta_time:.4f}s"
        )

    return records


def save_search_records(records):
    fieldnames = [
        "depth", "minimax_move", "alphabeta_move", "same_move",
        "minimax_nodes", "alphabeta_nodes", "node_reduction_percent",
        "minimax_avg_time", "alphabeta_avg_time", "time_reduction_percent",
    ]

    with open(SEARCH_CSV, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)


def play_game(black_ai, white_ai):
    """执行完整对局，统计比分、时间、节点数和超时情况。"""
    game = Game()
    black_nodes = 0
    white_nodes = 0
    move_count = 0
    timeout_player = None

    while not game.game_over:
        current_player = game.current_player
        ai = black_ai if current_player == BLACK else white_ai

        move = ai.choose_move(game.board, current_player)

        if current_player == BLACK:
            black_nodes += ai.nodes_searched
        else:
            white_nodes += ai.nodes_searched

        # 单步思考超过 60 秒直接判负
        if ai.move_time > MOVE_TIME_LIMIT:
            game.declare_timeout(current_player)
            timeout_player = current_player
            break

        if move is None:
            raise RuntimeError(f"{ai.name} 未返回合法动作，但游戏尚未结束。")

        row, col = move
        success = game.play_move(row, col, move_time=ai.move_time)

        if not success:
            raise RuntimeError(f"{ai.name} 返回非法动作：{move}")

        move_count += 1

    black_score, white_score = game.board.count_pieces()

    return {
        "winner": game.get_winner(),
        "black_score": black_score,
        "white_score": white_score,
        "black_time": game.black_time,
        "white_time": game.white_time,
        "black_nodes": black_nodes,
        "white_nodes": white_nodes,
        "moves": move_count,
        "end_reason": game.end_reason,
        "timeout_player": timeout_player,
    }


def run_matchup(algorithm_a, algorithm_b, games, seed_offset):
    """两种算法进行多局比赛，交替交换黑白棋。"""
    records = []

    a_wins = 0
    b_wins = 0
    draws = 0

    a_total_score = 0
    b_total_score = 0
    a_total_time = 0.0
    b_total_time = 0.0
    a_total_nodes = 0
    b_total_nodes = 0

    print()
    print("-" * 90)
    print(f"{algorithm_a} vs {algorithm_b}")
    print("-" * 90)

    for game_index in range(games):
        seed_a = BASE_SEED + seed_offset + game_index * 2
        seed_b = BASE_SEED + seed_offset + game_index * 2 + 1

        ai_a = create_ai(algorithm_a, seed=seed_a)
        ai_b = create_ai(algorithm_b, seed=seed_b)

        # 每局交换颜色，MCTS 使用不同随机种子
        if game_index % 2 == 0:
            black_ai = ai_a
            white_ai = ai_b
            a_color = BLACK
        else:
            black_ai = ai_b
            white_ai = ai_a
            a_color = -BLACK

        result = play_game(black_ai, white_ai)

        # 将黑白棋数据转换为算法 A/B 视角
        if a_color == BLACK:
            a_score = result["black_score"]
            b_score = result["white_score"]
            a_time = result["black_time"]
            b_time = result["white_time"]
            a_nodes = result["black_nodes"]
            b_nodes = result["white_nodes"]
            a_color_name = "Black"
        else:
            a_score = result["white_score"]
            b_score = result["black_score"]
            a_time = result["white_time"]
            b_time = result["black_time"]
            a_nodes = result["white_nodes"]
            b_nodes = result["black_nodes"]
            a_color_name = "White"

        winner = result["winner"]

        if winner == EMPTY:
            winner_name = "Draw"
            draws += 1
        elif winner == a_color:
            winner_name = algorithm_a
            a_wins += 1
        else:
            winner_name = algorithm_b
            b_wins += 1

        a_total_score += a_score
        b_total_score += b_score
        a_total_time += a_time
        b_total_time += b_time
        a_total_nodes += a_nodes
        b_total_nodes += b_nodes

        record = {
            "matchup": f"{algorithm_a} vs {algorithm_b}",
            "game": game_index + 1,
            "algorithm_a": algorithm_a,
            "algorithm_b": algorithm_b,
            "a_color": a_color_name,
            "a_seed": seed_a,
            "b_seed": seed_b,
            "winner": winner_name,
            "a_score": a_score,
            "b_score": b_score,
            "score_diff_a": a_score - b_score,
            "a_time": a_time,
            "b_time": b_time,
            "a_nodes": a_nodes,
            "b_nodes": b_nodes,
            "moves": result["moves"],
            "end_reason": result["end_reason"],
        }

        records.append(record)

        print(
            f"Game {game_index + 1:02d}/{games} | "
            f"A={a_color_name:<5} | "
            f"{a_score:02d}:{b_score:02d} | "
            f"Winner={winner_name}"
        )

    summary = {
        "algorithm_a": algorithm_a,
        "algorithm_b": algorithm_b,
        "games": games,
        "a_wins": a_wins,
        "b_wins": b_wins,
        "draws": draws,
        "a_win_rate": a_wins / games,
        "b_win_rate": b_wins / games,
        "draw_rate": draws / games,
        "a_avg_score": a_total_score / games,
        "b_avg_score": b_total_score / games,
        "a_avg_score_diff": (a_total_score - b_total_score) / games,
        "a_avg_time": a_total_time / games,
        "b_avg_time": b_total_time / games,
        "a_avg_nodes": a_total_nodes / games,
        "b_avg_nodes": b_total_nodes / games,
    }

    return records, summary


def run_tournament():
    """三种算法两两对战。"""
    print()
    print("=" * 90)
    print("PART 2 - Algorithm Tournament")
    print("=" * 90)
    print("Minimax depth:", MINIMAX_DEPTH)
    print("Alpha-Beta depth:", ALPHABETA_DEPTH)
    print("MCTS simulations:", MCTS_SIMULATIONS)
    print("Games per matchup:", TOURNAMENT_GAMES)

    all_records = []
    summaries = []

    matchups = [
        ("Minimax", "Alpha-Beta", 0),
        ("Minimax", "MCTS", 10000),
        ("Alpha-Beta", "MCTS", 20000),
    ]

    for algorithm_a, algorithm_b, seed_offset in matchups:
        records, summary = run_matchup(
            algorithm_a, algorithm_b, TOURNAMENT_GAMES, seed_offset
        )

        all_records.extend(records)
        summaries.append(summary)

    return all_records, summaries


def save_tournament_games(records):
    fieldnames = [
        "matchup", "game", "algorithm_a", "algorithm_b",
        "a_color", "a_seed", "b_seed", "winner",
        "a_score", "b_score", "score_diff_a",
        "a_time", "b_time", "a_nodes", "b_nodes",
        "moves", "end_reason",
    ]

    with open(TOURNAMENT_GAME_CSV, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)


def save_tournament_summary(summaries):
    fieldnames = [
        "algorithm_a", "algorithm_b", "games",
        "a_wins", "b_wins", "draws",
        "a_win_rate", "b_win_rate", "draw_rate",
        "a_avg_score", "b_avg_score", "a_avg_score_diff",
        "a_avg_time", "b_avg_time", "a_avg_nodes", "b_avg_nodes",
    ]

    with open(TOURNAMENT_SUMMARY_CSV, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(summaries)


def print_tournament_summary(summaries):
    print()
    print("=" * 100)
    print("FINAL TOURNAMENT SUMMARY")
    print("=" * 100)

    for summary in summaries:
        print(f"{summary['algorithm_a']} vs {summary['algorithm_b']}")

        print(
            f"  Wins: {summary['a_wins']} - {summary['b_wins']} "
            f"(Draws {summary['draws']})"
        )

        print(
            f"  Win rate: {summary['a_win_rate']:.2%} - "
            f"{summary['b_win_rate']:.2%}"
        )

        print(
            f"  Avg score: {summary['a_avg_score']:.2f} - "
            f"{summary['b_avg_score']:.2f}"
        )

        print(
            f"  Avg time: {summary['a_avg_time']:.4f}s - "
            f"{summary['b_avg_time']:.4f}s"
        )

        print(
            f"  Avg nodes: {summary['a_avg_nodes']:.1f} - "
            f"{summary['b_avg_nodes']:.1f}"
        )

        print()


def main():
    print("=" * 100)
    print("REVERSI FINAL ALGORITHM BENCHMARK")
    print("=" * 100)

    # Minimax 与 Alpha-Beta 搜索效率实验
    search_records = run_search_efficiency()
    save_search_records(search_records)

    # 三种算法两两对战
    tournament_records, tournament_summaries = run_tournament()

    save_tournament_games(tournament_records)
    save_tournament_summary(tournament_summaries)
    print_tournament_summary(tournament_summaries)

    print("=" * 100)
    print("正式实验完成")
    print("=" * 100)

    print()
    print("搜索效率数据：")
    print(SEARCH_CSV)

    print()
    print("逐局比赛数据：")
    print(TOURNAMENT_GAME_CSV)

    print()
    print("比赛汇总数据：")
    print(TOURNAMENT_SUMMARY_CSV)


if __name__ == "__main__":
    main()
