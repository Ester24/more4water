import matplotlib.pyplot as plt
import numpy as np
import Agilent_U2351A
import time

np.random.seed(1)

#Acquisition parameters
Fs = 1e4 #Acquisition sampling frequency
N = int(40*Fs) # Number of point to acquire
A_DAQ1 = 10 #Acquisition amplitude range, ch1
A_DAQ2 = 10 #Acquisition amplitude range, ch2

#Build signal
#Signal generation parameters
A_gen = 0.005 #Maximum value = 1
T_gen = 40 #Duration
Fs_gen = 2e4 #Generation sampling frequency
Ts_gen = 1/Fs_gen #Generation sampling period
N_gen = int(np.ceil(T_gen/Ts_gen)) #generation record length

f0_vector = np.array([0.05, 0.1, 0.2, 0.4, 1, 2, 4, 10, 20, 40,
                      100, 200, 400, 1000])

#Check if fs is a multiple of all frequencies
check_multiple_freq = np.sum(Fs/f0_vector)

#Mesurement
t_gen = np.arange(0, N_gen / Fs_gen, 1/Fs_gen)
signal_gen = np.zeros_like(t_gen)

for f0 in f0_vector:
    signal_gen += A_gen * np.sin(2* np.pi * f0 * t_gen +
                                 2 * np.pi * np.random.rand())

#Represent signal by 16-bit levels
signal_vector = np.floor(signal_gen * 2**15) + 2**15

plt.figure()
plt.plot(t_gen, signal_gen)
plt.title('Generated signal')
plt.xlabel('time [s]')
plt.ylabel('Amplitude [V]')

plt.figure()
plt.semilogx(np.fft.fftfreq(N_gen, 1/Fs_gen), 20 * np.log10(np.abs(np.fft.fft(signal_gen) / N_gen)), 'b.')
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

        daq.pot_galv_switch('galv')
       
        daq.prog_gen()

        # Convert signal to adequate format for the instrument
        msb = np.floor(signal_vector / (2**8)).astype(int)  # byte più significativo
        lsb = (signal_vector - (msb * (2**8))).astype(int)  # byte meno significativo
        test = np.vstack((lsb, msb)).reshape((2 * N_gen,), order='F')

        # Invia i dati definiti dall'utente al buffer dello strumento
        daq.send_data(test)

        daq.config_gen(Fs_gen)
        daq.prog_trigger()

        """Programming and Start acquisition."""
        daq.prog_acq(N, Fs, A_DAQ1, A_DAQ2)

        import time
        start_time = time.time()
        print('Output on ...')

        daq.start_acquisition()

        # Richiede i dati allo strumento
        signal_acq = daq.read_data()

        daq.signal_processing_multisine(signal_acq, N, Fs, f0_vector, A_DAQ1, A_DAQ2)
        daq.pot_galv_switch('off')

        daq.plot_multisine()
    elif user_input == 'exit':
        break
    else:
        print("Comando non riconosciuto. Riprova.")


daq.close()


