import dash
from dash import html, dcc, Input, Output
from datetime import datetime, date
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

# --- INIZIO DEL LAYOUT CORRETTO E AGGIORNATO ---
layout = html.Div(style={'padding': '20px'}, children=[
    html.Div(
        html.H1("Select Date and Sensor", className="my-custom-h1"),
        id="h1-title-wrapper"
    ),

    html.Div(className='sensor-dropdown-container', children=[
        dcc.Dropdown(
            id='sensore-dropdown',
            options=[{'label': s, 'value': s} for s in sensori],
            placeholder="Select a sensor",
            className='Select', # Manteniamo 'Select' per il CSS specifico del sensore
            searchable=False,   # <--- ESSENZIALE: Disabilita la ricerca testuale
            clearable=False     # <--- OPZIONALE: Impedisce di deselezionare
        )
    ]),

    html.Div(className='datetime-sections-wrapper', children=[
        html.Div(className='datetime-container', children=[
            html.Label("Start Date", className='date-time-label'),
            html.Div(className='date-time-group', children=[
                dcc.DatePickerSingle(
                    id='start-date',
                    placeholder="DD/MM/YYYY",
                    min_date_allowed=df['created_at'].min().date() if not df.empty else date(2020,1,1),
                    max_date_allowed=df['created_at'].max().date() if not df.empty else date.today(),
                    display_format='DD/MM/YYYY',
                    className='SingleDatePickerInput',
                    
                ),
                dcc.Dropdown(
                    id='start-hour',
                    options=[{'label': f"{h:02d}", 'value': h} for h in range(24)],
                    placeholder="Hour",
                    className='uniform-input', # Mantenuto per coerenza CSS
                    searchable=False, # <--- ESSENZIALE per i dropdown di ore/minuti
                    clearable=False   # <--- OPZIONALE
                ),
                dcc.Dropdown(
                    id='start-minute',
                    options=minuti_options,
                    placeholder="Min",
                    className='uniform-input', # Mantenuto per coerenza CSS
                    searchable=False, # <--- ESSENZIALE per i dropdown di ore/minuti
                    clearable=False   # <--- OPZIONALE
                )
            ])
        ]),
        html.Div(className='datetime-container', children=[
            html.Label("End Date", className='date-time-label'),
            html.Div(className='date-time-group', children=[
                dcc.DatePickerSingle(
                    id='end-date',
                    placeholder="DD/MM/YYYY",
                    min_date_allowed=df['created_at'].min().date() if not df.empty else date(2020,1,1),
                    max_date_allowed=df['created_at'].max().date() if not df.empty else date.today(),
                    display_format='DD/MM/YYYY',
                    className='SingleDatePickerInput',
                    
                ),
                dcc.Dropdown(
                    id='end-hour',
                    options=[{'label': f"{h:02d}", 'value': h} for h in range(24)],
                    placeholder="Hour",
                    className='uniform-input',
                    searchable=False, # <--- ESSENZIALE per i dropdown di ore/minuti
                    clearable=False   # <--- OPZIONALE
                ),
                dcc.Dropdown(
                    id='end-minute',
                    options=minuti_options,
                    placeholder="Min",
                    className='uniform-input',
                    searchable=False, # <--- ESSENZIALE per i dropdown di ore/minuti
                    clearable=False   # <--- OPZIONALE
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
    # Inizialmente non c'è link e non c'è errore
    link_output = None # o html.Div()
    error_message = ""

    if not sensore:
        error_message = "Please select a sensor."
        return link_output, error_message

    if not sd or not ed:
        error_message = "Specify start and end dates."
        return link_output, error_message

    sh = sh if sh is not None else 0
    sm = sm if sm is not None else 0
    eh = eh if eh is not None else 0
    em = em if em is not None else 0

    try:
        start_dt = datetime.strptime(sd, '%Y-%m-%d').replace(hour=sh, minute=sm)
        end_dt = datetime.strptime(ed, '%Y-%m-%d').replace(hour=eh, minute=em)
    except Exception as e:
        # Stampa l'errore per il debug nel terminale del server
        print(f"Error parsing date/time: {e}")
        error_message = "Invalid date or time format. Please check your selections."
        return link_output, error_message

    if start_dt > end_dt:
        error_message = "Error: start date/time must be before or equal to end date/time."
        return link_output, error_message

    # Se tutti i controlli passano, crea il link
    query = f"?sensore={sensore}&sd={sd}&sh={sh}&sm={sm}&ed={ed}&eh={eh}&em={em}"
    link_output = dcc.Link("Generate Graph", href=f"/grafici{query}", style={
        'fontSize': '20px', 'fontWeight': 'bold', 'textDecoration': 'none', 'color': 'white',
        'backgroundColor': '#007bff', 'padding': '10px 20px', 'borderRadius': '5px'
    })

    return link_output, error_message


