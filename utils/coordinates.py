from config import BOARD_SIZE


def position_to_notation(row, col):
    """
    将程序内部坐标转换为棋盘坐标。

    例如：
    (2, 3) -> "D3"
    """

    if not (
        0 <= row < BOARD_SIZE
        and
        0 <= col < BOARD_SIZE
    ):
        return None

    column_letter = chr(ord("A") + col)

    row_number = row + 1

    return f"{column_letter}{row_number}"

def notation_to_position(notation):
    """
    将棋盘坐标转换为程序内部坐标。

    例如：
    "D3" -> (2, 3)

    非法输入返回 None。
    """

    notation = notation.strip().upper()

    if len(notation) != 2:
        return None

    column_char = notation[0]
    row_char = notation[1]

    if not ("A" <= column_char <= "H"):
        return None

    if not ("1" <= row_char <= "8"):
        return None

    col = ord(column_char) - ord("A")

    row = int(row_char) - 1

    return row, col