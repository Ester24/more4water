import dash
import dash_bootstrap_components as dbc
from dash import dcc, html

# importa la navbar dal modulo components.shared_components
from components.shared_components import navbar

app = dash.Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[dbc.themes.CYBORG],
    suppress_callback_exceptions=True,
)

server = app.server

app.layout = html.Div(
    [
        dcc.Location(id="url", refresh=False),
        navbar,  # navbar sempre visibile
        dash.page_container,
    ],
    style={"backgroundColor": "#001133", "minHeight": "100vh"}
)

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=8090)

