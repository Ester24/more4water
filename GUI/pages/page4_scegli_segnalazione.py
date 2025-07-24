import dash
import dash_bootstrap_components as dbc
from dash import dcc, html

dash.register_page(__name__, path="/scegli_segnalazione", title="MORE4WATER - Choose Report Type") # Modificato il titolo della pagina

layout = dbc.Container([
    # Inizio del blocco commentato per l'inserimento del logo
    # html.Div(
    #     html.Img(src="/assets/logo.png", style={"height": "250px"}),
    #     className="text-center my-3"
    # ),
    # Fine del blocco commentato per l'inserimento del logo

    html.Hr(),

    html.Div("Select Report Type:", className="text-center fs-3 mb-5"), 

    dbc.Row([
        dbc.Col(
            # Bottone per segnalazione Utente Qualsiasi
            dbc.Button(
                "General User Report", 
                href="/segnalazione_generica",
                color="info",
                className="w-100 py-3"
            ),
            xs=12, sm=8, md=6, lg=4, className="mb-3"
        ),
        dbc.Col(
            # Bottone per segnalazione Specializzato
            dbc.Button(
                "Specialized Report", 
                href="/segnalazione_specializzata",
                color="primary",
                className="w-100 py-3"
            ),
            xs=12, sm=8, md=6, lg=4, className="mb-3"
        ),
    ], justify="center", className="g-3"),

    # Bottone "Back to Home"
    html.Div(
        html.A("Back to Home", href="/", id="back-to-home-from-choice", className="btn btn-secondary mt-4"), # Tradotto "Torna alla Home"
        className="text-center"
    ),

    dcc.Location(id="url", refresh=True)
], fluid=True, className="py-5")