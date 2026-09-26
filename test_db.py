import sqlite3

conn = sqlite3.connect("tasks.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    done BOOLEAN NOT NULL DEFAULT 0
)
""")

cursor.execute("SELECT COUNT(*) FROM tasks")
count = cursor.fetchone()[0]

if count == 0:
    cursor.executemany(
        "INSERT INTO tasks (title, done) VALUES (?, ?)",
        [("Buy milk", 0), ("Write README", 0), ("Push to GitHub", 1)]
    )
    print("seeded 3 example tasks")
else:
    print(f"table already has {count} tasks, skipping seed")

conn.commit()