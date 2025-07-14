import os
import pandas as pd
import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
from db_utils import insert_report

dash.register_page(__name__, path='/segnalazione', title='Inserisci Segnalazione')

# Percorso e caricamento CSV
current_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
csv_path = os.path.join(project_root, 'feeds.csv')

df = pd.read_csv(csv_path)  # Se non ti serve la data, puoi togliere parse_dates

# Lista sensori = colonne field1..field7 che esistono
sensori = [f'field{i}' for i in range(1, 8) if f'field{i}' in df.columns]

# Opzioni per il dropdown
dropdown_options = [{'label': s, 'value': s} for s in sensori]

layout = dbc.Container([
    html.H2("Inserisci una nuova segnalazione"),
    dbc.Form([
        dbc.Label("Priorità segnalazione", className="mt-3"),
        dcc.Dropdown(
            id='priority',
            options=[{'label': str(i), 'value': i} for i in range(1, 6)],
            value=1,
            clearable=False,
            style={'width': '100px'}
        ),

        dbc.Label("Sensor ID", className="mt-3"),
        dcc.Dropdown(
            id='sensor_id',
            options=dropdown_options,
            placeholder='Seleziona Sensor ID',
            clearable=False,
        ),

        dbc.Label("Tipo di problema", className="mt-3"),
        dcc.Dropdown(
            id='issue_type',
            options=[
                {'label': 'Sensore non risponde', 'value': 'sensore_non_risponde'},
                {'label': 'Valori anomali', 'value': 'valori_anomali'},
                {'label': 'Batteria scarica', 'value': 'batteria_scarica'},
                {'label': 'Problema di connessione', 'value': 'problema_connessione'},
                {'label': 'Altro', 'value': 'altro'}
            ],
            placeholder='Seleziona tipo di problema',
            clearable=False,
        ),

        dbc.Label("Descrizione", className="mt-3"),
        dbc.Textarea(id='description', placeholder='Descrizione (opzionale)'),



        dbc.Button("Invia", id='submit_btn', color='primary', className="mt-4"),

        html.Div(id='output_msg', className='mt-3')
    ])
])


@dash.callback(
    Output('output_msg', 'children'),
    Input('submit_btn', 'n_clicks'),
    #State('user_id', 'value'),
    State('sensor_id', 'value'),
    State('issue_type', 'value'),
    State('description', 'value'),
    State('priority', 'value'),
)

def submit_report(n_clicks, sensor_id, issue_type, description, priority):
    if not n_clicks:
        return ''
    if not all([sensor_id, issue_type]):
        return dbc.Alert("Sensor ID e Tipo di problema sono obbligatori.", color="danger")
    try:
        user_id = None  # perché non hai ancora login
        insert_report(user_id, sensor_id, issue_type, description or '', priority or 1)
        return dbc.Alert("Segnalazione inserita con successo!", color="success")
    except Exception as e:
        return dbc.Alert(f"Errore: {str(e)}", color="danger")
