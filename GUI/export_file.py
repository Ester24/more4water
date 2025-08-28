import os
import sqlite3
import pandas as pd
import base64
import uuid

# Funzione per salvare l'immagine
def save_image(contents, filename):
    # La cartella 'uploads' deve esistere nel tuo progetto
    upload_folder = os.path.join(os.getcwd(), 'uploads')
    os.makedirs(upload_folder, exist_ok=True)
    
    # Decodifica il contenuto base64
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    
    # Crea un nome file univoco
    unique_filename = f"{uuid.uuid4()}_{filename}"
    
    file_path = os.path.join(upload_folder, unique_filename)
    
    with open(file_path, 'wb') as f:
        f.write(decoded)
        
    return unique_filename

# Percorso al database
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'mydatabase.db')

# Funzione per estrarre dati da una tabella e formattare i timestamp, se esistono
def estrai_tabella_e_formatta(nome_tabella):
    conn = sqlite3.connect(DB_PATH)
    df = pd.DataFrame()
    try:
        df = pd.read_sql_query(f"SELECT * FROM {nome_tabella}", conn)
        
        # Identifica le colonne che contengono timestamp, ma solo se esistono
        timestamp_cols = [col for col in df.columns if 'timestamp' in col.lower() or 'data' in col.lower()]
        
        # Converti il formato del timestamp solo se la colonna è stata trovata
        if timestamp_cols:
            for col in timestamp_cols:
                df[col] = pd.to_datetime(df[col]).dt.strftime('%Y-%m-%d %H:%M:%S')
            
    except Exception as e:
        print(f"Errore durante la lettura della tabella {nome_tabella}: {e}")
        df = pd.DataFrame()
    conn.close()
    return df

# Funzione principale per esportare in CSV
def esporta_database_in_csv():
    # Tabella: reports (segnalazioni specializzate)
    df_reports = estrai_tabella_e_formatta("reports")
    if not df_reports.empty:
        csv_reports_path = os.path.join(BASE_DIR, "segnalazioni_specializzate.csv")
        df_reports.to_csv(csv_reports_path, index=False, encoding="utf-8")
        print(f"Esportata tabella reports in: {csv_reports_path}")
    else:
        print("La tabella 'reports' è vuota o non è stato possibile leggerla.")

    # Tabella: general_reports (segnalazioni generiche)
    df_general = estrai_tabella_e_formatta("general_reports")
    if not df_general.empty:
        csv_general_path = os.path.join(BASE_DIR, "segnalazioni_generiche.csv")
        df_general.to_csv(csv_general_path, index=False, encoding="utf-8")
        print(f"Esportata tabella general_reports in: {csv_general_path}")
    else:
        print("La tabella 'general_reports' è vuota o non è stato possibile leggerla.")

# Esecuzione
if __name__ == "__main__":
    esporta_database_in_csv()
