import sqlite3
import os
from GUI.db_utils import DB_PATH

def create_tables():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Tabella degli utenti
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        role TEXT DEFAULT 'user',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Tabella delle segnalazioni specializzate
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        sensor_id TEXT,
        issue_type TEXT NOT NULL,
        description TEXT,
        priority INTEGER DEFAULT 1,
        status TEXT DEFAULT 'open',
        timestamp TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')

    # Tabella delle segnalazioni generiche
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS general_reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        first_name TEXT,
        last_name TEXT,
        province TEXT,
        city TEXT,
        address TEXT,
        problem_description TEXT,
        image_path TEXT
    )
    ''')

    conn.commit()
    conn.close()

if __name__ == '__main__':
    create_tables()
