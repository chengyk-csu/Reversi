class BaseAI:
    """所有 AI 算法的基类，提供统一的决策接口。"""

    def __init__(self, name):
        self.name = name
        self.nodes_searched = 0
        self.move_time = 0.0

    def reset_stats(self):
        self.nodes_searched = 0
        self.move_time = 0.0

    def choose_move(self, board, player):
        """返回最佳落子 (row, col)，无合法动作时返回 None。"""
        raise NotImplementedError