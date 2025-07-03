import matplotlib.pyplot as plt
import numpy as np
import Agilent_U2351A
import time
import Signal_Generation as sg

np.random.seed(1)

#Acquisition parameters
A_DAQ1 = 10 #Acquisition amplitude range, ch1
A_DAQ2 = 10 #Acquisition amplitude range, ch2

#Build signal
signal = sg.SignalGenerator()
signal_input = input('inserisci il segnale da generare tra' \
        ' "multiseno", "seno singolo" e "mls" : ').strip().lower()
match signal_input:
    case 'multiseno':
        signal.generate_multisine('multiseno')
    case 'seno singolo':
        signal.generate_single_sine(float(input('inserisci la frequenza del segnale: ')), 'seno singolo')
    case 'mls':
        order = int(input('inserisci l\'ordine del mls: '))
        signal.generate_mls(order, 'mls')


plt.figure()
plt.plot(signal.t_gen, signal.signal_gen)
plt.title('Generated signal')
plt.xlabel('time [s]')
plt.ylabel('Amplitude [V]')

plt.figure()
plt.semilogx(np.fft.fftfreq(signal.N_gen, 1/signal.Fs_gen),
              20 * np.log10(np.abs(np.fft.fft(signal.signal_gen) / signal.N_gen)), 'b.')
plt.xlabel('frequency [Hz]')
plt.ylabel('Magnitude [dB]')
"""Create the signal generator object."""
daq = Agilent_U2351A.Agilent_U2351A('USB0::0x0957::0x0F18::TW54410533::0::INSTR')

"""Connect to the signal generator."""
daq.connect()
daq.idn()

"""Configure the signal generator."""
daq.reset()
daq.set_spi_channel()
while True:
    user_input = input("Inserisci il comando "
            "(galv, off, pot, gainv, gaini, misura, exit): ").strip().lower()
    if user_input == 'galv':
        daq.pot_galv_switch('galv')
        print('Modalità galvanostato impostata')   
    elif user_input == 'off':
        daq.pot_galv_switch('off')
        print('Modalità neutra impostata')
    elif user_input == 'pot':
        daq.pot_galv_switch('pot')
        print('Modalità potenziostato impostata')
    elif user_input == 'gainv':
        daq.gainV()
    elif user_input == 'gaini':
        daq.gainI()
    elif user_input == 'misura':
        match signal_input:
            case 'multiseno':
                daq.pot_galv_switch('galv')
            
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

                daq.signal_processing_multisine(signal_acq, signal.N, signal.Fs, signal.f0_vector, A_DAQ1, A_DAQ2)
                daq.pot_galv_switch('off')

                daq.plot_multisine()
            case 'seno singolo':
                for f0 in signal.f0_vector:
                    daq.pot_galv_switch('galv')
                
                    daq.prog_gen()

                    # Convert signal to adequate format for the instrument
                    msb = np.floor(signal.signal_vector / (2**8)).astype(int)  # byte più significativo
                    lsb = (signal.signal_vector - (msb * (2**8))).astype(int)  # byte meno significativo
                    test = np.vstack((lsb, msb)).reshape((2 * signal.N_gen,), order='F')

                    # Invia i dati definiti dall'utente al buffer dello strumento
                    daq.send_data(test)

                    daq.config_gen(signal.Fs_gen)
                    daq.prog_trigger()

                    # Parametri di acquisizione
                    Nsamples_per_period = 100  # Numero di campioni per periodo della sinusoide
                    Fs = int(Nsamples_per_period * f0)  # Frequenza di campionamento di acquisizione
                    N = int(Nsamples_per_period * signal.N_periods)  # Numero di punti da acquisire

                    daq.prog_acq(N, Fs, A_DAQ1, A_DAQ2)

                    start_time = time.time()
                    print('Output on ...')

                    daq.start_acquisition()

                    # Richiede i dati allo strumento
                    signal_acq = daq.read_data()
                    # Genera nomi di file univoci per ogni frequenza
                    sig_V_I_filename = f'sig_V_I_{f0}.csv'


                    daq.signal_processing_single_sine(signal_acq, N, Fs, f0, A_DAQ1, A_DAQ2, sig_V_I_filename)
                    daq.pot_galv_switch('off')
            case 'mls':
                daq.pot_galv_switch('galv')
       
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

                daq.signal_processing_seq_mls(signal_acq, signal.N, signal.Fs, signal.f0_vector, A_DAQ1, A_DAQ2)
                daq.pot_galv_switch('off')
                time.sleep(2)

                daq.plot_mls()
    elif user_input == 'exit':
        break
    else:
        print("Comando non riconosciuto. Riprova.")

daq.close()