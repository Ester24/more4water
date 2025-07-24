import os
import sqlite3
from datetime import datetime # Importa datetime per i timestamp

# Percorso assoluto al file mydatabase.db
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'mydatabase.db')

# --- Funzione per l'inserimento di Segnalazioni Specializzate ---
# Questa funzione è utilizzata dalla pagina '/segnalazione_specializzata'
# per registrare segnalazioni che includono Sensor ID, Issue Type e Priority.
def insert_report(user_id, sensor_id, issue_type, description, priority=1):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Crea la tabella 'reports' se non esiste.
    # Aggiunto 'timestamp' per registrare quando la segnalazione è stata fatta.
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

    timestamp = datetime.now().isoformat() # Genera il timestamp corrente

    query = '''
        INSERT INTO reports (timestamp, user_id, sensor_id, issue_type, description, priority)
        VALUES (?, ?, ?, ?, ?, ?)
    '''
    cursor.execute(query, (timestamp, user_id, sensor_id, issue_type, description, priority))
    conn.commit()
    conn.close()

# --- Funzione per l'inserimento di Segnalazioni Generiche ---
# Questa funzione è utilizzata dalla pagina '/segnalazione_generica'
# per registrare segnalazioni con i dettagli dell'utente e la località.
def insert_general_report(first_name, last_name, region, province, city, address, problem_description):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Crea la tabella 'general_reports' se non esiste.
    # Aggiunto 'timestamp' per registrare quando la segnalazione è stata fatta.
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
            problem_description TEXT
        )
    ''')
    conn.commit()

    timestamp = datetime.now().isoformat() # Genera il timestamp corrente

    query = '''
        INSERT INTO general_reports (timestamp, first_name, last_name, region, province, city, address, problem_description)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    '''
    cursor.execute(query, (timestamp, first_name, last_name, region, province, city, address, problem_description))
    conn.commit()
    conn.close()
