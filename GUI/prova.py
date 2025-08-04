import pandas as pd
import os

# Imposta il path alla root del progetto
project_root = os.path.dirname(os.path.abspath(__file__))

# Cambia qui se vuoi testare altri file
csv_path = os.path.join(project_root, 'm4w_Villaverla.csv')

print(f"✅ CSV path: {csv_path}")

# STEP 1 - Mostra le prime due righe raw (senza parse_dates)
try:
    df_preview = pd.read_csv(csv_path, nrows=2)
    print("\n📌 Colonne trovate:")
    print(df_preview.columns.tolist())
    print("\n📌 Prime due righe del file:")
    print(df_preview.head())
except Exception as e:
    print("\n❌ Errore durante la lettura iniziale del CSV:")
    print(str(e))

# STEP 2 - Prova a leggere con parse_dates
try:
    df_full = pd.read_csv(csv_path, parse_dates=['created_at'])
    print("\n✅ Lettura con parse_dates riuscita!")
    print("📌 Tipo della colonna 'created_at':", df_full['created_at'].dtype)
    print("📌 Prime righe:")
    print(df_full[['created_at']].head())
except ValueError as ve:
    print("\n❌ Errore con parse_dates=['created_at']:")
    print(str(ve))
except Exception as e:
    print("\n❌ Altro errore:")
    print(str(e))
