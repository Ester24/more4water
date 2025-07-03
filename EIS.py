import matplotlib.pyplot as plt
import numpy as np
import Agilent_U2351A
import time
import Signal_Generation as sg
import json  # Per leggere i parametri
import glob  # Per trovare i file da eliminare
from pathlib import Path  # Per gestire i file e le directory
from datetime import datetime  # Per gestire le date e gli orari

np.random.seed(1)

# Cancella tutti i file nella cartella output_csv
output_csv_dir = "output_csv"
for file_path in glob.glob(f"{output_csv_dir}/*"):
    try:
        Path(file_path).unlink()
    except Exception as e:
        print(f"Errore durante l'eliminazione di {file_path}: {e}")

# File temporaneo per indicare lo stato della misurazione
status_file = "measurement_status.json"

# Scrivi lo stato "in corso" all'inizio della misurazione, includendo tutti i campi necessari
with open(status_file, "w") as f:
    json.dump({
        "status": "running",
        "completed": 0,
        "start_time": datetime.now().isoformat()
    }, f)

try:
    # Leggi i parametri dal file JSON
    with open("eis_parameters.json", "r") as f:
        parameters = json.load(f)

    # Parametri acquisiti dalla GUI
    board_mode = parameters["board_mode"]
    signal_type = parameters["signal_type"]
    gain_i = parameters["gain_i"]
    gain_v = parameters["gain_v"]
    n_meas = parameters["repeated_measurements"]
    A_DAQ1 = parameters["a_daq1"]
    A_DAQ2 = parameters["a_daq2"]
    DEIS_offset = parameters["DEIS_offset"]

    # Crea il generatore di segnali
    signal = sg.SignalGenerator()

    """Crea l'oggetto generatore di segnali."""
    # daq = Agilent_U2351A.Agilent_U2351A('USB0::0x0957::0x0F18::TW54410533::0::INSTR') # U2351A
    daq = Agilent_U2351A.Agilent_U2351A("USB0::0x0957::0x1518::TW57160002::0::INSTR") # U2331A
    """Connetti al generatore di segnali."""
    daq.connect()
    daq.idn()

    """Configura il generatore di segnali."""
    daq.reset()
    daq.set_spi_channel()

    """ # Plotta il segnale generato
    plt.figure()
    plt.plot(signal.t_gen, signal.signal_gen)
    plt.title("Generated signal")
    plt.xlabel("time [s]")
    plt.ylabel("Amplitude [V]")

    plt.figure()
    plt.semilogx(
        np.fft.fftfreq(signal.N_gen, 1 / signal.Fs_gen),
        20 * np.log10(np.abs(np.fft.fft(signal.signal_gen) / signal.N_gen)),
        "b.",
    )
    plt.xlabel("frequency [Hz]")
    plt.ylabel("Magnitude [dB]") """

    if board_mode == "Galvanostat":
        daq.pot_galv_switch("galv")
        print("Modalità galvanostato impostata")
    elif board_mode == "Potentiostat":
        daq.pot_galv_switch("pot")
        print("Modalità potenziostato impostata")

    # daq.gainV(gain_v)  # Guadagno in tensione
    # daq.gainI(gain_i)  # Guadagno in corrente
  
    # Genera il segnale in base al tipo selezionato
    if signal_type == "MLS":
        signal.generate_mls(order=13, sig="mls")
    elif signal_type == "MS":
        signal.generate_multisine(sig="multiseno", DynamicEISOffset=DEIS_offset)
    elif signal_type == "S":
        for i in range(n_meas):
            for f0 in signal.f0_vector:
                signal.generate_single_sine(frequency=f0, sig="seno singolo")
                daq.prog_gen()
                msb = np.floor(signal.signal_vector / (2**8)).astype(int)  # byte più significativo
                lsb = (signal.signal_vector - (msb * (2**8))).astype(int)  # byte meno significativo
                test = np.vstack((lsb, msb)).reshape((2 * signal.N_gen,), order='F')

                daq.send_data(test)
                daq.config_gen(signal.Fs_gen)
                daq.prog_trigger()
                """Programming and Start acquisition."""
                daq.prog_acq(signal.N, signal.Fs, A_DAQ1, A_DAQ2)
                start_time = time.time()
                print('Output on ...')
                daq.start_acquisition()
                # Richiede i dati allo strumento
                signal_acq = daq.read_data()
                # Elaborazione del segnale
                daq.signal_processing_single_sine(signal_acq, signal.N, signal.Fs, f0, A_DAQ1, A_DAQ2, i)
                print(f'Misurazione alla frequenza {f0} Hz completata.')
        daq.pot_galv_switch("off")
        # Aggiorna lo stato a "completed" 
        with open(status_file, "w") as f:
            json.dump({
                "status": "completed",
                "completed": n_meas,
                "start_time": parameters.get("start_time", datetime.now().isoformat())
            }, f)
        daq.close()
        exit()

    for i in range(n_meas):
        
        daq.prog_gen()

        # Convert signal to adequate format for the instrument
        msb = np.floor(signal.signal_vector / (2**8)).astype(int)  # byte più significativo
        lsb = (signal.signal_vector - (msb * (2**8))).astype(int)  # byte meno significativo
        test = np.vstack((lsb, msb)).reshape((2 * signal.N_gen,), order='F')

        # Invia i dati definiti dall'utente al buffer dello strumento
        daq.send_data(test)

        daq.config_gen(signal.Fs_gen)
        daq.prog_trigger()

        """Programming and Start acquisition."""
        daq.prog_acq(signal.N, signal.Fs, A_DAQ1, A_DAQ2)

        import time
        start_time = time.time()
        print('Output on ...')

        daq.start_acquisition()

        # Richiede i dati allo strumento
        signal_acq = daq.read_data()

        # Elaborazione del segnale in base al tipo selezionato
        if signal_type == "MLS":
            daq.signal_processing_seq_mls(signal_acq, signal.N, signal.Fs, signal.f0_vector, A_DAQ1, A_DAQ2, i)
            # daq.plot_mls(i)
        elif signal_type == "MS":
            daq.signal_processing_multisine(signal_acq, signal.N, signal.Fs, signal.f0_vector, A_DAQ1, A_DAQ2, i)
            # daq.plot_multisine(i)

        print("Misurazione completata.")

    daq.pot_galv_switch("off")

    # Aggiorna lo stato a "completed" 
    with open(status_file, "w") as f:
        json.dump({
            "status": "completed",
            "completed": n_meas,
            "start_time": parameters.get("start_time", datetime.now().isoformat())
        }, f)

finally:
    # Chiudi la connessione al dispositivo
    daq.close()
