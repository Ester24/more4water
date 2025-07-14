import dash
from dash import dcc, html, Input, Output
from urllib import parse
import pandas as pd
import plotly.graph_objs as go
from datetime import datetime
import os

# Registra la pagina Dash con path e titolo
dash.register_page(__name__, path='/grafici', title='View Charts')

# Percorso assoluto del file CSV
current_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
csv_path = os.path.join(project_root, 'feeds.csv')

# Carica il dataset
df = pd.read_csv(csv_path, parse_dates=['created_at'])
df['created_at'] = df['created_at'].dt.tz_localize(None)

# Dizionario per mappare nomi sensori più leggibili
sensor_labels = {
    'field1': 'Sconosciuto',
    'field2': 'Sconosciuto',
    'field3': 'Sconosciuto',
    'field4': 'Sconosciuto',
    'field5': 'Sconosciuto',
    'field6': 'Sconosciuto',
    'field7': 'Temperature',
}

layout = html.Div([
    html.H2(),

    dcc.Graph(
        id='sensore-graph',
        style={
            'width': '100%',
            'height': '400px',
            'maxWidth': '1000px',
            'margin': '0 auto'
        }
    ),

    html.Div(id='error-message', style={'color': 'red', 'textAlign': 'center', 'marginTop': '10px'}),

    html.Div(id='selected-dates', style={'textAlign': 'center', 'marginTop': '10px', 'fontWeight': 'bold'}),

    html.Div(
        dcc.Link("Back to selection", href="/inserimento", className="btn btn-secondary"),
        style={'textAlign': 'center', 'marginTop': '20px'}
    ),

    dcc.Location(id='url', refresh=False)
], style={
    'width': '1000px',
    'height': '600px',
    'margin': '0 auto',
    'padding': '0',  # niente padding
    'boxSizing': 'border-box',
    'overflow': 'hidden',
    'display': 'flex',
    'flexDirection': 'column',
    'justifyContent': 'flex-start',
    'backgroundColor': 'transparent',  # nessuno sfondo
})




@dash.callback(
    Output('sensore-graph', 'figure'),
    Output('error-message', 'children'),
    Output('selected-dates', 'children'),
    Input('url', 'search')
)
def mostra_grafico(query_string):
    # Parsing parametri URL
    params = parse.parse_qs(query_string[1:])
    sensore = params.get('sensore', [None])[0]
    sd = params.get('sd', [None])[0]
    sh = int(params.get('sh', [0])[0])
    sm = int(params.get('sm', [0])[0])
    ed = params.get('ed', [None])[0]
    eh = int(params.get('eh', [0])[0])
    em = int(params.get('em', [0])[0])

    # Verifica sensore valido
    if sensore is None or sensore not in df.columns:
        return go.Figure(), f"Errore: sensore '{sensore}' non valido.", ""

    # Costruzione datetime
    def build_datetime(date_str, hour, minute):
        return datetime.strptime(date_str, '%Y-%m-%d').replace(hour=hour, minute=minute)

    start_dt = build_datetime(sd, sh, sm)
    end_dt = build_datetime(ed, eh, em)

    # Filtro dati
    df_filtered = df[(df['created_at'] >= start_dt) & (df['created_at'] <= end_dt)]

    if df_filtered.empty:
        return go.Figure(), "Nessun dato disponibile per l'intervallo selezionato.", ""

    # Etichetta sensore leggibile
    label_sensore = sensor_labels.get(sensore, sensore)

    # Costruzione grafico
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_filtered['created_at'],
        y=df_filtered[sensore],
        mode='lines+markers',
        name=label_sensore,
        marker=dict(color='RoyalBlue'),
        line=dict(color='RoyalBlue'),
        hovertemplate='Data: %{x}<br>Valore: %{y}<extra></extra>'
    ))


    # Layout grafico
    fig.update_layout(
    title=f'{label_sensore} Time Series',
    xaxis_title='Timestamp',
    yaxis_title='Values',
    template='plotly_white'
    )


    intervallo_testo = f"Intervallo selezionato: {start_dt.strftime('%d/%m/%Y %H:%M')} → {end_dt.strftime('%d/%m/%Y %H:%M')}"


    return fig, "", intervallo_testo


