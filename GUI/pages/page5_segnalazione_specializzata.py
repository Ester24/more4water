import os
import pandas as pd
import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
from db_utils import insert_report
from export_db_to_csv import esporta_database_in_csv

dash.register_page(__name__, path='/segnalazione_specializzata', title='Insert Report') 

# Percorso e caricamento CSV
current_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
csv_path = os.path.join(project_root, 'feeds.csv')

df = pd.read_csv(csv_path)

# Lista sensori = colonne field1..field7 che esistono
sensori = [f'field{i}' for i in range(1, 8) if f'field{i}' in df.columns]

# --- MODIFICA APPORTATA QUI ---
# Opzioni per il dropdown con etichette personalizzate
dropdown_options = []
for s in sensori:
    try:
        sensor_number = s.replace('field', '')
        # Crea la label nel formato "Sensore X"
        label = f'Sensor {sensor_number}'
        dropdown_options.append({'label': label, 'value': s})
    except (ValueError, IndexError):
        # Gestisce il caso in cui il nome non sia nel formato atteso
        dropdown_options.append({'label': s, 'value': s})
# --------------------------------

layout = dbc.Container([
    html.H2("Submit a New Report"),
    dbc.Form([
        dbc.Label("Report Priority", className="mt-3"), 
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
            placeholder='Select Sensor ID', 
            clearable=False,
        ),

        dbc.Label("Issue Type", className="mt-3"), 
        dcc.Dropdown(
            id='issue_type',
            options=[
                {'label': 'Sensor not responding', 'value': 'sensor_not_responding'},
                {'label': 'Anomalous values', 'value': 'anomalous_values'},
                {'label': 'Low battery', 'value': 'low_battery'},
                {'label': 'Connection issue', 'value': 'connection_issue'},
                {'label': 'Other', 'value': 'other'}
            ],
            placeholder='Select issue type', 
            clearable=False,
        ),

        dbc.Label("Description", className="mt-3"),
        dbc.Textarea(id='description', placeholder='Description (optional)'), 

        dbc.Button("Submit", id='submit_btn', color='primary', className="mt-4"), 

        html.Div(id='output_msg', className='mt-3')
    ])
])


@dash.callback(
    Output('output_msg', 'children'),
    Input('submit_btn', 'n_clicks'),
    State('sensor_id', 'value'),
    State('issue_type', 'value'),
    State('description', 'value'),
    State('priority', 'value'),
)
def submit_report(n_clicks, sensor_id, issue_type, description, priority):
    if not n_clicks:
        return ''
    if not all([sensor_id, issue_type]):
        return dbc.Alert("Sensor ID and Issue Type are mandatory.", color="danger")
    try:
        user_id = None
        # Passo 1: Inserimento del report nel database
        insert_report(user_id, sensor_id, issue_type, description or '', priority or 1)
        
        # Passo 2: Esportazione in CSV
        esporta_database_in_csv()

        return dbc.Alert("Report submitted and data exported to CSV successfully!", color="success")
    except Exception as e:
        return dbc.Alert(f"Error submitting report or exporting data: {str(e)}", color="danger")
