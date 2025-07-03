import dash_bootstrap_components as dbc
from dash import html

navbar = dbc.Navbar(
    dbc.Container([
        dbc.NavbarBrand("EMERLAB-POTGALV GUI", href="/", style={"fontWeight": "bold", "fontSize": "2rem"}),
        dbc.Nav([
            dbc.NavLink("Home", href="/", active="exact", className="mx-2"),
            dbc.NavLink("EIS", href="/eis", active="exact", className="mx-2"),
            dbc.NavLink("Running", href="/running", active="exact", className="mx-2"),
            dbc.NavLink("Results", href="/results", active="exact", className="mx-2"),
        ], navbar=True),
    ]),
    color="primary",
    dark=True,
    sticky="top",
    className="mb-4 shadow",
)
