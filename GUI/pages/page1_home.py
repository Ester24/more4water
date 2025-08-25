import dash
import dash_bootstrap_components as dbc
from dash import dcc, html

dash.register_page(__name__, path="/", title="MORE4WATER")

layout = dbc.Container([
    # LOGO centrato sopra il titolo
    html.Div(
        html.Img(src="/assets/logo.png", style={"height": "300px"}),
        className="text-center my-4"
    ),

    html.Hr(),

    html.Div("Select an option:", className="text-center fs-4 mb-4"),

    dbc.Row([
        dbc.Col(
            dbc.Button("View Charts", href="/scelta", color="primary", className="w-100"),
            xs=12, sm=6, md=4, lg=3
        ),
        dbc.Col(
            dbc.Button("Insert Report", href="/scegli_segnalazione", color="warning", className="w-100"),
            xs=12, sm=6, md=4, lg=3
        ),
    ], justify="center", className="g-3"),

    dcc.Location(id="url", refresh=True)
], fluid=True)





