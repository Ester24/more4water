import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output
# Importa entrambe le navbar dal tuo modulo
from components.shared_components import navbar_no_logo, navbar_with_logo

app = dash.Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[dbc.themes.FLATLY, '/assets/style.css'],
    suppress_callback_exceptions=True,
)

server = app.server

app.layout = html.Div(
    [
        dcc.Location(id="url", refresh=False),
        html.Div(id='navbar-container'), # Un div contenitore per la navbar che verrà aggiornata
        dash.page_container,
    ],
    style={"minHeight": "100vh"}
)

# Callback per scegliere quale navbar visualizzare
@app.callback(
    Output('navbar-container', 'children'),
    Input('url', 'pathname')
)
def display_navbar(pathname):
    if pathname == '/': # Se l'URL è la home page
        return navbar_no_logo
    else: # Per tutte le altre pagine
        return navbar_with_logo

if __name__ == "__main__":
    #app.run(debug=True, host="127.0.0.1", port=8090)
    app.run(debug=True, host='0.0.0.0', port=8090)

