import sqlite3
import time



conn = sqlite3.connect("casino.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    money INTEGER NOT NULL,
    daily INTEGER
)
""")

conn.commit()
conn.close()



def get_or_create_user(user_id):
    conn = sqlite3.connect("casino.db")
    cur = conn.cursor()

    cur.execute(
        "SELECT money FROM users WHERE user_id = ?",
        (user_id,)
    )
    row = cur.fetchone()

    if row is None:
        cur.execute(
            "INSERT INTO users (user_id, money, daily) VALUES (?, ?, ?)",
            (user_id, 100, None)  # argent initial
        )
        conn.commit()
        money = 100
    else:
        money = row[0]

    conn.close()
    return money

def get_user(user_id):
    conn = sqlite3.connect("casino.db")
    cur = conn.cursor()

    cur.execute(
        "SELECT money FROM users WHERE user_id = ?",
        (user_id,)
    )
    row = cur.fetchone()

    if row is None:
        return -1
    else:
        money = row[0]

    conn.close()
    return money

def get_daily(user_id):
    conn = sqlite3.connect("casino.db")
    cur = conn.cursor()

    cur.execute(
        "SELECT daily FROM users WHERE user_id = ?",
        (user_id,)
    )
    row = cur.fetchone()
    
    conn.close()
    return(row[0])

def set_daily(user_id):
    conn = sqlite3.connect("casino.db")
    cur = conn.cursor()

    cur.execute(
        "UPDATE users SET daily = ? WHERE user_id = ?",
        (int(time.time()), user_id)
    )

    conn.commit()
    conn.close()


def add_money(user_id, amount):
    conn = sqlite3.connect("casino.db")
    cur = conn.cursor()

    cur.execute(
        "UPDATE users SET money = money + ? WHERE user_id = ?",
        (amount, user_id)
    )

    conn.commit()
    conn.close()

def remove_money(user_id, amount):
    conn = sqlite3.connect("casino.db")
    cur = conn.cursor()

    cur.execute(
        "UPDATE users SET money = money - ? WHERE user_id = ?",
        (amount, user_id)
    )

    conn.commit()
    conn.close()

def top(x, y):

    limit = y - x + 1
    offset = x - 1

    conn = sqlite3.connect("casino.db")
    cur = conn.cursor()    

    cur.execute(
        """
        SELECT user_id, money
        FROM users
        ORDER BY money DESC
        LIMIT ? OFFSET ?
        """,
        (limit, offset)
    )
    rows = cur.fetchall()
    conn.close()
    return rows