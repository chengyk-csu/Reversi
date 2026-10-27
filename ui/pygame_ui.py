import os
import time
from pathlib import Path

import pygame

from config import (
    BOARD_SIZE,
    EMPTY,
    BLACK,
    WHITE,
)

from core.game import Game

from ai.minimax import MinimaxAI
from ai.alphabeta import AlphaBetaAI
from ai.mcts import MCTSAI

from ai.evaluation import (
    evaluate_fixed,
    evaluate_dynamic,
)

from utils.coordinates import (
    position_to_notation,
)


# ============================================================
# 窗口尺寸
# ============================================================

CELL_SIZE = 80

BOARD_PIXEL_SIZE = (
    BOARD_SIZE * CELL_SIZE
)

SIDE_PANEL_WIDTH = 380

WINDOW_WIDTH = (
    BOARD_PIXEL_SIZE
    + SIDE_PANEL_WIDTH
)

WINDOW_HEIGHT = BOARD_PIXEL_SIZE


# ============================================================
# 游戏参数
# ============================================================

MOVE_TIME_LIMIT = 60.0

MINIMAX_DEPTH = 4

ALPHABETA_DEPTH = 4

MCTS_SIMULATIONS = 500


# ============================================================
# 颜色
# ============================================================

BACKGROUND_COLOR = (
    235,
    235,
    235,
)

BOARD_COLOR = (
    34,
    139,
    34,
)

GRID_COLOR = (
    20,
    80,
    20,
)

BLACK_COLOR = (
    25,
    25,
    25,
)

WHITE_COLOR = (
    245,
    245,
    245,
)

WHITE_BORDER_COLOR = (
    80,
    80,
    80,
)

VALID_MOVE_COLOR = (
    255,
    215,
    0,
)

LAST_MOVE_COLOR = (
    220,
    60,
    60,
)

TEXT_COLOR = (
    35,
    35,
    35,
)

PANEL_COLOR = (
    245,
    245,
    245,
)

BUTTON_COLOR = (
    220,
    220,
    220,
)

BUTTON_HOVER_COLOR = (
    205,
    205,
    205,
)

BUTTON_ACTIVE_COLOR = (
    80,
    150,
    230,
)

BUTTON_ACTIVE_TEXT_COLOR = (
    255,
    255,
    255,
)

BUTTON_BORDER_COLOR = (
    120,
    120,
    120,
)

DISABLED_BUTTON_COLOR = (
    232,
    232,
    232,
)

DISABLED_TEXT_COLOR = (
    155,
    155,
    155,
)

RESTART_BUTTON_COLOR = (
    225,
    225,
    225,
)


# ============================================================
# 字体
# ============================================================

def load_font(
    size,
    bold=False,
):
    """
    直接从 Windows 字体目录加载字体。

    不使用 pygame.font.SysFont()，
    避免 pygame 2.6.1 在部分 Windows
    环境中扫描系统字体时报错。
    """

    windows_dir = Path(
        os.environ.get(
            "WINDIR",
            r"C:\Windows",
        )
    )

    font_dir = (
        windows_dir
        / "Fonts"
    )

    if bold:

        candidates = [
            "msyhbd.ttc",
            "msyh.ttc",
            "simhei.ttf",
            "simsun.ttc",
        ]

    else:

        candidates = [
            "msyh.ttc",
            "msyhl.ttc",
            "simhei.ttf",
            "simsun.ttc",
        ]

    for font_name in candidates:

        font_path = (
            font_dir
            / font_name
        )

        if font_path.exists():

            font = pygame.font.Font(
                str(font_path),
                size,
            )

            if bold:

                font.set_bold(
                    True
                )

            return font

    font = pygame.font.Font(
        None,
        size,
    )

    if bold:

        font.set_bold(
            True
        )

    return font


# ============================================================
# GUI
# ============================================================

