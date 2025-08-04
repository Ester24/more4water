import pandas as pd
from io import StringIO
import os

def ripulisci_csv(percorso_origine, percorso_destinazione):
    """
    Legge un file CSV, rimuove le virgolette esterne non necessarie e
    sostituisce le doppie virgolette interne con singole.
    Salva il risultato in un nuovo file pulito.
    """
    try:
        with open(percorso_origine, 'r', encoding='utf-8') as infile:
            lines = infile.readlines()

        righe_pulite = []
        for line in lines:
            line = line.strip()
            if line.startswith('"') and line.endswith('"'):
                line = line[1:-1]
            line = line.replace('""', '"')
            righe_pulite.append(line)

        with open(percorso_destinazione, 'w', encoding='utf-8') as outfile:
            outfile.write('\n'.join(righe_pulite))
        return True

    except Exception:
        return False


def carica_df_sanitizzato(percorso_csv):
    """
    Pulisce il file CSV e poi lo carica in un DataFrame pandas.
    """
    try:
        if not os.path.exists(percorso_csv):
            return pd.DataFrame()

        percorso_pulito = percorso_csv.replace('.csv', '_pulito.csv')
        
        if not ripulisci_csv(percorso_csv, percorso_pulito):
            return pd.DataFrame()

        df = pd.read_csv(
            percorso_pulito,
            sep=",",
            quotechar='"',
            engine='python',
            skipinitialspace=True
        )

        os.remove(percorso_pulito)

        df.columns = df.columns.str.strip()
            
        if 'created_at' not in df.columns:
            return pd.DataFrame()

        df['created_at'] = pd.to_datetime(df['created_at'], format="%Y-%m-%dT%H:%M:%S%z", errors='coerce')
        df.dropna(subset=['created_at'], inplace=True)

        if df.empty:
            return df

        if df['created_at'].dt.tz is not None:
             df['created_at'] = df['created_at'].dt.tz_convert('UTC').dt.tz_localize(None)

        sensor_cols = [col for col in df.columns if col.startswith('field') and col[5:].isdigit()]
        for col in sensor_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df

    except FileNotFoundError:
        return pd.DataFrame()
    except Exception:
        return pd.DataFrame()
        