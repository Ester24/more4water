# More4Water_GUI

Progetto GUI per il monitoraggio di sensori nella rete idrica e sistema di segnalazione guasti.

## 📋 Obiettivi del Progetto

Questo progetto è suddiviso in due step principali:

### **Step 1**: Visualizzazione Dati da CSV
- Creazione di una GUI per visualizzare i dati dei sensori salvati in file CSV
- Implementazione di un sistema di segnalazione guasti per la rete idrica
- Gestione utenti e segnalazioni tramite database SQLite3

### **Step 2**: Grafici Live con API
- Integrazione con API ThingSpeak per dati in tempo reale
- Visualizzazione di grafici live aggiornati automaticamente
- Espansione del sistema di monitoraggio

## 🛠️ Tecnologie Utilizzate

- **Python**: Linguaggio principale per frontend, backend e gestione dati
- **Plotly Dash**: Framework per la creazione della GUI web interattiva
- **SQLite3**: Database locale per gestione utenti e segnalazioni
- **Pandas**: Manipolazione e analisi dei dati CSV
- **ThingSpeak API**: Servizio IoT per dati in tempo reale (Step 2)

## 📚 Documentazione di Riferimento

### Plotly & Dash
- [Documentazione Plotly](https://plotly.com/python/)
- [Documentazione Dash](https://dash.plotly.com/)
- [Tutorial Dash per principianti](https://dash.plotly.com/tutorial)
- [Galleria esempi Dash](https://dash-gallery.plotly.host/Portal/)

### Database
- [Documentazione SQLite3 Python](https://docs.python.org/3/library/sqlite3.html)
- [Tutorial SQLite](https://www.sqlitetutorial.net/)

### API e Dati
- [ThingSpeak API Documentation](https://it.mathworks.com/help/thingspeak/)
- [ThingSpeak python API library (da testare)](https://pypi.org/project/thingspeak/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)

## 🔧 Setup Ambiente di Sviluppo

### Estensioni VS Code Consigliate:

- **Python**: Supporto completo per Python (syntax highlighting, debugging, IntelliSense)
- **Python Environment**: Gestione degli ambienti virtuali Python
- **VSCode-icons**: Icone per una migliore organizzazione dei file nel workspace
- **Python Debugger**: Strumenti avanzati per il debugging del codice Python
- **Data Wrangler**: Visualizzazione e manipolazione interattiva dei dataset
- **Pylance**: Language server avanzato per Python (completamento automatico, type checking)

### Creazione Ambiente Virtuale con VS Code

1. **Apri VS Code** nella cartella del progetto
2. **Apri il Command Palette** (`Ctrl+Shift+P`)
3. **Cerca e seleziona**: `Python: Create Environment`
4. **Seleziona**: `Venv` 
5. **Scegli l'interprete Python** (solitamente l'ultima versione installata)
6. VS Code creerà automaticamente la cartella `venv` e la attiverà

**Riferimenti utili**:
- [Guida ufficiale VS Code - Python environments](https://code.visualstudio.com/docs/python/environments)
- [Tutorial creazione venv in VS Code](https://code.visualstudio.com/docs/python/tutorial-django#_create-a-project-environment-for-the-django-tutorial)

### Creazione File Requirements

**IMPORTANTE**: Il file `requirements.txt` non esiste ancora nel repository. Dovrai crearlo tu seguendo questi passi:

1. **Crea il file** `requirements.txt` nella root del progetto
2. **Aggiungi le dipendenze** necessarie:

```txt
dash
plotly
pandas
requests
dash-bootstrap-components
```

3. **Installa le dipendenze**:
```bash
pip install -r requirements.txt
```

**Nota**: Le versioni potrebbero cambiare nel tempo. Usa `pip freeze > requirements.txt` dopo aver installato tutto per salvare le versioni esatte.

## 📁 Struttura del Progetto

```
More4Water_GUI/
├── GUI/
│   ├── app.py                 # Applicazione principale Dash
│   ├── assets/
│   │   └── Style.css          # Stili CSS personalizzati
│   ├── components/
│   │   ├── __init__.py
│   │   └── shared_components.py
│   └── pages/
│       ├── __init__.py
│       ├── page1_home.py      # Homepage
│       ├── page2_eis.py       # Pagina visualizzazione dati
│       ├── page3_running.py   # Pagina monitoraggio live
│       └── page4_results.py   # Pagina risultati e segnalazioni
├── data/                      # Cartella per file CSV
├── database/                  # Database SQLite
├── config/                    # File di configurazione
└── docs/                      # Documentazione aggiuntiva
```

## 🚀 Getting Started

### Prerequisiti
- **GitHub Desktop**: Scarica e installa [GitHub Desktop](https://desktop.github.com/) per una gestione semplificata del repository
- **Python 3.8+**: Assicurati di avere Python installato sul sistema
- **VS Code**: Con le estensioni Python consigliate

### Setup Progetto

1. **Clona il repository**:
   - Apri GitHub Desktop
   - Clicca su `Clone a repository from the Internet`
   - Inserisci l'URL: `https://github.com/electrical-and-electronic-measurement/More4Water_GUI.git`
   - Scegli la cartella locale dove salvare il progetto
   - Clicca `Clone`

2. **Apri il progetto in VS Code**:
   - In GitHub Desktop, clicca su `Open in Visual Studio Code`
   - Oppure apri VS Code e usa `File > Open Folder`

3. **Crea l'ambiente virtuale** (vedi sezione precedente)

4. **Crea e installa le dipendenze**:
   - Crea il file `requirements.txt` (vedi sezione precedente)
   - Nel terminale integrato di VS Code:
   ```bash
   pip install -r requirements.txt
   ```

5. **Avvia l'applicazione**:
   ```bash
   python GUI/app.py
   ```

## 💾 Gestione Database

Il progetto utilizza SQLite3 per:
- **Tabella Utenti**: Gestione degli utenti del sistema
- **Tabella Segnalazioni**: Log delle segnalazioni di guasti
- **Tabella Sensori**: Metadata dei sensori monitorati

### Schema Database Esempio:
```sql
-- Tabella Utenti
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabella Segnalazioni
CREATE TABLE reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    sensor_id TEXT,
    issue_type TEXT NOT NULL,
    description TEXT,
    priority INTEGER DEFAULT 1,
    status TEXT DEFAULT 'open',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);
```

## 📊 Gestione Dati CSV

I file CSV dovranno contenere almeno le seguenti colonne:
- `timestamp`: Data e ora della misurazione
- `sensor_id`: Identificativo del sensore
- `value`: Valore misurato
- `unit`: Unità di misura
- `status`: Stato del sensore (OK, WARNING, ERROR)

## 🌐 Integrazione ThingSpeak (Step 2)

Per il Step 2, sarà necessario:
1. Creare un account ThingSpeak
2. Configurare i canali per i sensori
3. Ottenere le API Keys
4. Implementare il polling automatico dei dati

## ⚠️ Importante: Gestione GitHub

**ATTENZIONE**: Non abbiamo GitHub Pro, quindi:
- ❌ **NON caricare file di grandi dimensioni** (>100MB)
- ❌ **NON usare GitHub come Onedrive**
- ✅ Utilizzare `.gitignore` per escludere:
  - File di dati CSV di grandi dimensioni
  - Database SQLite con molti record
  - Cache e file temporanei
  - Ambienti virtuali (`venv/`)

### File .gitignore Consigliato:
```
# Dati e Database
data/*.csv
database/*.db
*.sqlite
*.sqlite3

# Ambiente Python
venv/
__pycache__/
*.pyc
*.pyo

# IDE
.vscode/settings.json
.idea/

# File temporanei
*.tmp
*.log
temp/
```

## 📈 Roadmap Sviluppo

### Step 1 (Priorità Alta):
- [ ] Setup base dell'applicazione Dash
- [ ] Implementazione lettura CSV
- [ ] Creazione database SQLite
- [ ] Sistema di autenticazione utenti
- [ ] Form per segnalazione guasti
- [ ] Dashboard di visualizzazione dati

### Step 2 (Priorità Media):
- [ ] Integrazione API ThingSpeak
- [ ] Grafici live in tempo reale
- [ ] Sistema di notifiche
- [ ] Dashboard amministratore
- [ ] Export report in PDF

## 👥 Supporto e Risorse

- **GitHub Desktop**: Per gestione semplificata del repository - [Download](https://desktop.github.com/)
- **Stack Overflow**: Per problemi tecnici specifici
- **Documentazione ufficiale**: Sempre la fonte più aggiornata
- **GitHub Issues**: Per segnalare bug o richiedere funzionalità

## 📄 Report Finale

### Gestione del Report su Overleaf

Link al report finale: [Overleaf Document](https://www.overleaf.com/7962726742ksdbctdgkscm#fb980e)

**IMPORTANTE**: Tieni aggiornato il report durante tutto il percorso di sviluppo!

### Scaletta Consigliata per il Report:

1. **Introduzione**
   - Contesto del progetto More4Water
   - Obiettivi del tirocinio
   - Tecnologie utilizzate

2. **Analisi del Codice Esistente**
   - Struttura iniziale del progetto
   - Funzionalità già implementate
   - Problematiche identificate

3. **Step 1: Visualizzazione Dati CSV**
   - Progettazione dell'interfaccia
   - Implementazione database SQLite
   - Sistema di autenticazione
   - Form segnalazione guasti
   - Problemi incontrati e soluzioni

4. **Step 2: Integrazione API ThingSpeak**
   - Studio delle API ThingSpeak
   - Implementazione grafici live
   - Sistema di notifiche
   - Ottimizzazioni performance

5. **Testing e Debugging**
   - Metodologie di test utilizzate
   - Bug principali e relative correzioni
   - Validazione dell'interfaccia utente

6. **Conclusioni**
   - Obiettivi raggiunti
   - Competenze acquisite
   - Possibili sviluppi futuri
   - Riflessioni sull'esperienza

**Suggerimento**: Aggiorna settimanalmente il report aggiungendo quello che hai fatto, così alla fine dovrai solo riscrivere tutto in modo fluente senza dimenticare nulla!

---

**Nota per la studentessa**: Leggi attentamente questo README prima di iniziare. Familiarizza con le tecnologie elencate e consulta regolarmente la documentazione di riferimento. Ricorda di:
- 📝 **Documentare il tuo lavoro** quotidianamente nel file PRESENZE.md
- 🔄 **Aggiornare il report** settimanalmente su Overleaf
- 💾 **Effettuare commit frequenti** su GitHub Desktop
- 🆘 **Chiedere aiuto** quando necessario - non rimanere bloccata!