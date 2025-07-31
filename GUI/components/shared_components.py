# components/shared_components.py
import dash_bootstrap_components as dbc
from dash import html

# Percorso del logo (assicurati che il tuo logo.png sia nella cartella 'assets' del tuo progetto)
LOGO_PATH = '/assets/logo.png'

# Navbar SENZA logo (per la home) - Non cambia, perché il logo non c'è
navbar_no_logo = dbc.Navbar(
    dbc.Container([
        dbc.NavbarBrand(
            "More4Water",
            href="/",
            style={"fontWeight": "bold", "fontSize": "2rem"}
        ),
    ]),
    color="primary",
    dark=True,
    sticky="top",
    className="mb-4 shadow",
)

# Navbar CON logo (per le altre pagine)
navbar_with_logo = dbc.Navbar(
    dbc.Container([
        dbc.NavbarBrand(
            "More4Water", # Il brand rimane solo testo e sta a sinistra
            href="/",
            style={"fontWeight": "bold", "fontSize": "2rem"}
        ),
        # Questo elemento spingerà tutto ciò che viene dopo di esso all'estrema destra
        dbc.Nav(
            dbc.NavItem(
                html.A(
                    html.Img(src=LOGO_PATH, height="35px"),
                    href="/", # Puoi rendere il logo cliccabile per tornare alla home
                    style={"marginLeft": "10px"} # Piccolo margine se necessario, ma con ms-auto si adatta
                )
            ),
            className="ms-auto", # Questa classe Bootstrap spinge l'elemento a destra
            navbar=True
        ),
    ]),
    color="primary",
    dark=True,
    sticky="top",
    className="mb-4 shadow",
)
