import argparse
import time

import matplotlib.pyplot as plt
import numpy as np

import Agilent_U2351A
import Signal_Generation as sg


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Signal generation and acquisition interface."
    )

    # Argomenti principali
    parser.add_argument(
        "--signal-type",
        choices=["multiseno", "seno singolo", "mls"],
        help="Tipo di segnale da generare",
    )
    parser.add_argument("--frequency", type=float, help="Frequenza per seno singolo")
    parser.add_argument("--mls-order", type=int, help="Ordine del MLS")

    # Comando di operazione
    parser.add_argument(
        "--command",
        choices=["galv", "off", "pot", "gainv", "gaini", "misura"],
        help="Comando da eseguire",
    )

    # Parametri di acquisizione
    parser.add_argument(
        "--a-daq1", type=float, default=10.0, help="Acquisition amplitude range, ch1"
    )
    parser.add_argument(
        "--a-daq2", type=float, default=10.0, help="Acquisition amplitude range, ch2"
    )

    # Modalità interattiva
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Modalità interattiva per input comandi",
    )

    return parser.parse_args()


def generate_signal(signal_type, frequency=None, mls_order=None):
    """Generate signal based on type and parameters."""
    signal = sg.SignalGenerator()

    if signal_type == "multiseno":
        signal.generate_multisine("multiseno")
    elif signal_type == "seno singolo":
        if frequency is None:
            raise ValueError("Frequency must be provided for single sine signal")
        signal.generate_single_sine(frequency, "seno singolo")
    elif signal_type == "mls":
        if mls_order is None:
            raise ValueError("MLS order must be provided for MLS signal")
        signal.generate_mls(mls_order, "mls")
    else:
        raise ValueError(f"Invalid signal type: {signal_type}")

    return signal


def plot_generated_signal(signal):
    """Plot the generated signal and its spectrum."""
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
    plt.ylabel("Magnitude [dB]")


def configure_device():
    """Create and configure the DAQ device."""
    daq = Agilent_U2351A.Agilent_U2351A("USB0::0x0957::0x0F18::TW54410533::0::INSTR")
    daq.connect()
    daq.idn()
    daq.reset()
    daq.set_spi_channel()
    return daq


def process_command(daq, command, signal_type=None, signal=None, a_daq1=10, a_daq2=10):
    """Process the given command on the DAQ device."""
    if command == "galv":
        daq.pot_galv_switch("galv")
        print("Modalità galvanostato impostata")
        return False
    elif command == "off":
        daq.pot_galv_switch("off")
        print("Modalità neutra impostata")
        return False
    elif command == "pot":
        daq.pot_galv_switch("pot")
        print("Modalità potenziostato impostata")
        return False
    elif command == "gainv":
        daq.gainV()
        return False
    elif command == "gaini":
        daq.gainI()
        return False
    elif command == "misura":
        if signal is None or signal_type is None:
            raise ValueError(
                "Signal and signal_type must be provided for 'misura' command"
            )

        process_measurement(daq, signal_type, signal, a_daq1, a_daq2)
        return True  # Indica che la misurazione è stata completata
    else:
        print(f"Comando non riconosciuto: {command}")
        return False


