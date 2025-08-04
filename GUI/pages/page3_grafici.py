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

# Percorso al CSV
current_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
csv_path = os.path.join(project_root, 'feeds.csv')

# Caricamento dati
df = carica_df_sanitizzato(csv_path)

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
    html.H2(),
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
    Input('url', 'search')
)
def mostra_grafico(query_string):
    params = parse.parse_qs(query_string[1:])
    
    # Pulizia avanzata del valore del sensore estratto dalla query string
    sensore = params.get('sensore', [None])[0]
    if isinstance(sensore, str):
        # Normalizza la stringa per rimuovere caratteri di codifica non standard
        sensore = sensore.strip().encode('utf-8').decode('utf-8', 'ignore')

    # DEBUG: Stampa il valore pulito del sensore per diagnostica
    print(f"DEBUG: Sensore estratto dalla query string e pulito: '{sensore}'")

    sd = params.get('sd', [None])[0]
    ed = params.get('ed', [None])[0]
    sh = params.get('sh', [None])[0]
    sm = params.get('sm', [None])[0]
    eh = params.get('eh', [None])[0]
    em = params.get('em', [None])[0]

    if sensore is None or sensore not in df.columns or df.empty:
        return go.Figure(), f"Errore: il sensore '{sensore}' non è valido o il dataset è vuoto.", ""

    def build_datetime_with_tz(date_str, hour, minute):
        return datetime.strptime(f"{date_str} {hour}:{minute}", "%Y-%m-%d %H:%M")

    try:
        if sd and ed and not any([sh, sm, eh, em]):
            start_dt = build_datetime_with_tz(sd, 0, 0)
            end_dt = build_datetime_with_tz(ed, 23, 59)
        else:
            sh = int(sh) if sh else 0
            sm = int(sm) if sm else 0
            eh = int(eh) if eh else 0
            em = int(em) if em else 0

            if ed and not (eh or em):
                eh, em = 23, 59

            start_dt = build_datetime_with_tz(sd, sh, sm)
            end_dt = build_datetime_with_tz(ed, eh, em)
    except Exception:
        return go.Figure(), "Errore nel formato di data o orario.", ""
    
    print(f"DEBUG: Filtering with interval: {start_dt} to {end_dt}")

    df_filtered = df[(df['created_at'] >= start_dt) & (df['created_at'] <= end_dt)]
    
    print(f"DEBUG: Found {len(df_filtered)} rows in the selected interval.")

    if df_filtered.empty:
        return go.Figure(), "Nessun dato trovato nell'intervallo selezionato.", ""

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
        title=f'Time Series - {label_sensore}',
        xaxis_title='Date',
        yaxis_title='Values',
        template='plotly_white',
        margin=dict(l=20, r=20, t=50, b=20),
        title_font_size=20,
        xaxis=dict(title_font_size=14, tickfont_size=10),
        yaxis=dict(title_font_size=14, tickfont_size=10)
    )

    fig.update_xaxes(
        tickformat='%d %b %y',
        tickangle=0
    )

    intervallo_testo = f"Intervallo selezionato: {start_dt.strftime('%d/%m/%Y %H:%M')} → {end_dt.strftime('%d/%m/%Y %H:%M')}"
    return fig, "", intervallo_testo