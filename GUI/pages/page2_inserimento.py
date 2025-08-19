import dash
from dash import html, dcc, Input, Output, State
from datetime import datetime, date
import pandas as pd
import os
import dash_bootstrap_components as dbc
from data_loader import carica_df

dash.register_page(__name__, path='/inserimento', title='Seleziona dati')

# --- Sezione di caricamento iniziale dei dati ---
current_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))

# Nomi dei file CSV disponibili.
opzioni_file = [
    {'label': 'feeds.csv', 'value': 'feeds.csv'},
    {'label': 'm4w_Villaverla.csv', 'value': 'm4w_Villaverla.csv'}
]

minuti_options = [{'label': '00', 'value': 0}, {'label': '30', 'value': 30}]

# --- LAYOUT COMPLETO ---
layout = html.Div(style={'padding': '20px'}, children=[
    html.Div([
        html.H1("Select Data and Sensor", className="my-custom-h1"),
    ], style={'textAlign': 'center', 'marginTop': '20px'}),

    # Nuovo contenitore flessibile per i dropdown File e Sensore
    html.Div(className='dropdown-container-wrapper', children=[
        html.Div(className='file-dropdown-container', children=[
            html.Label("Select Data File:", className='dropdown-label'),
            dcc.Dropdown(
                id='file-dropdown',
                options=opzioni_file,
                value='m4w_Villaverla.csv',
                clearable=False,
                searchable=False,
                className='common-dropdown-style'
            )
        ]),

        # Questo contenitore viene popolato dalla callback con il dropdown del sensore
        html.Div(id='sensor-dropdown-wrapper', className='sensor-dropdown-container')
    ]),

    # Contenitore per gli elementi dinamici (selezioni data/ora e bottoni)
    html.Div(id='dynamic-content-container'),
    
    # Componente dcc.Store per memorizzare l'ultimo timestamp
    dcc.Store(id='latest-timestamp-store')
])

# --- Callback principale per aggiornare i dati e il layout in base al file selezionato ---
@dash.callback(
    Output('sensor-dropdown-wrapper', 'children'),
    Output('dynamic-content-container', 'children'),
    Output('latest-timestamp-store', 'data'),
    Input('file-dropdown', 'value')
)
def aggiorna_dati_e_layout(file_selezionato):
    csv_path = os.path.join(project_root, file_selezionato)
    
    # La nostra funzione ora restituisce una lista di dizionari
    dati_sensori = carica_df(csv_path)
    
    # Convertiamo subito la lista in un DataFrame
    df_new = pd.DataFrame(dati_sensori)
    
    if df_new.empty:
        df_min_date = date(2020, 1, 1)
        df_max_date = date.today()
        latest_timestamp_data = None
        
        return (
            html.Div(children=[
                html.Label("Select a sensor:", className='dropdown-label'),
                dcc.Dropdown(
                    id='sensore-dropdown',
                    options=[],
                    placeholder="No sensors available",
                    disabled=True,
                    className='common-dropdown-style'
                )
            ]),
            html.Div("Nessun dato valido trovato per il file selezionato.", style={'textAlign': 'center', 'color': 'red', 'marginTop': '20px'}),
            latest_timestamp_data
        )
    else:
        # Ora il resto del codice può usare il DataFrame come faceva prima
        df_min_date = df_new['created_at'].min().date()
        df_max_date = df_new['created_at'].max().date()
        sensori = [f'field{i}' for i in range(1, 8) if f'field{i}' in df_new.columns]
        latest_timestamp = df_new['created_at'].max()
        latest_timestamp_data = {'date': latest_timestamp.date().isoformat(), 'hour': latest_timestamp.hour, 'minute': latest_timestamp.minute}
        
        default_start_hour_value = None
        default_start_minute_value = None
        default_end_hour_value = None
        default_end_minute_value = None

        return (
            html.Div(children=[
                html.Label("Select a sensor:", className='dropdown-label'),
                dcc.Dropdown(
                    id='sensore-dropdown',
                    options=[{'label': f"Sensor {i+1}", 'value': s} for i, s in enumerate(sensori)],
                    placeholder="Select a sensor",
                    searchable=False,
                    clearable=False,
                    className='common-dropdown-style'
                )
            ]),
            html.Div(children=[
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
                                className='uniform-input common-dropdown-style',
                                searchable=False,
                                clearable=False,
                                value=default_start_hour_value
                            ),
                            dcc.Dropdown(
                                id='start-minute',
                                options=minuti_options,
                                placeholder="Min",
                                className='uniform-input common-dropdown-style',
                                searchable=False,
                                clearable=False,
                                value=default_start_minute_value
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
                                className='uniform-input common-dropdown-style',
                                searchable=False,
                                clearable=False,
                                value=default_end_hour_value
                            ),
                            dcc.Dropdown(
                                id='end-minute',
                                options=minuti_options,
                                placeholder="Min",
                                className='uniform-input common-dropdown-style',
                                searchable=False,
                                clearable=False,
                                value=default_end_minute_value
                            )
                        ])
                    ])
                ]),
                html.Div(id='selection-error-message', style={'color': 'red', 'textAlign': 'center', 'marginBottom': '20px'}),
                html.Div(id='link-container', className='d-flex justify-content-center mt-4')
            ]),
            latest_timestamp_data
        )

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
    State('file-dropdown', 'value'),
    State('latest-timestamp-store', 'data')
)
def genera_link(sensore, sd, sh, sm, ed, eh, em, file_selezionato, latest_timestamp_data):
    link_output = None
    error_message = ""

    if not sensore or not sd or not ed:
        error_message = "Please select a sensor and both start and end dates."
        return link_output, error_message
    
    start_date_obj = date.fromisoformat(sd)
    end_date_obj = date.fromisoformat(ed)
    
    sh = sh if sh is not None else 0
    sm = sm if sm is not None else 0

    if start_date_obj == end_date_obj and eh is None and em is None:
        if latest_timestamp_data and date.fromisoformat(latest_timestamp_data['date']) == end_date_obj:
            eh = latest_timestamp_data['hour']
            em = latest_timestamp_data['minute']
        else:
            eh = 23
            em = 59
    else:
        eh = eh if eh is not None else 23
        em = em if em is not None else 59

    try:
        start_dt = datetime.strptime(sd, '%Y-%m-%d').replace(hour=sh, minute=sm)
        end_dt = datetime.strptime(ed, '%Y-%m-%d').replace(hour=eh, minute=em)
    except Exception:
        error_message = "Invalid date or time format. Please check your selections."
        return link_output, error_message

    if start_dt > end_dt:
        error_message = "Error: start date/time must be before or equal to end date/time."
        return link_output, error_message
    
    query = f"?file={file_selezionato}&sensore={sensore}&sd={sd}&sh={sh}&sm={sm}&ed={ed}&eh={eh}&em={em}"
    link_output = dcc.Link(
        dbc.Button("Generate Graph", color="success", className="me-1"),
        href=f"/grafici{query}",
        style={'display': 'block', 'margin': '0 auto', 'width': 'fit-content'}
    )

    return link_output, error_message