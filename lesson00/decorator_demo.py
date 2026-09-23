"""装饰器的两种用途，以及用于阅读的迷你路由表。

MiniApp 用字典保存对应关系；FastAPI 的 app.routes 是路由对象列表。
两者职责相似，但数据结构与匹配机制不同，不把本例当成真实框架实现。
"""

# ---------- 用途一：包装函数 ----------


# #region log_call
def log_call(func):
    def wrapper(*args, **kwargs):
        print(f"[调用] {func.__name__}")
        return func(*args, **kwargs)
    return wrapper


@log_call                 # 等价于： greet = log_call(greet)
def greet():
    return "hi"
# #endregion log_call


# ---------- 用途二：登记函数（本例返回原函数） ----------


# #region miniapp
class MiniApp:
    def __init__(self):
        self.routes = {}                             # 路由表就是一个字典

    def route(self, path, method="GET"):             # 第一步：接住参数
        def decorator(func):                          # 第二步：接住被装饰的函数
            self.routes[(method, path)] = func         # 登记！函数本身没被改动
            print(f"[注册] {method} {path} -> {func.__name__}")
            return func                                # 原样返回
        return decorator

    def handle(self, method, path):                   # 模拟"来了一个请求"
        func = self.routes.get((method, path))
        if func is None:
            return 404, "not found"
        return 200, func()
# #endregion miniapp


app = MiniApp()


# #region register
@app.route("/posts")                  # 两步展开：
def list_posts():                     #   decorator = app.route("/posts")
    return "帖子列表"                  #   list_posts = decorator(list_posts)


@app.route("/posts", method="POST")
def create_post():
    return "已创建"
# #endregion register


if __name__ == "__main__":
    print("--- 模块顶层已完成注册；尚未调用处理函数 ---")
    print(app.routes)
    print(app.handle("GET", "/posts"))
    print(app.handle("POST", "/posts"))
    print(app.handle("GET", "/nope"))
    print(greet())
