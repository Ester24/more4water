import pandas as pd

def carica_df_sanitizzato(percorso_csv):
    try:
        # Tenta di caricare il CSV con parametri robusti
        df = pd.read_csv(
            percorso_csv,
            sep=",",
            quotechar='"',
            engine='python',
            skipinitialspace=True
        )

        # DEBUG: Stampa i nomi delle colonne appena lette
        print("DEBUG: Colonne lette dopo pd.read_csv:", df.columns.tolist())

        # Rimuove gli spazi bianchi iniziali/finali dai nomi delle colonne
        df.columns = df.columns.str.strip()

        # DEBUG: Stampa i nomi delle colonne dopo la pulizia
        print("DEBUG: Colonne dopo la pulizia:", df.columns.tolist())

        if 'created_at' not in df.columns:
            print("ERRORE: La colonna 'created_at' non è presente nel CSV.")
            print("Colonne trovate:", df.columns.tolist())
            return pd.DataFrame()

        # Parsing esplicito con formato ISO 8601 + offset
        df['created_at'] = pd.to_datetime(df['created_at'], format="%Y-%m-%dT%H:%M:%S%z", errors='coerce')
        df.dropna(subset=['created_at'], inplace=True)

        if not df.empty:
            # Rimuovi il timezone dopo averlo convertito in UTC
            df['created_at'] = df['created_at'].dt.tz_convert('UTC').dt.tz_localize(None)
            
            # DEBUG: Controlla se la colonna 'field7' è presente dopo la pulizia
            if 'field7' in df.columns:
                print("DEBUG: La colonna 'field7' è presente nel DataFrame sanificato.")
            else:
                print("ERRORE DI PARSING: 'field7' non è stato trovato dopo la sanificazione. Rivedere il file CSV.")


        return df

    except FileNotFoundError:
        print(f"Errore: Il file CSV non è stato trovato al percorso {percorso_csv}")
        return pd.DataFrame()


