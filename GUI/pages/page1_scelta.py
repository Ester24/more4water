import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

# Register the page with the Dash router
dash.register_page(__name__, path='/scelta', title='Choose Data Source')

# --- LAYOUT OF THE SELECTION PAGE ---
layout = html.Div(
    className="container",
    style={'padding': '50px', 'textAlign': 'center'},
    children=[
        html.H1("Choose a Data Source", className="my-custom-h1"),
        
        html.Div(
            className="d-flex justify-content-center mt-5",
            children=[
                # Button for real-time data (ThingSpeak)
                dcc.Link(
                    dbc.Button(
                        "Real-Time Data (ThingSpeak)",
                        color="info",
                        size="lg",
                        className="me-3"
                    ),
                    href="/thingspeak",  # Redirect to the ThingSpeak page
                    style={'textDecoration': 'none'}
                ),
                
                # Button for historical data (CSV files)
                dcc.Link(
                    dbc.Button(
                        "File Data (Historical)",
                        color="primary", # Modificato in "primary" per il colore blu
                        size="lg",
                        className="ms-3"
                    ),
                    href="/inserimento",  # Redirect to the CSV file input page
                    style={'textDecoration': 'none'}
                )
            ]
        ),
        
        # Bottone "Back to Home"
        html.Div(
            html.A(
                "Back to Home", 
                href="/", 
                id="back-to-home-from-choice", 
                className="btn btn-secondary mt-4"
            ),
            className="text-center"
        ),
    ]
)