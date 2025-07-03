import json
from datetime import datetime
import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, callback, ctx, dcc, html

dash.register_page(__name__, path="/running", title="Running Measure")

measurement_state = {
    "status": "running",
    "completed": 0,
    "start_time": datetime.now(),
}

# Variabile globale per memorizzare il tempo finale
final_elapsed_time = None

layout = dbc.Container(
    [
        html.H2(id="measure-state-title", className="text-center", style={"margin-top": "20px"}),
        html.Hr(),
        html.Div(
            [
                dbc.Button(
                    "Stop",
                    id="btn-stop",
                    href="/eis",  # Aggiunto href per renderlo un link
                    className='me-3',
                    
                ),
                dbc.Button(
                    "Show Results",
                    id="btn-show-results",
                    href="/results",  # Aggiunto href per renderlo un link
                    disabled=True,  # Disabilitato inizialmente
                    className='me-3',
                    
                ),
                dbc.Button(
                    "Repeat Measure",
                    id="btn-repeat-measure",
                    disabled=True,  # Disabilitato inizialmente
                    className='me-3',
                    
                ),
            ]
        ),
        html.Hr(),
        dbc.Input(id="num-measurements-completed", readonly=True, className='mb-3'),
        dbc.Input(id="running-time", readonly=True),
        html.Hr(),
        dcc.Interval(id="status-check-interval", interval=2000),  # Controlla ogni 2 secondi
    ]
)


@callback(
    Output("measure-state-title", "children"),
    Output("num-measurements-completed", "value"),
    Output("running-time", "value"),
    Input("status-check-interval", "n_intervals"),
    prevent_initial_call=True,
)
def update_measurement_state(n_intervals):
    """
    Controlla lo stato della misurazione leggendo il file JSON.
    """
    global final_elapsed_time
    try:
        # Leggi lo stato dal file JSON
        with open("measurement_status.json", "r") as f:
            measurement_state = json.load(f)

        start_time = datetime.fromisoformat(measurement_state["start_time"])

        if measurement_state["status"] == "running":
            elapsed_time = datetime.now() - start_time
            final_elapsed_time = elapsed_time  # aggiorna sempre durante la misura
        else:
            # Se completed, mostra sempre il tempo finale della misura
            if final_elapsed_time is None:
                final_elapsed_time = datetime.now() - start_time
            elapsed_time = final_elapsed_time

        # Restituisci lo stato aggiornato
        return (
            "Measurement Running" if measurement_state["status"] == "running" else "Measurement Completed",
            measurement_state["completed"],
            str(elapsed_time),
        )
    except (FileNotFoundError, KeyError, ValueError):
        # Se il file non esiste o è corrotto, restituisci uno stato predefinito
        return "Measurement Status Unknown", 0, "00:00:00"


@callback(
    Output("btn-show-results", "disabled"),
    Output("btn-repeat-measure", "disabled"),
    Input("status-check-interval", "n_intervals"),
)
def update_button_states(n_intervals):
    try:
        with open("measurement_status.json", "r") as f:
            status = json.load(f)["status"]
        if status == "running":
            return True, True  # Disabilita i pulsanti
        elif status == "completed":
            return False, False  # Abilita i pulsanti
    except (FileNotFoundError, KeyError):
        # Se il file non esiste o è corrotto, disabilita i pulsanti
        return True, True
