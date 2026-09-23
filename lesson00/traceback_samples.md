# 练习：读这三段报错，各回答两个问题
# ① 哪个文件、哪一行？  ② 我该先去改什么？

## 第 1 段
Traceback (most recent call last):
  File "<frozen runpy>", line 198, in _run_module_as_main
  File "<frozen runpy>", line 88, in _run_code
  File "/Users/me/course/mini/cli.py", line 8, in <module>
    from mini.errors import AppError
ModuleNotFoundError: No module named 'mini'

## 第 2 段
Traceback (most recent call last):
  File "/Users/me/course/mini/cli.py", line 9, in <module>
    from mini.service import TodoService
  File "/Users/me/course/mini/service.py", line 3, in <module>
    from mini.cli import main
ImportError: cannot import name 'main' from partially initialized module 'mini.cli'
(most likely due to a circular import)

## 第 3 段
Traceback (most recent call last):
  File "/Users/me/course/mini/cli.py", line 62, in main
    print("已添加：" + render(svc.add_todo(args.title)))
                                ^^^^^^^^^^^^^^^^^^^^^
  File "/Users/me/course/mini/service.py", line 31, in add_todo
    if self.repo.title_exists(title):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/me/course/mini/repo.py", line 47, in title_exists
    return any(row.titel == title for row in self._load())
               ^^^^^^^^^
AttributeError: 'Todo' object has no attribute 'titel'. Did you mean: 'title'?

<!-- 参考答案（学生版请删除此段）
第1段：不是代码问题，是工作目录不对或没用 -m。先 cd 到 snippets/lesson00 再用 python -m mini.cli
第2段：循环导入。service.py 第 3 行那句 import 要删掉——依赖方向反了
第3段：repo.py 第 47 行拼错了 title。注意：错误产生在仓储层，
       但报错是从 cli 一路传上来的——这就是异常穿层
-->
