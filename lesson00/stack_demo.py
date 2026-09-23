"""调用栈练习：在 return total 那一行打断点，观察 Call Stack 面板的四个帧。"""


# #region levels
def level3(n: int) -> int:
    total = n * 2
    return total            # ← 断点打在这一行


def level2(n: int) -> int:
    return level3(n + 1)


def level1(n: int) -> int:
    return level2(n * 10)
# #endregion levels


if __name__ == "__main__":
    print(level1(3))        # 期望输出 62
