import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, State
import os
import base64
import uuid
from db_utils import insert_general_report
from export_file import esporta_database_in_csv, save_image

dash.register_page(__name__, path='/segnalazione_generica', title='MORE4WATER - General Report')

layout = dbc.Container([
    html.H2("Submit a General User Report", className="text-center mb-4 mt-0"),

    dbc.Form([
        dbc.Row([
            dbc.Col(html.Div([dbc.Label("First Name", html_for="first_name", className="mt-3"),
                             dbc.Input(id="first_name", type="text", placeholder="Enter your first name")]), md=6),
            dbc.Col(html.Div([dbc.Label("Last Name", html_for="last_name", className="mt-3"),
                             dbc.Input(id="last_name", type="text", placeholder="Enter your last name")]), md=6),
        ], className="mb-3"),

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

        # Componente per il caricamento file
        dbc.Label("Attach a photo (optional)", className="mt-3"),
        dcc.Upload(
            id='upload-image',
            children=html.Div([
                'Drag and Drop or ',
                html.A('Select Files')
            ]),
            style={
                'width': '100%', 'height': '60px', 'lineHeight': '60px',
                'borderWidth': '1px', 'borderStyle': 'dashed',
                'borderRadius': '5px', 'textAlign': 'center', 'margin': '10px 0'
            },
            multiple=False
        ),
        html.Div(id='upload-status'),

        dbc.Button("Submit Report", id="submit_general_report_btn", color="primary", className="mt-4"),
        html.Div(id='general_report_output_msg', className='mt-3')
    ])
], fluid=True, className="py-0")

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
    State('upload-image', 'contents'),
    State('upload-image', 'filename')
)
def submit_general_report_callback(n_clicks, first_name, last_name, region, province, city, address, problem_description, image_contents, image_filename):
    if not n_clicks:
        return ''

    # Validazione minima
    if not all([first_name, last_name, problem_description]):
        return dbc.Alert("First Name, Last Name, and Problem Description are mandatory.", color="danger")
    
    # Salva la foto se presente
    image_path = None
    if image_contents:
        try:
            image_path = save_image(image_contents, image_filename)
        except Exception as e:
            return dbc.Alert(f"Errore durante il caricamento della foto: {str(e)}", color="danger")

    try:
        # Assicurati che la tua funzione insert_general_report possa accettare il nome del file immagine
        insert_general_report(
            first_name,
            last_name,
            region or '',
            province or '',
            city or '',
            address or '',
            problem_description,
            image_path # Passa il nome del file immagine alla funzione di inserimento
        )
        
        # Esportazione in CSV
        esporta_database_in_csv()

        return dbc.Alert("General report submitted", color="success")
    except Exception as e:
        return dbc.Alert(f"Error submitting report or exporting data: {str(e)}", color="danger")