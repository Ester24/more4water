import os
import zipfile
from io import BytesIO
from pathlib import Path

import dash
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objs as go
import numpy as np
from dash import Input, Output, callback, dcc, html

dash.register_page(__name__, path="/results", title="Results")

layout = dbc.Container(
    [
        dcc.Location(id="url", refresh=False),
        dcc.Interval(id="refresh-results", interval=500, n_intervals=0, max_intervals=1),  # <--- aggiungi questo
        html.H2("Results", className="text-center", style={"margin-top": "20px"}),
        html.Hr(),
        dbc.Button(
            "HOME",
            id="btn-home-from-results",
            href="/",  # Aggiunto href per tornare alla home
            className='me-3',
        ),
        dbc.Button(
            "Download Data Results",
            id="btn-download-results",
            className='me-3',
        ),
        html.Hr(),
        html.Div(id="parameters-summary"),  # Per i parametri della misurazione
        html.Hr(),
        html.Div(id="plots-section"),  # Per i grafici
        html.Hr(),
        dcc.Download(id="download-results-data"),
    ]
)


@callback(
    Output("parameters-summary", "children"),
    Output("plots-section", "children"),
    Input("url", "pathname"),
    Input("refresh-results", "n_intervals"),  # <--- aggiungi questo input
)
def display_results(_, __):
    """
    Legge i dati dai file CSV dell'ultima misurazione e genera i grafici con Plotly.
    """
    # Percorso della directory dei risultati
    results_dir = Path("output_csv")

    # Trova i file CSV dell'ultima misurazione
    sig_v_i_files = list(results_dir.glob("sig_V_I_*_*.csv"))
    z_vector_files = list(results_dir.glob("z_vector_*_*.csv"))

    if not sig_v_i_files or not z_vector_files:
        return "Nessun risultato trovato.", "Nessun grafico disponibile."

    # Ordina i file per indice e seleziona l'ultimo
    sig_v_i_file = max(sig_v_i_files, key=lambda f: int(f.stem.split("_")[-1]))
    z_vector_file = max(z_vector_files, key=lambda f: int(f.stem.split("_")[-1]))

    # Leggi i dati di tensione e corrente
    df_sig_v_i = pd.read_csv(sig_v_i_file)
    t_base = df_sig_v_i["Time [s]"]
    sig_v = df_sig_v_i["Voltage [V]"]
    sig_i = df_sig_v_i["Current [I]"]

    # Leggi i dati di impedenza
    df_z_vector = pd.read_csv(z_vector_file)
    f_base = df_z_vector["Frequency [Hz]"]
    Z_real = df_z_vector["Re(Z)"]
    Z_imag = df_z_vector["Im(Z)"]

    # Calcola modulo e fase dell'impedenza
    Z_vector = Z_real + 1j * Z_imag
    Z_magnitude = abs(Z_vector)
    Z_phase = np.angle(Z_vector)

    # Parametri della misurazione
    parameters_html = html.Div(
        [
            html.H4("Parametri della Misurazione"),
            html.P(f"Durata: {t_base.iloc[-1]:.2f} s"),
            html.P(f"Campioni: {len(t_base)}"),
            html.P(f"Frequenza di campionamento: {1 / (t_base.iloc[1] - t_base.iloc[0]):.2f} Hz"),
            html.P(f"Ultima misurazione: {sig_v_i_file.name}"),
        ]
    )

    # Determina se il file è MLS
    is_mls = "mls" in z_vector_file.name.lower()

    # Grafico del segnale acquisito
    # Se il file contiene dati di più frequenze (es. seno singolo), spezza i dati con None
    if "Frequency [Hz]" in df_sig_v_i.columns:
        time_all = []
        voltage_all = []
        current_all = []
        for _, group in df_sig_v_i.groupby("Frequency [Hz]"):
            time_all.extend(group["Time [s]"].values)
            voltage_all.extend(group["Voltage [V]"].values)
            current_all.extend(group["Current [I]"].values)
            # Aggiungi None per spezzare le linee
            time_all.append(None)
            voltage_all.append(None)
            current_all.append(None)
        traces = [
            go.Scatter(
                x=time_all, 
                y=voltage_all, 
                mode="lines", 
                name="Tensione [V]",
                line=dict(width=2)  # Linea sottile
            ),
            go.Scatter(
                x=time_all, 
                y=current_all, 
                mode="lines", 
                name="Corrente [I]",
                line=dict(width=2)  # Linea sottile
            ),
        ]
    else:
        traces = [
            go.Scatter(
                x=t_base, 
                y=sig_v, 
                mode="lines", 
                name="Tensione [V]",
                line=dict(width=1)  # Linea sottile
            ),
            go.Scatter(
                x=t_base, 
                y=sig_i, 
                mode="lines", 
                name="Corrente [I]",
                line=dict(width=1)  # Linea sottile
            ),
        ]

    time_plot = dcc.Graph(
        id="time-domain-plot",
        figure={
            "data": traces,
            "layout": go.Layout(
                title="Segnale Acquisito nel Dominio del Tempo",
                xaxis={"title": "Tempo [s]"},
                yaxis={"title": "Ampiezza"},
                legend={"x": 0, "y": 1},
            ),
        },
        style={"margin-bottom": "40px"},
    )

    # Grafico di modulo e fase dell'impedenza
    if is_mls:
        impedance_plot = dcc.Graph(
            id="impedance-plot",
            figure={
                "data": [
                    go.Scatter(x=f_base[0:int(len(f_base)/4)], y=20 * np.log10(Z_magnitude[0:int(len(f_base)/4)]), mode="lines+markers", name="Modulo [dB]"),
                    go.Scatter(x=f_base[0:int(len(f_base)/4)], y=np.degrees(Z_phase[0:int(len(f_base)/4)]), mode="lines+markers", name="Fase [°]"),
                ],
                "layout": go.Layout(
                    title="Modulo e Fase dell'Impedenza",
                    xaxis={"title": "Frequenza [Hz]", "type": "log"},
                    yaxis={"title": "Modulo [dB] / Fase [°]"},
                    legend={"x": 0, "y": 1},
                ),
            },
            style={"margin-bottom": "40px"},
        )
        nyquist_plot = dcc.Graph(
            id="nyquist-plot",
            figure={
                "data": [
                    go.Scatter(x=Z_real[0:int(len(Z_real)/4)], y=-Z_imag[0:int(len(Z_imag)/4)], mode="lines+markers", name="Nyquist"),
                ],
                "layout": go.Layout(
                    title="Diagramma di Nyquist",
                    xaxis={"title": "Re(Z) [Ω]"},
                    yaxis={"title": "-Im(Z) [Ω]"},
                    legend={"x": 0, "y": 1},
                    xaxis_scaleanchor="y",
                ),
            },
            style={"margin-bottom": "40px"},
        )
    else:
        impedance_plot = dcc.Graph(
            id="impedance-plot",
            figure={
                "data": [
                    go.Scatter(x=f_base, y=20 * np.log10(Z_magnitude), mode="lines+markers", name="Modulo [dB]"),
                    go.Scatter(x=f_base, y=np.degrees(Z_phase), mode="lines+markers", name="Fase [°]"),
                ],
                "layout": go.Layout(
                    title="Modulo e Fase dell'Impedenza",
                    xaxis={"title": "Frequenza [Hz]", "type": "log"},
                    yaxis={"title": "Modulo [dB] / Fase [°]"},
                    legend={"x": 0, "y": 1},
                ),
            },
            style={"margin-bottom": "40px"},
        )
        nyquist_plot = dcc.Graph(
            id="nyquist-plot",
            figure={
                "data": [
                    go.Scatter(x=Z_real, y=-Z_imag, mode="lines+markers", name="Nyquist"),
                ],
                "layout": go.Layout(
                    title="Diagramma di Nyquist",
                    xaxis={"title": "Re(Z) [Ω]"},
                    yaxis={"title": "-Im(Z) [Ω]"},
                    legend={"x": 0, "y": 1},
                    xaxis_scaleanchor="y",
                ),
            },
            style={"margin-bottom": "40px"},
        )

    # Sezione dei grafici
    plots_html = html.Div([time_plot, impedance_plot, nyquist_plot])

    return parameters_html, plots_html


