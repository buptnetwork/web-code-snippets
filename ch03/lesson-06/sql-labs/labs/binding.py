"""参数绑定示例：值由 Python 传入，SQL 文本里只留 %s 占位符。

连接由调用者提供（见 labs/connection.py，已配置 row_factory=dict_row）。
运行：uv run --env-file .env python -m examples.ex05_q1_binding
"""

# region find-by-author
def find_questions_by_author(conn, author_id: int):
    rows = conn.execute(
        """
        SELECT id, title
        FROM questions
        WHERE author_id = %s
        ORDER BY id
        """,
        (author_id,),
    ).fetchall()
    return rows
# endregion find-by-author
