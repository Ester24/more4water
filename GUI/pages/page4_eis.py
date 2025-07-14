import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, callback, ctx, dcc, html
import subprocess
import json

dash.register_page(__name__, path="/eis", title="EIS")

layout = dbc.Container(
    [
        html.H2("EIS", className="text-center", style={"margin-top": "20px"}),
        dcc.Store(id="eis-paramters"),
        html.Hr(),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Select(
                        id="board-mode",
                        options=[
                            {"label": "Potentiostat", "value": "Potentiostat"},
                            {"label": "Galvanostat", "value": "Galvanostat"},
                        ],
                        placeholder="Board Mode (required)",
                        className='mb-3',
                    ),
                    width="6"
                ),
                dbc.Col(
                    dbc.Select(
                        id="signal-type",
                        options=[
                            {"label": "Maximum Length Sequency", "value": "MLS"},
                            {"label": "Multisine", "value": "MS"},
                            {"label": "Sine", "value": "S"},
                        ],
                        placeholder="Signal Type (required)",
                        className='mb-3',
                    ),
                    width="6"
                ),
            ],
            className="g-2 mb-3"
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Label('Gain I', html_for="gain-i"),
                        dbc.Input(
                            type="number",
                            id="gain-i",
                            placeholder="Gain I (3-130)",
                            min=3,
                            max=130,
                            step=1,
                            value=3,
                            className='mb-3',
                        ),
                    ],
                    className='text-center',
                    style = {'color' : 'white', 'font-size' : '20px'},
                    width="4"
                ),
                dbc.Col(
                    [
                        dbc.Label('Gain V', html_for="gain-v"),
                        dbc.Input(
                            type="number",
                            id="gain-v",
                            placeholder="Gain V (0-10)",
                            min=0,
                            max=10,
                            step=1,
                            value=5,
                            className='mb-3',
                        ),
                    ],
                    className='text-center',
                    style = {'color' : 'white', 'font-size' : '20px'},
                    width="4"
                ),
                dbc.Col(
                    [
                        dbc.Label('Number of measurements', html_for="repeated-measurements"),
                        dbc.Input(
                            type="number",
                            id="repeated-measurements",
                            placeholder="Repeated Measurements (1-100)",
                            min=1,
                            max=100,
                            value=1,
                            className='mb-3',
                        ),
                    ],
                    className='text-center',
                    style = {'color' : 'white', 'font-size' : '20px'},
                    width="4"
                ),
                dbc.Col(
                    [
                        dbc.Label('Voltage range', html_for="a-daq1"),
                        dbc.Input(
                            type="number",
                            id="a-daq1",
                            placeholder="A_DAQ1 (0-10)",
                            min=0,
                            max=10,
                            value=10,
                            className='mb-3',
                        ),
                    ],
                    className='text-center',
                    style = {'color' : 'white', 'font-size' : '20px'},
                    width="4"
                ),
                dbc.Col(
                    [
                        dbc.Label('Current range', html_for="a-daq2"),
                        dbc.Input(
                            type="number",
                            id="a-daq2",
                            placeholder="A_DAQ2 (0-10)",
                            min=0,
                            max=10,
                            value=10,
                            className='mb-3',
                        ),
                    ],
                    className='text-center',
                    style = {'color' : 'white', 'font-size' : '20px'},
                    width="4"
                ),
                dbc.Col(
                    [
                        dbc.Label('Dynamic EIS Offset', html_for="DEIS-offset"),
                        dbc.Input(
                            type="number",
                            id="DEIS-offset",
                            placeholder="Dynamic EIS Offset (-1;1)",
                            min=-1,
                            max=1,
                            value=0.000,
                            step=0.001,
                            className='mb-3',
                        ),
                    ],
                    className='text-center',
                    style = {'color' : 'white', 'font-size' : '20px'},
                    width="4"
                )
            ]
        ),
        html.Hr(),
        dbc.Button(
            "START MEASURE",
            id="btn-start-measure",
            disabled=True,
            href="/running",  # Aggiunto href per renderlo un link
            className="me-3",
        ),
        dbc.Button(
            "HOME",
            id="btn-home-from-eis",
            href="/",  # Aggiunto href per renderlo un link
        ),
    ]
)


# Callback legato ai componenti su questa pagina
@callback(
    Output("btn-start-measure", "disabled"),
    Input("board-mode", "value"),
    Input("signal-type", "value"),
)
def enable_start_measure(board_mode, signal_type):
    return not (board_mode and signal_type)


@callback(
    Output("eis-paramters", "data"),
    Input("btn-start-measure", "n_clicks"),
    State("board-mode", "value"),
    State("signal-type", "value"),
    State("gain-i", "value"),
    State("gain-v", "value"),
    State("repeated-measurements", "value"),
    State("a-daq1", "value"),
    State("a-daq2", "value"),
    State("DEIS-offset", "value"),
    prevent_initial_call=True,
)
def start_measure(n_clicks, board_mode, signal_type, gain_i, gain_v, repeated_measurements, a_daq1, a_daq2, DEIS_offset):
    """
    Avvia la misura e passa i parametri al codice esterno.
    """
    if n_clicks:
        # Parametri da passare al codice
        parameters = {
            "board_mode": board_mode,
            "signal_type": signal_type,
            "gain_i": gain_i,
            "gain_v": gain_v,
            "repeated_measurements": repeated_measurements,
            "a_daq1": a_daq1,
            "a_daq2": a_daq2,
            "DEIS_offset": DEIS_offset,
        }

        # Salva i parametri in formato JSON
        with open("eis_parameters.json", "w") as f:
            json.dump(parameters, f)

        # Esegui il codice esterno
        subprocess.Popen(["python", "EIS.py"])

        return parameters
