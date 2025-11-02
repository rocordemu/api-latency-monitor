import sqlite3
import time

def init_db():
    conn = sqlite3.connect("status.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS status (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            endpoint TEXT,
            status_code INTEGER,
            latency REAL,
            timestamp REAL
        )
    """)
    conn.commit()
    conn.close()

def save_status(endpoint: str, status_code: int, latency: float):
    conn = sqlite3.connect("status.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO status (endpoint, status_code, latency, timestamp) VALUES (?, ?, ?, ?)",
        (endpoint, status_code, latency, time.time())
    )
    conn.commit()
    conn.close()

def get_latest_status():
    conn = sqlite3.connect("status.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT endpoint, status_code, latency, timestamp
        FROM status
        WHERE (endpoint, timestamp) IN (
            SELECT endpoint, MAX(timestamp)
            FROM status
            GROUP BY endpoint
        )
    """)
    rows = cursor.fetchall()
    conn.close()
    return [
        {"endpoint": row[0], "status_code": row[1], "latency": row[2], "timestamp": row[3]}
        for row in rows
    ]