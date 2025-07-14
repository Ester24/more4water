import dash_bootstrap_components as dbc

navbar = dbc.Navbar(
    dbc.Container([
        dbc.NavbarBrand("More4Water", href="/", style={"fontWeight": "bold", "fontSize": "2rem"}),

    ]),
    color="primary",
    dark=True,
    sticky="top",
    className="mb-4 shadow",
)
