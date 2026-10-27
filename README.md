# Reversi 黑白棋人工智能系统

一个基于 Python 实现的黑白棋（Reversi / Othello）人工智能课程项目。

项目实现了完整的黑白棋规则、Pygame 图形化人机对弈界面，以及三种人工智能搜索算法：

- Minimax
- Alpha-Beta Pruning
- Monte Carlo Tree Search（MCTS）

在基础固定评价函数之外，项目还实现了一个阶段感知的 Dynamic Evaluation，根据开局、中局和残局动态调整评价权重，并通过独立实验进行了验证。

---

## 1. 项目功能

### 黑白棋规则

支持标准 8×8 黑白棋规则：

- 黑棋先手
- 八方向合法落子判断
- 自动翻转被夹住的棋子
- 无合法动作时自动 Pass
- 双方均无合法动作时游戏结束
- 根据最终棋子数量判断胜负
- 单步思考时间超过 60 秒判负

### 图形化界面

使用 Pygame 实现人机对弈界面，支持：

- 鼠标点击落子
- 合法落子位置提示
- 最后一步位置标记
- 实时比分
- 当前回合显示
- 单步思考时间
- 双方累计思考时间
- 60 秒倒计时
- AI 搜索节点数显示
- 重新开始
- AI 算法切换
- Fixed / Dynamic Evaluation 切换

### 人工智能算法

实现：

1. Minimax
2. Alpha-Beta Pruning
3. Monte Carlo Tree Search

Minimax 和 Alpha-Beta 支持：

- Fixed Evaluation
- Dynamic Evaluation

MCTS 使用蒙特卡洛随机模拟，不依赖上述启发式评价函数。

---

## 2. 项目结构

```text
Reversi/
├── main.py
├── config.py
├── README.md
├── requirements.txt
├── report.md
│
├── core/
│   ├── __init__.py
│   ├── board.py
│   └── game.py
│
├── ai/
│   ├── __init__.py
│   ├── base.py
│   ├── evaluation.py
│   ├── minimax.py
│   ├── alphabeta.py
│   └── mcts.py
│
├── ui/
│   ├── __init__.py
│   └── pygame_ui.py
│
├── utils/
│   ├── __init__.py
│   └── coordinates.py
│
├── experiments/
│   ├── __init__.py
│   ├── search_comparison.py
│   ├── tournament.py
│   ├── evaluation_comparison.py
│   ├── evaluation_position_comparison.py
│   ├── evaluation_weight_tuning.py
│   ├── evaluation_weight_tuning_round2.py
│   ├── final_dynamic_validation.py
│   ├── final_algorithm_benchmark.py
│   ├── final_search_efficiency_only.py
│   ├── plot_results.py
│   ├── plot_final_validation.py
│   ├── plot_final_algorithm_benchmark.py
│   └── figures/
│
└── tests/
    ├── test_board.py
    ├── test_game.py
    ├── test_evaluation.py
    ├── test_minimax.py
    ├── test_alphabeta.py
    └── test_mcts.py
```

---

## 3. 环境要求

推荐环境：

```text
Python 3.10+
Windows 10 / Windows 11
```

主要第三方依赖：

```text
pygame
matplotlib
```

项目核心搜索算法本身只依赖 Python 标准库。

---

## 4. 安装

进入项目根目录：

```powershell
cd D:\Code\Python\Reversi
```

安装依赖：

```powershell
pip install -r requirements.txt
```

---

## 5. 启动游戏

在项目根目录运行：

```powershell
python main.py
```

启动后默认配置为：

```text
玩家：黑棋
AI：白棋
算法：Alpha-Beta
评价函数：Fixed
搜索深度：4
单步限时：60 秒
```

玩家点击棋盘上的黄色提示位置完成落子。

---

## 6. GUI 中切换算法

程序支持：

```text
Minimax
Alpha-Beta
MCTS
```

选择 Minimax 或 Alpha-Beta 时，还可以选择：

```text
Fixed
Dynamic
```

例如：

```text
Minimax + Fixed
Minimax + Dynamic
Alpha-Beta + Fixed
Alpha-Beta + Dynamic
MCTS
```

由于 MCTS 不使用 Minimax 类启发式叶节点评价，因此 MCTS 模式下 Fixed / Dynamic 选项不可用。

切换算法或评价函数时会自动重新开始一局。

---

## 7. 固定评价函数

Fixed Evaluation 综合考虑：

- 棋子数量差
- 位置价值
- 机动性
- 角点占有

评价形式为：

```text
Score =
Piece
+ Position
+ 10 × Mobility
+ 25 × Corner
```

---

## 8. 动态阶段评价函数

Dynamic Evaluation 根据当前棋盘已占据格数将棋局划分为：

```text
Opening:
occupied <= 20

Midgame:
21 <= occupied <= 50

Endgame:
occupied >= 51
```

最终采用的权重为：

| 阶段 | Piece | Position | Mobility | Corner |
|---|---:|---:|---:|---:|
| Opening | -1.0 | 1.0 | 12.0 | 30.0 |
| Midgame | 1.0 | 1.0 | 15.0 | 40.0 |
| Endgame | 10.0 | 0.5 | 5.0 | 50.0 |

