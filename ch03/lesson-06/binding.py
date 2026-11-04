"""psycopg 3 同步读取示例；连接由调用者提供，配置 row_factory=dict_row。"""

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
