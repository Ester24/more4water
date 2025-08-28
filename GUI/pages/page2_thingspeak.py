import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from io import StringIO
from data_loader import carica_df_thingspeak

# Mappa dei nomi dei sensori per una migliore leggibilità
SENSOR_NAMES = {
    'field1': 'Null',
    'field2': 'Null',
    'field3': 'Water Level',
    'field4': 'Null',
    'field5': 'Null',
    'field6': 'Null',
    'field7': 'Temperature'
}

# Registra la pagina con il router di Dash
dash.register_page(__name__, path='/thingspeak', title='Real-Time Data')

# Intervallo di aggiornamento del grafico (in millisecondi)
# Impostato a 20 secondi per allinearsi al canale ThingSpeak
REFRESH_INTERVAL = 20 * 1000
#1800 * 1000

# --- LAYOUT DELLA PAGINA ---
layout = html.Div(
    className="container mt-4",
    children=[
        html.H1("Real-Time Data from ThingSpeak", className="text-center mb-4"),
        
        # Menu a tendina per la selezione del sensore
        html.Div(
            className="d-flex justify-content-center",
            children=[
                html.Label("Select Sensor:", className="me-2 align-self-center"),
                dcc.Dropdown(
                    id='thingspeak-sensor-dropdown',
                    options=[],
                    placeholder="Select a sensor",
                    className="w-50",
                    style={'width': '300px'},
                    clearable=False
                )
            ]
        ),
        
        # Grafico che verrà aggiornato
        dcc.Graph(id='thingspeak-live-graph'),
        
        # Componente dcc.Store per memorizzare i dati
        dcc.Store(id='thingspeak-data-store'),
        
        # Componente dcc.Interval per l'aggiornamento automatico
        dcc.Interval(
            id='interval-component',
            interval=REFRESH_INTERVAL,
            n_intervals=0
        ),
        
        # # Pulsante di aggiornamento manuale (opzionale)
        # dbc.Button(
        #     "Refresh Now", 
        #     id="refresh-button", 
        #     color="primary", 
        #     className="mt-3"
        # ),

        # Bottone "Torna alla Home"
        html.Div(
            html.A(
                "Back to Selection", 
                href="/scelta", 
                id="back-to-home-thingspeak", 
                className="btn btn-secondary mt-4"
            ),
            className="text-center"
        ),
    ]
)

# --- CALLBACK PER CARICARE E AGGIORNARE I DATI ---
@dash.callback(
    Output('thingspeak-data-store', 'data'),
    Output('thingspeak-sensor-dropdown', 'options'),
    Input('interval-component', 'n_intervals'),
    # Input('refresh-button', 'n_clicks')
)
def update_data_and_options(n_intervals):
    """
    Carica i dati da ThingSpeak e aggiorna lo Store e le opzioni del dropdown.
    """
    df = carica_df_thingspeak()
    
    if df.empty:
        return {}, []
        
    sensori = [col for col in df.columns if col.startswith('field')]
    opzioni = [{'label': SENSOR_NAMES.get(s, s), 'value': s} for s in sensori]
    
    return df.to_json(date_format='iso', orient='split'), opzioni

# --- CALLBACK PER MANTENERE LA SELEZIONE DEL SENSORE ---
@dash.callback(
    Output('thingspeak-sensor-dropdown', 'value'),
    Input('thingspeak-sensor-dropdown', 'options'),
    State('thingspeak-sensor-dropdown', 'value')
)
def set_default_sensor(options, current_value):
    """
    Imposta il valore predefinito solo se non è già stato selezionato un sensore.
    """
    if current_value:
        return current_value
    if options:
        return options[0]['value']
    return None

# --- CALLBACK PER AGGIORNARE IL GRAFICO ---
@dash.callback(
    Output('thingspeak-live-graph', 'figure'),
    Input('thingspeak-data-store', 'data'),
    Input('thingspeak-sensor-dropdown', 'value')
)
def update_graph(data_json, selected_sensor):
    """
    Questa callback prende i dati dallo Store e aggiorna il grafico.
    """
    if not data_json or not selected_sensor:
        return {}
    
    df = pd.read_json(StringIO(data_json), orient='split')
    
    fig = px.line(df, x='created_at', y=selected_sensor)
    
    # Etichette degli assi ripristinate
    fig.update_layout(
        xaxis_title="Date and Time (Europe/Rome)", 
        yaxis_title=SENSOR_NAMES.get(selected_sensor, selected_sensor),
        title=f'Time trend of {SENSOR_NAMES.get(selected_sensor, selected_sensor)}'
    )
    
    # Mantiene il tooltip pulito
    fig.update_traces(
        hovertemplate='Date: %{x}<br>Value: %{y}<extra></extra>'
    )
    
    return fig