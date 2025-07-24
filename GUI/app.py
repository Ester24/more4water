import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from components.shared_components import navbar

app = dash.Dash(
    __name__,
    use_pages=True,
    # QUESTO È IL MODO CORRETTO PER CARICARE IL TUO CSS DA ASSETS
    external_stylesheets=[dbc.themes.FLATLY, '/assets/style.css'],
    suppress_callback_exceptions=True,
)

server = app.server

app.layout = html.Div(
    [
        dcc.Location(id="url", refresh=False),
        navbar,
        dash.page_container,
    ],
    style={"minHeight": "100vh"}  # niente backgroundColor qui, gestisci tutto da CSS
)

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=8090)
    #app.run(debug=True, host='0.0.0.0', port=8090)

