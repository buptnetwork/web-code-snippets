"""类型注解不参与运行时检查。"""


# #region double
def double(n: int) -> int:
    return n * 2
# #endregion double


print(double(3))                    # 6
print(double("ab"))                 # 注解写着 int，传 str 照样跑 → abab
print(double([1, 2]))               # 也照样跑 → [1, 2, 1, 2]
print(double.__annotations__)       # 注解只是被存起来了，谁想读谁读