@callback(
    Output("download-results-data", "data"),
    Input("btn-download-results", "n_clicks"),
    prevent_initial_call=True,
)
def download_results(n_clicks):
    """
    Crea un file ZIP con i risultati e lo invia al browser per il download.
    """
    from datetime import datetime

    # Percorso della directory dei risultati
    results_dir = Path("output_csv")

    # Verifica se la directory esiste e contiene file
    if not results_dir.exists() or not any(results_dir.iterdir()):
        return dcc.send_file("Nessun risultato disponibile.")

    # Ottieni la data corrente
    current_date = datetime.now().strftime("%Y/%m/%d-%H:%M:%S")

    # Trova l'indice dell'ultima misurazione
    sig_v_i_files = list(results_dir.glob("sig_V_I_*_*.csv"))
    if not sig_v_i_files:
        return dcc.send_file("Nessun risultato disponibile.")
    last_measurement_index = max(int(f.stem.split("_")[-1]) for f in sig_v_i_files)

    # Nome del file ZIP
    zip_filename = f"{current_date}.zip"

    # Crea un file ZIP in memoria
    memory_file = BytesIO()
    with zipfile.ZipFile(memory_file, "w") as zf:
        for file in results_dir.glob("*.csv"):
            zf.write(file, arcname=file.name)  # Aggiungi i file CSV al file ZIP

    memory_file.seek(0)  # Torna all'inizio del buffer

    # Invia il file ZIP al browser per il download
    return dcc.send_bytes(memory_file.read(), filename=zip_filename)
