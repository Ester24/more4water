import dash
from dash import dcc, html, Input, Output
from urllib import parse
import pandas as pd
import plotly.graph_objs as go
from datetime import datetime, timezone, timedelta
import os
from data_loader import carica_df_sanitizzato

# Registra la pagina Dash con path e titolo
dash.register_page(__name__, path='/grafici', title='View Charts')

# Percorso alla cartella principale del progetto
current_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))

# --- RIMOZIONE: Il DataFrame non viene più caricato all'avvio ---
# Il caricamento verrà fatto all'interno della callback.

# Dizionario per mappare nomi sensori più leggibili
sensor_labels = {
    'field1': 'Sensor 1',
    'field2': 'Sensor 2',
    'field3': 'Sensor 3',
    'field4': 'Sensor 4',
    'field5': 'Sensor 5',
    'field6': 'Sensor 6',
    'field7': 'Sensor 7',
}

layout = html.Div([
    html.H2(id='graph-title', style={'textAlign': 'center'}),
    dcc.Graph(
        id='sensore-graph',
        config={
            'responsive': True,
            'displayModeBar': False
        },
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
    'width': '100%',
    'height': 'auto',
    'margin': '0 auto',
    'padding': '0',
    'boxSizing': 'border-box',
    'display': 'flex',
    'flexDirection': 'column',
    'justifyContent': 'flex-start',
    'backgroundColor': 'transparent',
})

@dash.callback(
    Output('sensore-graph', 'figure'),
    Output('error-message', 'children'),
    Output('selected-dates', 'children'),
    Output('graph-title', 'children'),
    Input('url', 'search')
)
def mostra_grafico(query_string):
    if not query_string:
        return go.Figure(), "Nessun parametro di ricerca trovato. Torna alla pagina di selezione per inserire i dati.", "", ""

    params = parse.parse_qs(query_string[1:])
    
    file_selezionato = params.get('file', [None])[0]
    if not file_selezionato:
        return go.Figure(), "Errore: nome del file non specificato nella query.", "", ""
    
    csv_path = os.path.join(project_root, file_selezionato)
    
    # --- MODIFICA QUI: Convertiamo la lista in un DataFrame ---
    dati_sensori = carica_df_sanitizzato(csv_path)
    df = pd.DataFrame(dati_sensori)
    
    sensore = params.get('sensore', [None])[0]
    sd = params.get('sd', [None])[0]
    ed = params.get('ed', [None])[0]
    sh = int(params.get('sh', ['0'])[0])
    sm = int(params.get('sm', ['0'])[0])
    eh = int(params.get('eh', ['23'])[0])
    em = int(params.get('em', ['59'])[0])

    if not sensore or not df.columns.isin([sensore]).any() or df.empty:
        return go.Figure(), f"Errore: il sensore '{sensore}' non è valido o il dataset è vuoto per il file '{file_selezionato}'.", "", ""
    
    try:
        start_dt = datetime.strptime(f"{sd} {sh}:{sm}", "%Y-%m-%d %H:%M")
        end_dt = datetime.strptime(f"{ed} {eh}:{em}", "%Y-%m-%d %H:%M")
    except (ValueError, TypeError):
        return go.Figure(), "Errore nel formato di data o orario. Torna indietro e verifica le tue selezioni.", "", ""

    if start_dt > end_dt:
        return go.Figure(), "Errore: la data/ora di inizio deve essere precedente o uguale a quella di fine.", "", ""

    df_filtered = df[(df['created_at'] >= start_dt) & (df['created_at'] <= end_dt)]

    if df_filtered.empty:
        return go.Figure(), "Nessun dato trovato nell'intervallo selezionato. Prova un intervallo diverso.", "", ""

    label_sensore = sensor_labels.get(sensore, sensore)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_filtered['created_at'],
        y=df_filtered[sensore],
        mode='lines+markers',
        name=label_sensore,
        marker=dict(color='RoyalBlue'),
        line=dict(color='RoyalBlue'),
        hovertemplate='Date: %{x|%d %b %Y %H:%M}<br>Value: %{y}<extra></extra>'
    ))

    fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Values',
        template='plotly_white',
        margin=dict(l=20, r=20, t=50, b=20),
        xaxis=dict(title_font_size=14, tickfont_size=10),
        yaxis=dict(title_font_size=14, tickfont_size=10)
    )

    fig.update_xaxes(
        tickformat='%d %b %y',
        tickangle=0
    )

    intervallo_testo = f"Selected interval: {start_dt.strftime('%d/%m/%Y %H:%M')} → {end_dt.strftime('%d/%m/%Y %H:%M')}"
    title_text = f"Time Series - {label_sensore}"

    return fig, "", intervallo_testo, title_text