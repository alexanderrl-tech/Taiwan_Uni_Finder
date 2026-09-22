import sqlite3
import os

DB_PATH = "sql/TwUni_Finder.db"


def init_database():
    os.makedirs("data", exist_ok=True)

    connection = sqlite3.connect(DB_PATH)

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            affiliation TEXT,
            major TEXT,
            degree TEXT,
            about TEXT,
            interests TEXT,
            preferred_degree TEXT,
            preferred_field TEXT,
            photo_path TEXT
        )
    """)

    connection.commit()
    connection.close()