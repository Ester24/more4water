import pandas as pd
import requests
import os
from io import StringIO
import math
from datetime import datetime
import csv
# https://thingspeak.mathworks.com/channels/1293177
# --- ID del canale ThingSpeak da utilizzare per i dati in tempo reale ---
THINGSPEAK_CHANNEL_ID = '1293177'
# THINGSPEAK_API_KEY = 'YOUR_API_KEY' # Sostituisci con la tua API key di lettura

def carica_df_thingspeak():
    """
    Carica gli ultimi 100 dati in tempo reale dal canale ThingSpeak.

    Restituisce:
        pandas.DataFrame: Un DataFrame con i dati, o un DataFrame vuoto in caso di errore.
    """
    try:
        #url = f"https://api.thingspeak.com/channels/{THINGSPEAK_CHANNEL_ID}/feeds.json?results=100&api_key={THINGSPEAK_API_KEY}"
        url = f"https://api.thingspeak.com/channels/{THINGSPEAK_CHANNEL_ID}/feeds.json?results=100"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        feeds = data.get('feeds', [])
        if not feeds:
            print("Nessun dato trovato nel canale ThingSpeak.")
            return pd.DataFrame()
            
        df = pd.DataFrame(feeds)
        df['created_at'] = pd.to_datetime(df['created_at'])
        
        # Converte il fuso orario da UTC a Europa/Roma
        df['created_at'] = df['created_at'].dt.tz_convert('Europe/Rome')
        
        # Rimuove le informazioni sul fuso orario per compatibilità
        df['created_at'] = df['created_at'].dt.tz_localize(None)

        sensori_disponibili = [col for col in df.columns if col.startswith('field')]
        for col in sensori_disponibili:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
    except requests.exceptions.RequestException as e:
        print(f"Errore nella richiesta a ThingSpeak: {e}")
        return pd.DataFrame()
    except Exception as e:
        print(f"Si è verificato un errore: {e}")
        return pd.DataFrame()


def carica_df(percorso_csv):
    """
    Carica, pulisce e parsa il file CSV in un DataFrame di Pandas.
    """
    try:
        if not os.path.exists(percorso_csv):
            print(f"File non trovato: {percorso_csv}")
            return pd.DataFrame()

        with open(percorso_csv, 'r', encoding='utf-8', newline='') as infile:
            lines = infile.readlines()
        
        righe_pulite = []
        for line in lines:
            line = line.strip()
            if line.startswith('"') and line.endswith('"'):
                line = line[1:-1]
            line = line.replace('""', '"')
            righe_pulite.append(line)
        
        cleaned_data_io = StringIO('\n'.join(righe_pulite))
        df = pd.read_csv(cleaned_data_io)
        
        df.columns = df.columns.str.strip()
        df['created_at'] = pd.to_datetime(df['created_at'])
        
        # Rimuovi le informazioni sul fuso orario per compatibilità
        if df['created_at'].dt.tz is not None:
            df['created_at'] = df['created_at'].dt.tz_localize(None)
        
        DELTA = 2.048 / (2**12)
        I_MIN = 4
        I_MAX = 20
        H_MIN = 0
        H_MAX = 20
        
        is_villaverla_sensor = percorso_csv.endswith('m4w_Villaverla.csv')

        for col_name in df.columns:
            if col_name.startswith('field') and col_name[5:].isdigit():
                if col_name == 'field3' and is_villaverla_sensor:
                    df[col_name] = pd.to_numeric(df[col_name], errors='coerce')
                    i = df[col_name] * DELTA / 102 * 1000
                    h = ((i - I_MIN) / (I_MAX - I_MIN)) * (H_MAX - H_MIN) + H_MIN
                    df[col_name] = h
                else:
                    df[col_name] = pd.to_numeric(df[col_name], errors='coerce')
                    df[col_name] = df[col_name].apply(lambda x: math.trunc(x * 100) / 100.0 if not pd.isna(x) else None)
        
        return df
    except Exception as e:
        print(f"Si è verificato un errore in carica_df: {e}")
        return pd.DataFrame()

