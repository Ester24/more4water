import os
import sqlite3

# Percorso assoluto al file mydatabase.db
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'mydatabase.db')

def insert_report(user_id, sensor_id, issue_type, description, priority=1): 
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    query = '''
        INSERT INTO reports (user_id, sensor_id, issue_type, description, priority)
        VALUES (?, ?, ?, ?, ?)
    '''
    cursor.execute(query, (user_id, sensor_id, issue_type, description, priority))
    conn.commit()
    conn.close()
