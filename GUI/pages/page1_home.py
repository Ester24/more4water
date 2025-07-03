import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, callback, dcc, html

dash.register_page(__name__, path="/", title="EMERLAB-POTGALV")

layout = dbc.Container(
    [
        html.H1("EMERLAB-POTGALV", className="text-center "),
        html.Hr(),
        html.Div(
            "Available", 
            id="state-display", 
            className="text-center bg-success text-white p-2 rounded"
        ),  # Stato visualizzato come testo
        html.Hr(),
        dbc.Button(
            "EIS",
            id="btn-eis",
            href="/eis",  # Aggiunto href per renderlo un link
            className='me-3',
        ),
        dbc.Button(
            "CYCLER",
            id="btn-ciycler",
            href="/cycler",  # Aggiunto href per renderlo un link
            className='me-3',          
        ),
        dbc.Button(
            "RUNNING MEASURE",
            id="btn-running-measure",
            href="/running",  # Aggiunto href per renderlo un link
            className='le',
        ),
        dcc.Location(id="url", refresh=True),
        dcc.Store(id="board-state"),
    ]
)


# Callback associato ai pulsanti su questa pagina
@callback(
    Output("btn-eis", "disabled"),
    Output("btn-ciycler", "disabled"),
    Output("btn-running-measure", "disabled"),
    Input("state-display", "children"),  # Cambiato da "state-input" a "state-display"
)
def update_buttons_state(state):
    print(f"State: {state}")
    if state == "Occupied":
        return True, True, False
    else:
        return False, False, True


# Se preferisci la navigazione in questa pagina, puoi farlo:
@callback(
    Input("btn-eis", "n_clicks"),
    Input("btn-ciycler", "n_clicks"),
    Input("btn-running-measure", "n_clicks"),
    prevent_initial_call=True,
)
def go_to_pages(n_eis, n_ciycler, n_run):
    triggered = dash.ctx.triggered_id
    if triggered == "btn-eis":
        print("EIS button clicked")
        print("ESEGUO EIS")

    elif triggered == "btn-ciycler":
        print("Ciycler button clicked")

    elif triggered == "btn-running-measure":
        print("Running measure button clicked")
