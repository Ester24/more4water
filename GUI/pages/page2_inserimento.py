import dash
from dash import html, dcc, Input, Output
from datetime import datetime
import pandas as pd
import os
import dash_bootstrap_components as dbc

dash.register_page(__name__, path='/inserimento', title='Seleziona dati')

# Carica dati
current_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
csv_path = os.path.join(project_root, 'feeds.csv')

df = pd.read_csv(csv_path, parse_dates=['created_at'])
df['created_at'] = df['created_at'].dt.tz_localize(None)

sensori = [f'field{i}' for i in range(1, 8) if f'field{i}' in df.columns]

minuti_options = [{'label': '00', 'value': 0}, {'label': '30', 'value': 30}]

layout = html.Div([
    html.H1("Select Data and Sensor", style={'textAlign': 'center', 'marginBottom': '30px'}),

    # Dropdown sensore centrato
    html.Div([
        dcc.Dropdown(
            id='sensore-dropdown',
            options=[{'label': s, 'value': s} for s in sensori],
            placeholder="Select a sensor",
            style={'width': '300px'}
        )
    ], style={'display': 'flex', 'justifyContent': 'center', 'marginBottom': '40px'}),

    # Blocchi Data Inizio e Data Fine affiancati e centrati
    html.Div([
        # Blocco Data Inizio
        html.Div([
            html.Label("Start Date", style={'marginBottom': '5px'}),
            html.Div([
                dcc.DatePickerSingle(
                    id='start-date',
                    placeholder="DD/MM/YYYY",
                    min_date_allowed=df['created_at'].min().date(),
                    max_date_allowed=df['created_at'].max().date(),
                    display_format='DD/MM/YYYY',
                    style={'width': '150px'}
                ),
                dcc.Dropdown(
                    id='start-hour',
                    options=[{'label': f"{h:02d}", 'value': h} for h in range(24)],
                    placeholder="Hour",
                    style={'width': '80px'}
                ),
                dcc.Dropdown(
                    id='start-minute',
                    options=minuti_options,
                    placeholder="Min",
                    style={'width': '80px'}
                )
            ], style={'display': 'flex', 'gap': '10px'})
        ], style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center'}),

        # Blocco Data Fine
        html.Div([
            html.Label("End Date", style={'marginBottom': '5px'}),
            html.Div([
                dcc.DatePickerSingle(
                    id='end-date',
                    placeholder="DD/MM/YYYY",
                    min_date_allowed=df['created_at'].min().date(),
                    max_date_allowed=df['created_at'].max().date(),
                    display_format='DD/MM/YYYY',
                    style={'width': '150px'}
                ),
                dcc.Dropdown(
                    id='end-hour',
                    options=[{'label': f"{h:02d}", 'value': h} for h in range(24)],
                    placeholder="Hour",
                    style={'width': '80px'}
                ),
                dcc.Dropdown(
                    id='end-minute',
                    options=minuti_options,
                    placeholder="Min",
                    style={'width': '80px'}
                )
            ], style={'display': 'flex', 'gap': '10px'})
        ], style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center'})
    ], style={'display': 'flex', 'justifyContent': 'center', 'gap': '60px', 'marginBottom': '30px'}),

    html.Div([
    html.Div(id='link-container'),
    dbc.Button("Back to Home", href="/", color="primary", style={'fontWeight': 'bold'})
], style={
    'display': 'flex',
    'justifyContent': 'center',
    'alignItems': 'center',
    'gap': '20px',
    'marginTop': '30px'
}),

html.Div(id='selection-error-message', style={'color': 'red', 'textAlign': 'center', 'marginTop': '10px'}),

   
])


@dash.callback(
    Output('link-container', 'children'),
    Output('selection-error-message', 'children'),
    Input('sensore-dropdown', 'value'),
    Input('start-date', 'date'),
    Input('start-hour', 'value'),
    Input('start-minute', 'value'),
    Input('end-date', 'date'),
    Input('end-hour', 'value'),
    Input('end-minute', 'value'),
)
def genera_link(sensore, sd, sh, sm, ed, eh, em):
    if not sensore:
        return "", "Please select a sensor."
    if not sd or not ed:
        return "", "Specify start and end dates."

    sh = sh if sh is not None else 0
    sm = sm if sm is not None else 0
    eh = eh if eh is not None else 0
    em = em if em is not None else 0

    try:
        start_dt = datetime.strptime(sd, '%Y-%m-%d').replace(hour=sh, minute=sm)
        end_dt = datetime.strptime(ed, '%Y-%m-%d').replace(hour=eh, minute=em)
    except Exception:
        return "", "Invalid date or time format."

    if start_dt > end_dt:
        return "", "Error: start date/time must be before or equal to end date/time."

    query = f"?sensore={sensore}&sd={sd}&sh={sh}&sm={sm}&ed={ed}&eh={eh}&em={em}"
    link = dcc.Link("Generate Graph", href=f"/grafici{query}", style={
        'fontSize': '20px', 'fontWeight': 'bold', 'textDecoration': 'none', 'color': 'white',
        'backgroundColor': '#007bff', 'padding': '10px 20px', 'borderRadius': '5px'
    })

    return link, ""






