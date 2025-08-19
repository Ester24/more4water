import csv
from datetime import datetime
import os
from io import StringIO
import math # Importiamo la libreria math per il troncamento

def carica_df_sanitizzato(percorso_csv):
    """
    Legge, pulisce e parsa il file CSV usando solo librerie standard di Python.
    Restituisce una lista di dizionari con date senza fuso orario.
    """
    try:
        if not os.path.exists(percorso_csv):
            print(f"File non trovato: {percorso_csv}")
            return []

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
        reader = csv.reader(cleaned_data_io, delimiter=',', quotechar='"')
        dati_letti = list(reader)

        if not dati_letti:
            return []

        header = [col.strip() for col in dati_letti[0]]
        
        dati_sensori = []
        
        for riga in dati_letti[1:]:
            dizionario_riga = {}
            for i, col_name in enumerate(header):
                valore_stringa = riga[i]
                
                try:
                    if col_name == 'created_at':
                        dt_object = datetime.fromisoformat(valore_stringa)
                        dizionario_riga[col_name] = dt_object.replace(tzinfo=None)
                    elif col_name.startswith('field') and col_name[5:].isdigit():
                        valore_float = float(valore_stringa)
                        # NUOVA MODIFICA: Troncamento alla seconda cifra decimale
                        valore_troncato = math.trunc(valore_float * 100) / 100.0
                        dizionario_riga[col_name] = valore_troncato
                    else:
                        dizionario_riga[col_name] = valore_stringa
                except (ValueError, IndexError):
                    dizionario_riga[col_name] = None

            dati_sensori.append(dizionario_riga)

        return dati_sensori

    except Exception as e:
        print(f"Si è verificato un errore in carica_df_sanitizzato: {e}")
        return []