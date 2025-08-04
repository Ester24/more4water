import dash
from dash import html, dcc, Input, Output
from datetime import datetime, date
import pandas as pd
import os
import dash_bootstrap_components as dbc
from data_loader import carica_df_sanitizzato

dash.register_page(__name__, path='/inserimento', title='Seleziona dati')

# Percorso al CSV
current_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
#csv_path = os.path.join(project_root, 'feeds.csv')
csv_path = os.path.join(project_root, 'm4w_Villaverla.csv')

# Caricamento dati
try:
    df = carica_df_sanitizzato(csv_path)

    if df.empty:
        df_min_date = date(2020, 1, 1)
        df_max_date = date.today()
        sensori = []
    else:
        df_min_date = df['created_at'].min().date()
        df_max_date = df['created_at'].max().date()
        sensori = [f'field{i}' for i in range(1, 8) if f'field{i}' in df.columns]

except FileNotFoundError:
    df = pd.DataFrame()
    df_min_date = date(2020, 1, 1)
    df_max_date = date.today()
    sensori = []

minuti_options = [{'label': '00', 'value': 0}, {'label': '30', 'value': 30}]

# --- LAYOUT COMPLETO ---
layout = html.Div(style={'padding': '20px'}, children=[
    html.Div([
        html.H1("Select Date and Sensor", className="my-custom-h1"),
    ], style={'textAlign': 'center', 'marginTop': '20px'}),

    html.Div(className='sensor-dropdown-container custom-sensor-dropdown', children=[
        dcc.Dropdown(
            id='sensore-dropdown',
            options=[{'label': f"Sensor {i+1}", 'value': s} for i, s in enumerate(sensori)],
            placeholder="Select a sensor",
            className='Select my-sensor-specific-style',
            searchable=False,
            clearable=False
        )
    ]),

    html.Div(className='datetime-sections-wrapper', children=[
        html.Div(className='datetime-container', children=[
            html.Label("Start Date", className='date-time-label'),
            html.Div(className='date-time-group', children=[
                dcc.DatePickerSingle(
                    id='start-date',
                    placeholder="DD/MM/YYYY",
                    min_date_allowed=df_min_date,
                    max_date_allowed=df_max_date,
                    initial_visible_month=datetime.now().date(),
                    display_format='DD/MM/YYYY',
                    className='SingleDatePickerInput',
                ),
                dcc.Dropdown(
                    id='start-hour',
                    options=[{'label': f"{h:02d}", 'value': h} for h in range(24)],
                    placeholder="Hour",
                    className='uniform-input',
                    searchable=False,
                    clearable=False,
                    value=0
                ),
                dcc.Dropdown(
                    id='start-minute',
                    options=minuti_options,
                    placeholder="Min",
                    className='uniform-input',
                    searchable=False,
                    clearable=False,
                    value=0
                )
            ])
        ]),
        html.Div(className='datetime-container', children=[
            html.Label("End Date", className='date-time-label'),
            html.Div(className='date-time-group', children=[
                dcc.DatePickerSingle(
                    id='end-date',
                    placeholder="DD/MM/YYYY",
                    min_date_allowed=df_min_date,
                    max_date_allowed=df_max_date,
                    initial_visible_month=datetime.now().date(),
                    display_format='DD/MM/YYYY',
                    className='SingleDatePickerInput',
                ),
                dcc.Dropdown(
                    id='end-hour',
                    options=[{'label': f"{h:02d}", 'value': h} for h in range(24)],
                    placeholder="Hour",
                    className='uniform-input',
                    searchable=False,
                    clearable=False,
                    value=23
                ),
                dcc.Dropdown(
                    id='end-minute',
                    options=minuti_options,
                    placeholder="Min",
                    className='uniform-input',
                    searchable=False,
                    clearable=False,
                    value=30
                )
            ])
        ])
    ]),

    html.Div(id='selection-error-message', style={'color': 'red', 'textAlign': 'center', 'marginBottom': '20px'}),

    html.Div([
        html.Div(id='link-container'),
        dbc.Button("Back to Home", href="/", color="primary", style={'fontWeight': 'bold'})
    ], style={
        'display': 'flex',
        'justifyContent': 'center',
        'alignItems': 'center',
        'gap': '20px',
        'marginTop': '20px'
    }),
])
# --- FINE LAYOUT ---

# --- CALLBACK PER GENERARE IL LINK ---
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
    link_output = None
    error_message = ""

    if not sensore or not sd or not ed:
        error_message = "Please select a sensor and both start and end dates."
        return link_output, error_message

    sh = sh if sh is not None else 0
    sm = sm if sm is not None else 0
    eh = eh if eh is not None else 23
    em = em if em is not None else 30

    try:
        start_dt = datetime.strptime(sd, '%Y-%m-%d').replace(hour=sh, minute=sm)
        end_dt = datetime.strptime(ed, '%Y-%m-%d').replace(hour=eh, minute=em)
    except Exception:
        error_message = "Invalid date or time format. Please check your selections."
        return link_output, error_message

    if start_dt > end_dt:
        error_message = "Error: start date/time must be before or equal to end date/time."
        return link_output, error_message

    query = f"?sensore={sensore}&sd={sd}&sh={sh}&sm={sm}&ed={ed}&eh={eh}&em={em}"
    link_output = dcc.Link(
        dbc.Button("Generate Graph", color="success", className="me-1"),
        href=f"/grafici{query}"
    )

    return link_output, error_message