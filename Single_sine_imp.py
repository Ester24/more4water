import matplotlib.pyplot as plt
import numpy as np
import Agilent_U2351A
import time

np.random.seed(1)

# Nome del file per z_vector
z_vector_filename = 'z_vector.csv'

f0_vector = np.array([0.05, 0.1, 0.2, 0.4, 1, 2, 4, 10, 20, 40,
                      100, 200, 400, 1000])
# f0_vector = np.array([100, 200])
                      
A_DAQ1 = 10 #Acquisition amplitude range, ch1
A_DAQ2 = 10 #Acquisition amplitude range, ch2

# Crea l'oggetto generatore di segnali
daq = Agilent_U2351A.Agilent_U2351A('USB0::0x0957::0x0F18::TW54410533::0::INSTR')

# Connetti al generatore di segnali
daq.connect()
daq.idn()

# Configura il generatore di segnali
daq.reset()
daq.set_spi_channel()


while True:
    user_input = input("Inserisci il comando galv, off, gainv, misura, exit: ").strip().lower()
    if user_input == 'galv':
        daq.pot_galv_switch('galv')
    elif user_input == 'gainv':
        daq.gainV()
    elif user_input == 'off':   
        daq.pot_galv_switch('off')
    elif user_input == 'misura':
        for f0 in f0_vector:
            daq.pot_galv_switch('galv')
            # Parametri di generazione del segnale
            A_gen = 0.005  # Valore massimo = 1
            Fs_gen = 100 * f0  # Frequenza di campionamento per la generazione
            N_periods = 4 # Numero di periodi della sinusoide da acquisire
            T_gen = N_periods / f0  # Durata
            print(T_gen)
            Ts_gen = 1 / Fs_gen  # Periodo di campionamento per la generazione
            N_gen = int(np.ceil(T_gen / Ts_gen))  # Lunghezza del record di generazione

            t_gen = np.arange(0, N_gen / Fs_gen, 1 / Fs_gen)
            signal_gen = A_gen * np.sin(2 * np.pi * f0 * t_gen)

            # Rappresenta il segnale con livelli a 16 bit
            signal_vector = np.floor(signal_gen * 2**15) + 2**15

            plt.figure()
            plt.plot(t_gen, signal_gen)
            plt.title(f'Generated Sine Signal at {f0} Hz')
            plt.xlabel('time [s]')
            plt.ylabel('Amplitude [V]')
            plt.show()

            daq.prog_gen()

            # Converti il segnale nel formato adeguato per lo strumento
            msb = np.floor(signal_vector / (2**8)).astype(int)  # byte più significativo
            lsb = (signal_vector - (msb * (2**8))).astype(int)  # byte meno significativo
            test = np.vstack((lsb, msb)).reshape((2 * N_gen,), order='F')

            # Invia i dati definiti dall'utente al buffer dello strumento
            daq.send_data(test)

            daq.config_gen(Fs_gen)
            daq.prog_trigger()

            # Parametri di acquisizione
            Nsamples_per_period = 100  # Numero di campioni per periodo della sinusoide
            Fs = int(Nsamples_per_period * f0)  # Frequenza di campionamento di acquisizione
            N = int(Nsamples_per_period * N_periods)  # Numero di punti da acquisire

            daq.prog_acq(N, Fs, A_DAQ1, A_DAQ2)

            start_time = time.time()
            print('Output on ...')

            daq.start_acquisition()

            # Richiede i dati allo strumento
            signal_acq = daq.read_data()
            # Genera nomi di file univoci per ogni frequenza
            sig_V_I_filename = f'sig_V_I_{f0}.csv'


            daq.signal_processing_single_sine(signal_acq, N, Fs, f0, A_DAQ1, A_DAQ2, sig_V_I_filename, z_vector_filename)
            daq.pot_galv_switch('off')

        #daq.plot_signals()
    elif user_input == 'exit':
        break
    else:
        print("Comando non riconosciuto. Riprova.")
daq.close()


    