def process_measurement(daq, signal_type, signal, a_daq1, a_daq2):
    """Process measurement based on signal type."""
    # Preparazione dei dati per lo strumento
    msb = np.floor(signal.signal_vector / (2**8)).astype(int)
    lsb = (signal.signal_vector - (msb * (2**8))).astype(int)
    test = np.vstack((lsb, msb)).reshape((2 * signal.N_gen,), order="F")

    if signal_type == "multiseno":
        daq.pot_galv_switch("galv")
        daq.prog_gen()
        daq.send_data(test)
        daq.config_gen(signal.Fs_gen)
        daq.prog_trigger()

        daq.prog_acq(signal.N, signal.Fs, a_daq1, a_daq2)

        print("Output on ...")
        daq.start_acquisition()
        signal_acq = daq.read_data()

        daq.signal_processing_multisine(
            signal_acq, signal.N, signal.Fs, signal.f0_vector, a_daq1, a_daq2
        )
        daq.pot_galv_switch("off")

        daq.plot_multisine()

    elif signal_type == "seno singolo":
        for f0 in signal.f0_vector:
            daq.pot_galv_switch("galv")
            daq.prog_gen()
            daq.send_data(test)
            daq.config_gen(signal.Fs_gen)
            daq.prog_trigger()

            # Parametri di acquisizione
            Nsamples_per_period = 100
            Fs = int(Nsamples_per_period * f0)
            N = int(Nsamples_per_period * signal.N_periods)

            daq.prog_acq(N, Fs, a_daq1, a_daq2)

            print("Output on ...")
            daq.start_acquisition()
            signal_acq = daq.read_data()

            sig_V_I_filename = f"sig_V_I_{f0}.csv"
            daq.signal_processing_single_sine(
                signal_acq, N, Fs, f0, a_daq1, a_daq2, sig_V_I_filename
            )
            daq.pot_galv_switch("off")

    elif signal_type == "mls":
        daq.pot_galv_switch("galv")
        daq.prog_gen()
        daq.send_data(test)
        daq.config_gen(signal.Fs_gen)
        daq.prog_trigger()

        daq.prog_acq(signal.N, signal.Fs, a_daq1, a_daq2)

        print("Output on ...")
        daq.start_acquisition()
        signal_acq = daq.read_data()

        daq.signal_processing_seq_mls(
            signal_acq, signal.N, signal.Fs, signal.f0_vector, a_daq1, a_daq2
        )
        daq.pot_galv_switch("off")
        time.sleep(2)

        daq.plot_mls()


def interactive_mode(daq, signal_type=None, signal=None, a_daq1=10, a_daq2=10):
    """Run the interactive command prompt."""
    while True:
        user_input = (
            input(
                "Inserisci il comando " "(galv, off, pot, gainv, gaini, misura, exit): "
            )
            .strip()
            .lower()
        )

        if user_input == "exit":
            break

        if user_input == "misura":
            if signal is None:
                print("Errore: nessun segnale generato. Generare prima un segnale.")
                continue

            measurement_completed = True
            while measurement_completed:
                measurement_completed = process_command(
                    daq, user_input, signal_type, signal, a_daq1, a_daq2
                )
                if measurement_completed:
                    repeat = (
                        input("Vuoi ripetere la misurazione? (s/n): ").strip().lower()
                    )
                    if repeat != "s" and repeat != "si" and repeat != "sì":
                        break
        else:
            process_command(daq, user_input)


def main():
    """Main function to coordinate signal generation and acquisition."""
    np.random.seed(1)
    args = parse_arguments()

    # Gestione modalità interattiva per il tipo di segnale
    signal_type = args.signal_type
    signal = None

    if signal_type is None and args.interactive:
        signal_type = (
            input(
                "inserisci il segnale da generare tra"
                ' "multiseno", "seno singolo" e "mls" : '
            )
            .strip()
            .lower()
        )

    # Creazione del segnale
    if signal_type == "multiseno":
        signal = generate_signal("multiseno")
    elif signal_type == "seno singolo":
        frequency = args.frequency
        if frequency is None and args.interactive:
            frequency = float(input("inserisci la frequenza del segnale: "))
        signal = generate_signal("seno singolo", frequency=frequency)
    elif signal_type == "mls":
        mls_order = args.mls_order
        if mls_order is None and args.interactive:
            mls_order = int(input("inserisci l'ordine del mls: "))
        signal = generate_signal("mls", mls_order=mls_order)

    if signal:
        plot_generated_signal(signal)

    # Configurazione del dispositivo
    daq = configure_device()

    # Gestione dei comandi
    if args.interactive:
        interactive_mode(daq, signal_type, signal, args.a_daq1, args.a_daq2)
    elif args.command:
        process_command(
            daq, args.command, signal_type, signal, args.a_daq1, args.a_daq2
        )

    # Chiusura del dispositivo
    daq.close()


if __name__ == "__main__":
    main()
