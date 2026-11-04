def create_task(title):
    conn = get_db()
    cursor = conn.cursor()
    # psycopg2 needs us to insert, then select the new row
    cursor.execute("INSERT INTO tasks (title, done) VALUES (%s, %s) RETURNING id, title, done", (title, False))
    row = cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()
    return {"id": row[0], "title": row[1], "done": row[2]}

def update_task(task_id, title, done):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET title = %s, done = %s WHERE id = %s RETURNING id, title, done", (title, done, task_id))
    row = cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()
    return {"id": row[0], "title": row[1], "done": row[2]} if row else None