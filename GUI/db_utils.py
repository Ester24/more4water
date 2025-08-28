import os
import sqlite3
from datetime import datetime
import pandas as pd

# Percorso assoluto al file mydatabase.db
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'mydatabase.db')

# --- Funzione per l'inserimento di Segnalazioni Specializzate ---
def insert_report(user_id, sensor_id, issue_type, description, priority=1):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            user_id INTEGER,
            sensor_id TEXT,
            issue_type TEXT,
            description TEXT,
            priority INTEGER
        )
    ''')
    conn.commit()

    timestamp = datetime.now().isoformat()

    query = '''
        INSERT INTO reports (timestamp, user_id, sensor_id, issue_type, description, priority)
        VALUES (?, ?, ?, ?, ?, ?)
    '''
    cursor.execute(query, (timestamp, user_id, sensor_id, issue_type, description, priority))
    conn.commit()
    conn.close()

# --- Funzione per l'inserimento di Segnalazioni Generiche (MODIFICATA) ---
def insert_general_report(first_name, last_name, region, province, city, address, problem_description, image_path):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Aggiunta la colonna 'image_path' alla tabella 'general_reports'
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS general_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            first_name TEXT,
            last_name TEXT,
            region TEXT,
            province TEXT,
            city TEXT,
            address TEXT,
            problem_description TEXT,
            image_path TEXT  -- Nuova colonna per salvare il percorso dell'immagine
        )
    ''')
    conn.commit()

    timestamp = datetime.now().isoformat()

    query = '''
        INSERT INTO general_reports (timestamp, first_name, last_name, region, province, city, address, problem_description, image_path)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    '''
    cursor.execute(query, (timestamp, first_name, last_name, region, province, city, address, problem_description, image_path))
    conn.commit()
    conn.close()