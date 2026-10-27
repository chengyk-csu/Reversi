class BaseAI:
    """
    所有 AI 算法的基类。

    不同 AI 都需要提供统一的 choose_move() 接口。
    """

    def __init__(self, name):
        self.name = name

        # 本次决策搜索的节点数量
        self.nodes_searched = 0

        # 本次决策所花时间
        self.move_time = 0.0

    def reset_stats(self):
        """清空本次搜索统计数据。"""

        self.nodes_searched = 0
        self.move_time = 0.0

    def choose_move(self, board, player):
        """
        根据当前棋盘，为 player 选择一步棋。

        返回：
        (row, col)

        如果当前没有合法棋：
        返回 None。
        """

        raise NotImplementedError