import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output, State

# import callbacks from callback

app = dash.Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[dbc.themes.CYBORG],
    suppress_callback_exceptions=True,
)
server = app.server

app.layout = html.Div(
    [dcc.Location(id="url", refresh=False), dash.page_container],
    style={"backgroundColor": "#001133", "minHeight": "100vh"}
)


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=8090)
    print(dash.page_registry)
    # app.validation_layout = html.Div(
    #     layout_page_1, layout__page_2, layout__page_3, layout_page_4
    # )
