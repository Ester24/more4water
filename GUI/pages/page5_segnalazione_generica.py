import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, State
import os
from db_utils import insert_general_report # Dovrai implementare questa funzione

dash.register_page(__name__, path='/segnalazione_generica', title='MORE4WATER - General Report')

layout = dbc.Container([
    # Opzionale: puoi includere il logo o una versione più piccola anche qui
    # html.Div(
    #     html.Img(src="/assets/logo.png", style={"height": "150px"}),
    #     className="text-center my-4"
    # ),

    # RIMOSSO: html.Hr(), # Questa riga è stata rimossa per eliminare lo spazio extra

    html.H2("Submit a General User Report", className="text-center mb-4 mt-0"), # Aggiunto mt-0 per rimuovere il margine superiore

    dbc.Form([
        dbc.Row([
            dbc.Col(
                html.Div([
                    dbc.Label("First Name", html_for="first_name", className="mt-3"),
                    dbc.Input(id="first_name", type="text", placeholder="Enter your first name"),
                ]),
                md=6
            ),
            dbc.Col(
                html.Div([
                    dbc.Label("Last Name", html_for="last_name", className="mt-3"),
                    dbc.Input(id="last_name", type="text", placeholder="Enter your last name"),
                ]),
                md=6
            ),
        ], className="mb-3"), # Margine inferiore per la riga nome/cognome

        dbc.Label("Region", html_for="region", className="mt-3"),
        dbc.Input(id="region", type="text", placeholder="Umbria"),

        dbc.Label("Province", html_for="province", className="mt-3"),
        dbc.Input(id="province", type="text", placeholder="Perugia"),

        dbc.Label("City", html_for="city", className="mt-3"),
        dbc.Input(id="city", type="text", placeholder="Assisi"),

        dbc.Label("Address", html_for="address", className="mt-3"),
        dbc.Input(id="address", type="text", placeholder="Via Roma, 10"),

        dbc.Label("Problem Description", html_for="problem_description", className="mt-3"),
        dbc.Textarea(id="problem_description", placeholder="Describe the problem here...", rows=5),

        dbc.Button("Submit Report", id="submit_general_report_btn", color="primary", className="mt-4"),

        html.Div(id='general_report_output_msg', className='mt-3')
    ])
], fluid=True, className="py-0") # Modificato da "py-5" a "py-0" per rimuovere il padding verticale dal container principale


@dash.callback(
    Output('general_report_output_msg', 'children'),
    Input('submit_general_report_btn', 'n_clicks'),
    State('first_name', 'value'),
    State('last_name', 'value'),
    State('region', 'value'),
    State('province', 'value'),
    State('city', 'value'),
    State('address', 'value'),
    State('problem_description', 'value'),
)
def submit_general_report_callback(n_clicks, first_name, last_name, region, province, city, address, problem_description):
    if not n_clicks:
        return ''

    # Validazione minima: almeno nome, cognome e descrizione del problema
    if not all([first_name, last_name, problem_description]):
        return dbc.Alert("First Name, Last Name, and Problem Description are mandatory.", color="danger")

    try:
        insert_general_report(
            first_name,
            last_name,
            region or '',
            province or '',
            city or '',
            address or '',
            problem_description
        )
        return dbc.Alert("General report submitted successfully!", color="success")
    except Exception as e:
        return dbc.Alert(f"Error submitting report: {str(e)}", color="danger")