最终独立测试共进行 60 局：

```text
Dynamic：32 胜
Fixed：26 胜
平局：2
```

Dynamic Evaluation：

```text
胜率：53.33%
比赛积分率：55.00%
平均棋子差：+6.35
```

---

## 9. Minimax 与 Alpha-Beta 实验结果

使用相同：

- 初始局面
- 搜索深度
- Fixed Evaluation
- 动作顺序

得到：

| Depth | Minimax Nodes | Alpha-Beta Nodes | Node Reduction | Minimax Time | Alpha-Beta Time |
|---:|---:|---:|---:|---:|---:|
| 2 | 16 | 14 | 12.50% | 0.003606 s | 0.003066 s |
| 3 | 72 | 54 | 25.00% | 0.016873 s | 0.012070 s |
| 4 | 316 | 171 | 45.89% | 0.070491 s | 0.035621 s |
| 5 | 1712 | 504 | 70.56% | 0.378402 s | 0.106743 s |

所有搜索深度下，两种算法均选择：

```text
D3
```

说明 Alpha-Beta 在保持 Minimax 决策结果不变的情况下显著减少了搜索节点。

---

## 10. 三算法对战结果

正式实验参数：

```text
Minimax depth = 3
Alpha-Beta depth = 3
MCTS simulations = 500
```

### Minimax vs Alpha-Beta

```text
Minimax：5 胜
Alpha-Beta：5 胜
平局：0
```

说明相同深度和评价函数下两者决策能力基本一致，但 Alpha-Beta 搜索效率更高。

### Minimax vs MCTS

```text
Minimax：3 胜
MCTS：5 胜
平局：2
```

### Alpha-Beta vs MCTS

```text
Alpha-Beta：4 胜
MCTS：6 胜
```

在 500 次模拟条件下，MCTS 获得较好的实际对弈表现，但计算时间明显高于 Alpha-Beta。

---

## 11. 运行自动测试

项目根目录运行：

```powershell
python -m unittest discover -s tests
```

当前测试覆盖：

```text
Board
Game
Evaluation
Minimax
Alpha-Beta
MCTS
```

包括：

- 规则正确性
- Pass
- 终局
- 超时
- 搜索合法性
- 搜索不修改真实棋盘
- Alpha-Beta 与 Minimax 一致性
- Alpha-Beta 剪枝效果
- MCTS UCT
- MCTS Pass
- 随机种子可复现性

---

## 12. 运行正式搜索效率实验

```powershell
python -m experiments.final_search_efficiency_only
```

输出：

```text
experiments/final_search_efficiency.csv
```

---

## 13. 运行三算法正式对战

```powershell
python -m experiments.final_algorithm_benchmark
```

主要输出：

```text
experiments/final_search_efficiency.csv
experiments/final_tournament_games.csv
experiments/final_tournament_summary.csv
```

---

## 14. 运行 Dynamic Evaluation 最终验证

```powershell
python -m experiments.final_dynamic_validation
```

主要输出：

```text
experiments/final_dynamic_validation_games.csv
experiments/final_dynamic_validation_summary.csv
```

---

## 15. 生成实验图表

正式算法实验：

```powershell
python -m experiments.plot_final_algorithm_benchmark
```

动态评价最终实验：

```powershell
python -m experiments.plot_final_validation
```

图片输出至：

```text
experiments/figures/
```

主要包括：

```text
Minimax / Alpha-Beta 搜索节点数
Minimax / Alpha-Beta 搜索时间
Alpha-Beta 节点削减比例
三算法对战胜率
三算法平均棋子差
Dynamic Evaluation 比赛积分率
Dynamic Evaluation 平均棋子差
Dynamic / Fixed 最终胜负统计
```

---

## 16. 主要实验结论

### Alpha-Beta

在搜索深度 5 时：

```text
Minimax：
1712 nodes
0.378402 s

Alpha-Beta：
504 nodes
0.106743 s
```

Alpha-Beta：

```text
节点数减少 70.56%
时间减少 71.79%
```

同时最终动作保持一致。

因此 Alpha-Beta 能够有效降低 Minimax 搜索开销。

### MCTS

在 500 simulations 下，MCTS 在实际 AI 对战中取得较好的胜率，但运行时间明显高于 Alpha-Beta。

### Dynamic Evaluation

最终 60 局独立测试中：

```text
Dynamic 32 胜
Fixed 26 胜
2 平
```

说明阶段化评价函数在本实验条件下取得了小幅而稳定的整体改进。

---

## 17. 后续改进方向

可以进一步尝试：

- Alpha-Beta Move Ordering
- Transposition Table
- Zobrist Hashing
- Endgame Exact Search
- Iterative Deepening
- Stable Disc Evaluation
- Frontier Disc Evaluation
- Potential Mobility
- Parity Evaluation
- MCTS Heuristic Rollout
- RAVE
- Progressive Bias

---

## 18. 项目入口

游戏入口：

```text
main.py
```

运行：

```powershell
python main.py
```

实验报告：

```text
report.md
```