class PygameUI:

    def __init__(self):

        pygame.init()

        self.screen = (
            pygame.display.set_mode(
                (
                    WINDOW_WIDTH,
                    WINDOW_HEIGHT,
                )
            )
        )

        pygame.display.set_caption(
            "Reversi - 黑白棋"
        )

        self.clock = (
            pygame.time.Clock()
        )

        # ====================================================
        # 字体
        # ====================================================

        self.font = load_font(
            24
        )

        self.small_font = load_font(
            18
        )

        self.button_font = load_font(
            15
        )

        self.large_font = load_font(
            32,
            bold=True,
        )

        # ====================================================
        # 玩家
        # ====================================================

        self.human_player = BLACK

        self.ai_player = WHITE

        # ====================================================
        # AI 配置
        # ====================================================

        self.selected_algorithm = (
            "Alpha-Beta"
        )

        self.selected_evaluator = (
            "Fixed"
        )

        self.ai = (
            self.create_ai()
        )

        # ====================================================
        # 游戏
        # ====================================================

        self.game = Game()

        # ====================================================
        # 当前状态
        # ====================================================

        self.human_turn_start = (
            time.perf_counter()
        )

        self.ai_pending = False

        self.last_move = None

        self.last_move_player = None

        self.last_move_time = 0.0

        self.ai_nodes = 0

        self.status_message = (
            "你执黑棋，点击黄色位置落子。"
        )

        self.running = True

        # ====================================================
        # 按钮布局
        # ====================================================

        panel_x = (
            BOARD_PIXEL_SIZE
            + 20
        )

        # =========================
        # AI 算法按钮
        # =========================

        algorithm_y = 100

        algorithm_width = 105

        algorithm_height = 34

        algorithm_gap = 8

        self.algorithm_buttons = {

            "Minimax": pygame.Rect(
                panel_x,
                algorithm_y,
                algorithm_width,
                algorithm_height,
            ),

            "Alpha-Beta": pygame.Rect(
                panel_x
                + algorithm_width
                + algorithm_gap,

                algorithm_y,

                algorithm_width,
                algorithm_height,
            ),

            "MCTS": pygame.Rect(
                panel_x
                + (
                    algorithm_width
                    + algorithm_gap
                ) * 2,

                algorithm_y,

                algorithm_width,
                algorithm_height,
            ),
        }

        # =========================
        # 评价函数按钮
        # =========================

        evaluator_y = 170

        evaluator_width = 150

        evaluator_height = 34

        evaluator_gap = 12

        self.evaluator_buttons = {

            "Fixed": pygame.Rect(
                panel_x,
                evaluator_y,
                evaluator_width,
                evaluator_height,
            ),

            "Dynamic": pygame.Rect(
                panel_x
                + evaluator_width
                + evaluator_gap,

                evaluator_y,

                evaluator_width,
                evaluator_height,
            ),
        }

        # =========================
        # 重新开始
        # =========================

        self.restart_button = (
            pygame.Rect(
                panel_x,
                578,
                330,
                42,
            )
        )

    # ========================================================
    # 当前 evaluator
    # ========================================================

    def get_evaluator(self):
        """返回当前选中的评价函数。"""

        if (
            self.selected_evaluator
            == "Fixed"
        ):

            return evaluate_fixed

        if (
            self.selected_evaluator
            == "Dynamic"
        ):

            return evaluate_dynamic

        raise ValueError(
            "未知评价函数"
        )

    # ========================================================
    # 创建 AI
    # ========================================================

    def create_ai(self):
        """根据当前配置创建 AI。"""

        if (
            self.selected_algorithm
            == "Minimax"
        ):

            return MinimaxAI(
                depth=MINIMAX_DEPTH,
                evaluator=self.get_evaluator(),
            )

        if (
            self.selected_algorithm
            == "Alpha-Beta"
        ):

            return AlphaBetaAI(
                depth=ALPHABETA_DEPTH,
                evaluator=self.get_evaluator(),
            )

        if (
            self.selected_algorithm
            == "MCTS"
        ):

            return MCTSAI(
                simulations=(
                    MCTS_SIMULATIONS
                ),
                random_seed=None,
            )

        raise ValueError(
            "未知 AI 算法"
        )

    # ========================================================
    # 当前 AI 描述
    # ========================================================

    def get_ai_description(self):
        """获取当前 AI 完整名称。"""

        if (
            self.selected_algorithm
            == "MCTS"
        ):

            return "MCTS"

        return (
            f"{self.selected_algorithm}"
            f" + "
            f"{self.selected_evaluator}"
        )

    # ========================================================
    # 当前 AI 参数
    # ========================================================

    def get_ai_parameter_text(self):

        if (
            self.selected_algorithm
            == "Minimax"
        ):

            return (
                f"搜索深度："
                f"{MINIMAX_DEPTH}"
            )

        if (
            self.selected_algorithm
            == "Alpha-Beta"
        ):

            return (
                f"搜索深度："
                f"{ALPHABETA_DEPTH}"
            )

        if (
            self.selected_algorithm
            == "MCTS"
        ):

            return (
                f"模拟次数："
                f"{MCTS_SIMULATIONS}"
            )

        return ""

    # ========================================================
    # 重新开始
    # ========================================================

    def restart_game(self):
        """
        清空当前棋局。

        保留当前算法和评价函数设置。
        """

        self.game = Game()

        self.ai = (
            self.create_ai()
        )

        self.human_turn_start = (
            time.perf_counter()
        )

        self.ai_pending = False

        self.last_move = None

        self.last_move_player = None

        self.last_move_time = 0.0

        self.ai_nodes = 0

        self.status_message = (
            f"新游戏开始。"
            f"AI：{self.get_ai_description()}。"
        )

    # ========================================================
    # 切换算法
    # ========================================================

    def select_algorithm(
        self,
        algorithm_name,
    ):

        if (
            algorithm_name
            not in self.algorithm_buttons
        ):

            return

        self.selected_algorithm = (
            algorithm_name
        )

        self.restart_game()

    # ========================================================
    # 切换评价函数
    # ========================================================

    def select_evaluator(
        self,
        evaluator_name,
    ):
        """
        Minimax / Alpha-Beta
        可以切换评价函数。

        MCTS 不使用该评价函数。
        """

        if (
            evaluator_name
            not in self.evaluator_buttons
        ):

            return

        if (
            self.selected_algorithm
            == "MCTS"
        ):

            self.status_message = (
                "MCTS 使用蒙特卡洛模拟，"
                "不使用 Fixed / Dynamic 评价函数。"
            )

            return

        self.selected_evaluator = (
            evaluator_name
        )

        self.restart_game()

    # ========================================================
    # 主循环
    # ========================================================

    def run(self):

        while self.running:

            self.handle_events()

            self.check_human_timeout()

            self.draw()

            pygame.display.flip()

            if (
                self.ai_pending
                and self.running
                and not self.game.game_over
            ):

                self.ai_pending = False

                self.handle_ai_turn()

            self.clock.tick(
                60
            )

        pygame.quit()

    # ========================================================
    # 事件
    # ========================================================

    def handle_events(self):

        for event in (
            pygame.event.get()
        ):

            if (
                event.type
                == pygame.QUIT
            ):

                self.running = False

            elif (
                event.type
                == pygame.MOUSEBUTTONDOWN
            ):

                if event.button == 1:

                    self.handle_mouse_click(
                        event.pos
                    )

    # ========================================================
    # 鼠标点击
    # ========================================================

    def handle_mouse_click(
        self,
        mouse_position,
    ):

        # ====================================================
        # AI 算法按钮
        # ====================================================

        for (
            algorithm_name,
            rect,
        ) in (
            self.algorithm_buttons.items()
        ):

            if rect.collidepoint(
                mouse_position
            ):

                self.select_algorithm(
                    algorithm_name
                )

                return

        # ====================================================
        # 评价函数按钮
        # ====================================================

        for (
            evaluator_name,
            rect,
        ) in (
            self.evaluator_buttons.items()
        ):

            if rect.collidepoint(
                mouse_position
            ):

                self.select_evaluator(
                    evaluator_name
                )

                return

        # ====================================================
        # 重新开始
        # ====================================================

        if (
            self.restart_button.collidepoint(
                mouse_position
            )
        ):

            self.restart_game()

            return

        # ====================================================
        # 棋盘
        # ====================================================

        if self.game.game_over:
            return

        if (
            self.game.current_player
            != self.human_player
        ):

            return

        mouse_x, mouse_y = (
            mouse_position
        )

        position = (
            self.mouse_to_board(
                mouse_x,
                mouse_y,
            )
        )

        if position is None:
            return

        row, col = (
            position
        )

        valid_moves = (
            self.game.get_valid_moves()
        )

        if (
            row,
            col
        ) not in valid_moves:

            self.status_message = (
                "该位置不能落子，请选择黄色位置。"
            )

            return

        # ====================================================
        # 玩家本步时间
        # ====================================================

        move_time = (
            time.perf_counter()
            - self.human_turn_start
        )

        if (
            move_time
            >= MOVE_TIME_LIMIT
        ):

            self.game.declare_timeout(
                self.human_player
            )

            self.last_move_time = (
                move_time
            )

            self.update_game_over_status()

            return

        success = (
            self.game.play_move(
                row,
                col,
                move_time=move_time,
            )
        )

        if not success:
            return

        self.last_move = (
            row,
            col,
        )

        self.last_move_player = (
            self.human_player
        )

        self.last_move_time = (
            move_time
        )

        # ====================================================
        # 玩家落子之后
        # ====================================================

        if self.game.game_over:

            self.update_game_over_status()

            return

        if (
            self.game.current_player
            == self.ai_player
        ):

            self.status_message = (
                f"{self.get_ai_description()}"
                " 正在思考……"
            )

            self.ai_pending = True

        else:

            self.status_message = (
                "白棋无合法落子，"
                "自动 Pass，你继续。"
            )

            self.human_turn_start = (
                time.perf_counter()
            )

    # ========================================================
    # 玩家超时
    # ========================================================

    def check_human_timeout(self):

        if self.game.game_over:
            return

        if (
            self.game.current_player
            != self.human_player
        ):

            return

        elapsed = (
            time.perf_counter()
            - self.human_turn_start
        )

        if (
            elapsed
            >= MOVE_TIME_LIMIT
        ):

            self.game.declare_timeout(
                self.human_player
            )

            self.ai_pending = False

            self.last_move_time = (
                elapsed
            )

            self.update_game_over_status()

    # ========================================================
    # AI 回合
    # ========================================================

    def handle_ai_turn(self):

        if self.game.game_over:
            return

        if (
            self.game.current_player
            != self.ai_player
        ):

            return

        move = self.ai.choose_move(
            self.game.board,
            self.ai_player,
        )

        # ====================================================
        # AI 超时
        # ====================================================

        if (
            self.ai.move_time
            >= MOVE_TIME_LIMIT
        ):

            self.game.declare_timeout(
                self.ai_player
            )

            self.last_move_time = (
                self.ai.move_time
            )

            self.ai_nodes = (
                self.ai.nodes_searched
            )

            self.update_game_over_status()

            return

        if move is None:

            self.status_message = (
                "AI 没有找到合法落子。"
            )

            return

        row, col = (
            move
        )

        success = (
            self.game.play_move(
                row,
                col,
                move_time=self.ai.move_time,
            )
        )

        if not success:

            self.status_message = (
                "AI 返回了非法落子。"
            )

            return

        self.last_move = (
            row,
            col,
        )

        self.last_move_player = (
            self.ai_player
        )

        self.last_move_time = (
            self.ai.move_time
        )

        self.ai_nodes = (
            self.ai.nodes_searched
        )

        # ====================================================
        # AI 落子之后
        # ====================================================

        if self.game.game_over:

            self.update_game_over_status()

            return

        if (
            self.game.current_player
            == self.human_player
        ):

            self.status_message = (
                "轮到你，请选择黄色位置。"
            )

            self.human_turn_start = (
                time.perf_counter()
            )

        else:

            self.status_message = (
                "黑棋无合法落子，"
                "自动 Pass，AI 继续。"
            )

            self.ai_pending = True

    # ========================================================
    # 游戏结束
    # ========================================================

    def update_game_over_status(self):

        winner = (
            self.game.get_winner()
        )

        black_count, white_count = (
            self.game.board.count_pieces()
        )

        # =========================
        # 超时
        # =========================

        if (
            self.game.end_reason
            == "timeout"
        ):

            if (
                self.game.timed_out_player
                == self.human_player
            ):

                self.status_message = (
                    "游戏结束：你思考超过 60 秒，"
                    f"{self.get_ai_description()} 获胜！"
                )

            else:

                self.status_message = (
                    "游戏结束：AI 思考超过 60 秒，"
                    "你获胜！"
                )

            return

        # =========================
        # 正常结束
        # =========================

        if winner == BLACK:

            result = (
                "你获胜！"
            )

        elif winner == WHITE:

            result = (
                f"{self.get_ai_description()}"
                " 获胜！"
            )

        else:

            result = (
                "平局！"
            )

        self.status_message = (
            f"游戏结束："
            f"{result} "
            f"{black_count}:{white_count}"
        )

    # ========================================================
    # 坐标转换
    # ========================================================

    def mouse_to_board(
        self,
        mouse_x,
        mouse_y,
    ):

        if (
            mouse_x < 0
            or mouse_x >= BOARD_PIXEL_SIZE
            or mouse_y < 0
            or mouse_y >= BOARD_PIXEL_SIZE
        ):

            return None

        col = (
            mouse_x
            // CELL_SIZE
        )

        row = (
            mouse_y
            // CELL_SIZE
        )

        return (
            row,
            col,
        )

    # ========================================================
    # 绘制
    # ========================================================

    def draw(self):

        self.screen.fill(
            BACKGROUND_COLOR
        )

        self.draw_board()

        self.draw_pieces()

        self.draw_valid_moves()

        self.draw_last_move()

        self.draw_side_panel()

    # ========================================================
    # 棋盘
    # ========================================================

    def draw_board(self):

        pygame.draw.rect(
            self.screen,
            BOARD_COLOR,
            (
                0,
                0,
                BOARD_PIXEL_SIZE,
                BOARD_PIXEL_SIZE,
            ),
        )

        for index in range(
            BOARD_SIZE + 1
        ):

            position = (
                index
                * CELL_SIZE
            )

            pygame.draw.line(
                self.screen,
                GRID_COLOR,
                (
                    position,
                    0,
                ),
                (
                    position,
                    BOARD_PIXEL_SIZE,
                ),
                2,
            )

            pygame.draw.line(
                self.screen,
                GRID_COLOR,
                (
                    0,
                    position,
                ),
                (
                    BOARD_PIXEL_SIZE,
                    position,
                ),
                2,
            )

        self.draw_coordinates()

    # ========================================================
    # 坐标文字
    # ========================================================

    def draw_coordinates(self):

        for col in range(
            BOARD_SIZE
        ):

            letter = chr(
                ord("A")
                + col
            )

            surface = (
                self.small_font.render(
                    letter,
                    True,
                    TEXT_COLOR,
                )
            )

            self.screen.blit(
                surface,
                (
                    col
                    * CELL_SIZE
                    + 5,

                    3,
                ),
            )

        for row in range(
            BOARD_SIZE
        ):

            number = str(
                row + 1
            )

            surface = (
                self.small_font.render(
                    number,
                    True,
                    TEXT_COLOR,
                )
            )

            self.screen.blit(
                surface,
                (
                    5,

                    row
                    * CELL_SIZE
                    + 25,
                ),
            )

    # ========================================================
    # 棋子
    # ========================================================

    def draw_pieces(self):

        radius = (
            CELL_SIZE // 2
            - 10
        )

        for row in range(
            BOARD_SIZE
        ):

            for col in range(
                BOARD_SIZE
            ):

                piece = (
                    self.game.board.grid[
                        row
                    ][
                        col
                    ]
                )

                if piece == EMPTY:
                    continue

                center_x = (
                    col
                    * CELL_SIZE
                    + CELL_SIZE // 2
                )

                center_y = (
                    row
                    * CELL_SIZE
                    + CELL_SIZE // 2
                )

                if piece == BLACK:

                    pygame.draw.circle(
                        self.screen,
                        BLACK_COLOR,
                        (
                            center_x,
                            center_y,
                        ),
                        radius,
                    )

                elif piece == WHITE:

                    pygame.draw.circle(
                        self.screen,
                        WHITE_COLOR,
                        (
                            center_x,
                            center_y,
                        ),
                        radius,
                    )

                    pygame.draw.circle(
                        self.screen,
                        WHITE_BORDER_COLOR,
                        (
                            center_x,
                            center_y,
                        ),
                        radius,
                        2,
                    )

    # ========================================================
    # 合法位置
    # ========================================================

    def draw_valid_moves(self):

        if self.game.game_over:
            return

        if (
            self.game.current_player
            != self.human_player
        ):

            return

        valid_moves = (
            self.game.get_valid_moves()
        )

        for row, col in valid_moves:

            center_x = (
                col
                * CELL_SIZE
                + CELL_SIZE // 2
            )

            center_y = (
                row
                * CELL_SIZE
                + CELL_SIZE // 2
            )

            pygame.draw.circle(
                self.screen,
                VALID_MOVE_COLOR,
                (
                    center_x,
                    center_y,
                ),
                8,
            )

    # ========================================================
    # 最后一步
    # ========================================================

    def draw_last_move(self):

        if self.last_move is None:
            return

        row, col = (
            self.last_move
        )

        margin = 4

        pygame.draw.rect(
            self.screen,
            LAST_MOVE_COLOR,
            (
                col
                * CELL_SIZE
                + margin,

                row
                * CELL_SIZE
                + margin,

                CELL_SIZE
                - margin * 2,

                CELL_SIZE
                - margin * 2,
            ),
            3,
        )

    # ========================================================
    # 右侧面板
    # ========================================================

    def draw_side_panel(self):

        pygame.draw.rect(
            self.screen,
            PANEL_COLOR,
            (
                BOARD_PIXEL_SIZE,
                0,
                SIDE_PANEL_WIDTH,
                WINDOW_HEIGHT,
            ),
        )

        panel_x = (
            BOARD_PIXEL_SIZE
            + 20
        )

        mouse_position = (
            pygame.mouse.get_pos()
        )

        # ====================================================
        # 标题
        # ====================================================

        self.draw_text(
            "黑白棋",
            panel_x,
            12,
            self.large_font,
        )

        self.draw_text(
            "你：黑棋",
            panel_x,
            58,
            self.small_font,
        )

        # ====================================================
        # AI 算法
        # ====================================================

        self.draw_text(
            "AI 算法：",
            panel_x,
            78,
            self.small_font,
        )

        for (
            algorithm_name,
            rect,
        ) in (
            self.algorithm_buttons.items()
        ):

            active = (
                algorithm_name
                == self.selected_algorithm
            )

            hover = (
                rect.collidepoint(
                    mouse_position
                )
            )

            self.draw_button(
                rect=rect,
                text=algorithm_name,
                active=active,
                hover=hover,
            )

        # ====================================================
        # 评价函数
        # ====================================================

        self.draw_text(
            "评价函数：",
            panel_x,
            145,
            self.small_font,
        )

        evaluation_enabled = (
            self.selected_algorithm
            != "MCTS"
        )

        for (
            evaluator_name,
            rect,
        ) in (
            self.evaluator_buttons.items()
        ):

            active = (
                evaluation_enabled
                and evaluator_name
                == self.selected_evaluator
            )

            hover = (
                evaluation_enabled
                and rect.collidepoint(
                    mouse_position
                )
            )

            self.draw_button(
                rect=rect,
                text=evaluator_name,
                active=active,
                hover=hover,
                disabled=(
                    not evaluation_enabled
                ),
            )

        # ====================================================
        # 当前配置
        # ====================================================

        self.draw_text(
            (
                "当前配置："
                f"{self.get_ai_description()}"
            ),
            panel_x,
            215,
            self.small_font,
        )

        self.draw_text(
            self.get_ai_parameter_text(),
            panel_x,
            242,
            self.small_font,
        )

        self.draw_text(
            "单步限时：60 秒",
            panel_x,
            269,
            self.small_font,
        )

        # ====================================================
        # 当前回合
        # ====================================================

        if self.game.game_over:

            current_name = (
                "游戏结束"
            )

        else:

            current_name = (
                self.game.get_player_name(
                    self.game.current_player
                )
            )

        self.draw_text(
            f"当前：{current_name}",
            panel_x,
            305,
            self.font,
        )

        # ====================================================
        # 比分
        # ====================================================

        black_count, white_count = (
            self.game.board.count_pieces()
        )

        self.draw_text(
            (
                f"比分："
                f"{black_count} : "
                f"{white_count}"
            ),
            panel_x,
            342,
            self.font,
        )

        # ====================================================
        # 上一步
        # ====================================================

        if self.last_move is None:

            last_move_text = (
                "上一步：暂无"
            )

        else:

            notation = (
                position_to_notation(
                    *self.last_move
                )
            )

            if (
                self.last_move_player
                == BLACK
            ):

                player_name = (
                    "黑棋"
                )

            else:

                player_name = (
                    "白棋"
                )

            last_move_text = (
                f"上一步："
                f"{player_name} "
                f"{notation}"
            )

        self.draw_text(
            last_move_text,
            panel_x,
            385,
            self.small_font,
        )

        self.draw_text(
            (
                "上步耗时："
                f"{self.last_move_time:.3f}s"
            ),
            panel_x,
            412,
            self.small_font,
        )

        # ====================================================
        # 累计时间
        # ====================================================

        self.draw_text(
            (
                "黑棋累计："
                f"{self.game.black_time:.3f}s"
            ),
            panel_x,
            445,
            self.small_font,
        )

        self.draw_text(
            (
                "白棋累计："
                f"{self.game.white_time:.3f}s"
            ),
            panel_x,
            472,
            self.small_font,
        )

        # ====================================================
        # 倒计时
        # ====================================================

        if (
            not self.game.game_over
            and self.game.current_player
            == self.human_player
        ):

            current_thinking = (
                time.perf_counter()
                - self.human_turn_start
            )

            remaining_time = max(
                0.0,
                MOVE_TIME_LIMIT
                - current_thinking,
            )

            self.draw_text(
                (
                    "本步剩余："
                    f"{remaining_time:.1f}s"
                ),
                panel_x,
                499,
                self.small_font,
            )

        # ====================================================
        # 搜索信息
        # ====================================================

        self.draw_text(
            (
                "AI 上次搜索节点："
                f"{self.ai_nodes}"
            ),
            panel_x,
            526,
            self.small_font,
        )

        # ====================================================
        # 状态提示
        # ====================================================

        self.draw_wrapped_text(
            self.status_message,
            panel_x,
            550,
            SIDE_PANEL_WIDTH - 40,
        )

        # ====================================================
        # 重新开始
        # ====================================================

        restart_hover = (
            self.restart_button.collidepoint(
                mouse_position
            )
        )

        self.draw_button(
            rect=self.restart_button,
            text="重新开始",
            active=False,
            hover=restart_hover,
            restart=True,
        )

    # ========================================================
    # 按钮
    # ========================================================

    def draw_button(
        self,
        rect,
        text,
        active=False,
        hover=False,
        restart=False,
        disabled=False,
    ):

        if disabled:

            background = (
                DISABLED_BUTTON_COLOR
            )

            text_color = (
                DISABLED_TEXT_COLOR
            )

        elif active:

            background = (
                BUTTON_ACTIVE_COLOR
            )

            text_color = (
                BUTTON_ACTIVE_TEXT_COLOR
            )

        elif hover:

            background = (
                BUTTON_HOVER_COLOR
            )

            text_color = (
                TEXT_COLOR
            )

        elif restart:

            background = (
                RESTART_BUTTON_COLOR
            )

            text_color = (
                TEXT_COLOR
            )

        else:

            background = (
                BUTTON_COLOR
            )

            text_color = (
                TEXT_COLOR
            )

        pygame.draw.rect(
            self.screen,
            background,
            rect,
            border_radius=6,
        )

        pygame.draw.rect(
            self.screen,
            BUTTON_BORDER_COLOR,
            rect,
            width=1,
            border_radius=6,
        )

        surface = (
            self.button_font.render(
                text,
                True,
                text_color,
            )
        )

        text_rect = (
            surface.get_rect(
                center=rect.center
            )
        )

        self.screen.blit(
            surface,
            text_rect,
        )

    # ========================================================
    # 普通文字
    # ========================================================

    def draw_text(
        self,
        text,
        x,
        y,
        font,
    ):

        surface = (
            font.render(
                text,
                True,
                TEXT_COLOR,
            )
        )

        self.screen.blit(
            surface,
            (
                x,
                y,
            ),
        )

    # ========================================================
    # 自动换行
    # ========================================================

    def draw_wrapped_text(
        self,
        text,
        x,
        y,
        max_width,
    ):

        lines = []

        current_line = ""

        for char in text:

            test_line = (
                current_line
                + char
            )

            width = (
                self.small_font.size(
                    test_line
                )[0]
            )

            if (
                width > max_width
                and current_line
            ):

                lines.append(
                    current_line
                )

                current_line = (
                    char
                )

            else:

                current_line = (
                    test_line
                )

        if current_line:

            lines.append(
                current_line
            )

        for index, line in enumerate(
            lines
        ):

            self.draw_text(
                line,
                x,
                y
                + index * 24,
                self.small_font,
            )