import matplotlib.pyplot as plt
import numpy as np
import pyvisa
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

# Establish connection
print('Attempting to create handle object for communication with DAQ')
rm = pyvisa.ResourceManager()
g = rm.open_resource('USB0::0x0957::0x0F18::TW54410533::0::INSTR')  # U2351A
print('Setto timeout')
g.timeout = 60000  # 60 secondi

# Open connection to server
print('Tentativo di apertura della comunicazione con DAQ')
g.open()

# Try sending SCPI string
g.write('*IDN?')
x = g.read()
print(f"Il risultato della query *IDN? è:", x)
print('-------------------------------------------')

# Reset and clear the device
g.write('*RST;*CLS')

# Programma il generatore di forme d'onda
print('Impostazione parametri generatore in corso ...')
g.write('ROUT:ENAB OFF,(@201)')  # disabilita le operazioni di output per il canale 201
g.write('ROUT:ENAB OFF,(@202)')  # disabilita le operazioni di output per il canale 202
g.write('ROUT:ENAB ON,(@201)')   # abilita le operazioni di output per il canale 201

# Convert signal to adequate format for the instrument
msb = np.floor(signal_vector / (2**8)).astype(int)  # byte più significativo
lsb = (signal_vector - (msb * (2**8))).astype(int)  # byte meno significativo
test = np.vstack((lsb, msb)).reshape((2 * N_gen,), order='F')

# Invia i dati definiti dall'utente al buffer dello strumento
g.write_binary_values(f'DATA #8{"{:08d}".format(2 * N_gen)}',
                                           test, datatype="B", termination='',
                                           header_fmt='empty')

# Verifica la presenza di errori
g.write('SYST:ERR?')
x = g.read()
print(x)

# Configura il generatore di forme d'onda
g.write('OUTP:WAV:ITER 1')  # Generate the waveform only once
g.write(f'OUTP:WAV:SRAT {Fs_gen}')  # Set the AO waveform sampling rate
g.write('APPL:USER (@201)')  # Send the user define pattern to channel 201

# Verifica la frequenza di campionamento impostata
g.write('OUTP:WAV:SRAT?')
x = g.read()
print(f'Frequenza di campionamento impostata: {x}')

# Verifica il segnale impostato sul canale 201
g.write('APPL? (@201)')
x = g.read()
print(f'Segnale impostato sul canale 201: {x}')

# Configura il canale 2 con un offset
g.write('SOUR:VOLT 0, (@202)')

print('Impostazione parametri generatore terminata.')

# Verifica la presenza di errori
g.write('SYST:ERR?')
x = g.read()
print(x)

print('---------------------------------------------------------------')

# Program trigger
g.write('CONF:DIG:DIR OUTP,(@501)')  # imposta il canale di output come trigger
g.write('OUTP:TRIG:SOUR EXTD')  # Set the EXTD_AO_TRIG pin as the output triggering
g.write('OUTP:TRIG:DTRG:POL POS')  # Set a positive edge trigger
g.write('OUTP:TRIG:TYP POST')  # Generate waveform immediately after receiving trigger

# Program acquisition
print('Impostazione parametri DAQ in corso ...')

g.write(f'ACQ:POIN {N}')  # imposta il numero di punti da acquisire
g.write('ACQ:POIN?') #interroga per sapere il numero di punti impostati
N_imp = int(g.read())
print(f'Numero di punti da acquisire impostato (N): {N_imp}')

g.write(f'ACQ:SRAT {Fs}')  # frequenza di campionamento
g.write('ACQ:SRAT?')
Fs_imp = int(g.read())
print(f'Frequenza di campionamento impostata (Fs): {Fs_imp}')

# Trigger
g.write('TRIG:SOUR NONE')
g.write('OUTPut:TRIGger:SOURce?')
trigger_src = g.read()
print(f'Sorgente del trigger impostata: {trigger_src}')
g.write('TRIG:SOUR EXTD')  # trigger digitale
g.write('TRIG:DTRG:POL POS')
g.write('TRIG:TYPE POST')  # post-trigger

# Imposta i canali da acquisire
current_ch = '(@101,108)'  # U2351A
g.write(f'ROUT:SCAN {current_ch}')  # lista di scansione dei canali
g.write('ROUT:SCAN?')
sc_l_imp = g.read()
print(f'Lista di scansione impostata: {sc_l_imp}')
g.write(f'ROUT:CHAN:STYP DIFF,(@108)')  # modalità differenziale
g.write(f'ROUT:CHAN:STYP DIFF,(@101)')  # modalità differenziale
g.write(f'ROUT:CHAN:POL BIP,{current_ch}')  # modalità bipolare
g.write(f'ROUT:CHAN:RANG {A_DAQ1},(@101)')  # range canale 1
g.write(f'ROUT:CHAN:RANG {A_DAQ2},(@108)')  # range canale 2
g.write(f'ROUT:CHAN:RANG? {current_ch}')
range_set = g.read()
print(f'Range impostato: {range_set}')

# Verifica la presenza di errori
g.write('SYST:ERR?')
x = g.read()
print(x)

print('Impostazione parametri DAQ terminata.')
print('-------------------------------------------')

# Esegui l'acquisizione
import time
start_time = time.time()
print('Output on ...')

# NOTA: se il comando OUTP ON è dato immediatamente prima di DIG, il ritardo è deterministico
#g.write('OUTP ON')  # genera il segnale dal canale 201

# Inizia la procedura di acquisizione single-shot
g.write('DIG')

# NOTA: se il comando OUTP ON è dato immediatamente dopo DIG, il ritardo è deterministico di 7 ms
g.write('OUTP ON')  # genera il segnale dal canale 201

# Verifica la presenza di errori
g.write('SYST:ERR?')
x = g.read()
print(x)

# Invia il trigger
g.write('SOUR:DIG:DATA:BIT 1, 0,(@501)')

print('Acquisizione in corso ...')

# Controlla che l'acquisizione sia terminata
acq_flag = False  # flag che indica la fine dell'acquisizione
acq_timer = 0  # timer dell'acquisizione (per controllo errori)
while not acq_flag and acq_timer < 1e5:
    acq_timer += 1
    g.write('WAV:COMP?')
    x = g.read()
    if x.strip() == 'YES':
        acq_flag = True

# Messaggio di errore se l'acquisizione non termina
if acq_timer == 1e5:
    print('Errore di comunicazione')

# Richiede i dati allo strumento
g.write('WAV:DATA?')

sig = g.read_raw()[10:]  # legge i dati in formato binario, rimuovendo l'header di 10 byte

# Converte i dati acquisiti
signal_acq = np.frombuffer(sig, dtype=np.int16)

# Estrae i canali acquisiti
sig_v = -signal_acq[0::2] * (A_DAQ1 / 2**15)  # [V] (conversione ampiezze ADC) per il canale 1
sig_i = signal_acq[1::2] * (A_DAQ2 / 2**15)  # [V] (conversione ampiezze ADC) per il canale 2

# Calcola le statistiche dei segnali acquisiti
mean_sig_v = np.mean(sig_v)
mean_sig_i = np.mean(sig_i)
std_sig_v = np.std(sig_v)
std_sig_i = np.std(sig_i)

print(f'Media del segnale V: {mean_sig_v}')
print(f'Media del segnale I: {mean_sig_i}')
print(f'Deviazione standard del segnale V: {std_sig_v}')
print(f'Deviazione standard del segnale I: {std_sig_i}')

# Verifica la presenza di saturazione nei segnali acquisiti
if np.max(np.abs(sig_v)) > (0.95 * A_DAQ1):
    print('--- Saturazione V ---')
if np.max(np.abs(sig_i)) > (0.95 * A_DAQ2):
    print('--- Saturazione I ---')

# Reset trigger bit
g.write('SOUR:DIG:DATA:BIT 0, 0,(@501)')
print('Acquisizione terminata.')

g.write('SYST:ERR?')  # DEBUG: check if there are errors
x = g.read()
print(x)

# Set the output to 0
print('Impostazione output a zero')
g.write('OUTP OFF')
g.write('SOUR:VOLT -0.0231, (@201)')

g.write('SYST:ERR?')  # DEBUG: check if there are errors
x = g.read()
print(x)

# Time base for plotting
t_base = np.arange(0, N/Fs, 1/Fs)

# Plot acquired signal
plt.figure(10)
plt.plot(t_base, sig_v, label='Voltage')
plt.plot(t_base, sig_i, label='Current')
plt.title('Acquired signal')
plt.xlabel('Time [s]')
plt.ylabel('Amplitude [V]')
plt.legend()
plt.grid(True)

# Remove transient and mean
sig_v = sig_v[N//2:] - np.mean(sig_v[N//2:])
sig_v = sig_v / 10  # Compensate for voltage gain

sig_i = sig_i[N//2:] / (0.1 * 91)  # Compensate for shunt resistance and current gain
sig_i = sig_i - np.mean(sig_i)

t_base = t_base[N//2:]

# Debug delay plot
plt.figure()
plt.plot(t_base, sig_v / np.max(np.abs(sig_v)), label='Voltage')
plt.plot(t_base, sig_i / np.max(np.abs(sig_i)), 'r', label='Current')
plt.title('Acquired signal normalized')
plt.xlabel('Time [s]')
plt.ylabel('Amplitude [V]')
plt.legend()
plt.grid(True)

# Plot without mean and transient
plt.figure()
plt.plot(t_base, sig_v, label='Voltage')
plt.plot(t_base, sig_i, 'r', label='Current')
plt.title('Acquired signal without mean and transient')
plt.xlabel('Time [s]')
plt.ylabel('Amplitude [V]')
plt.legend()
plt.grid(True)

# Update record length
N = N // 2
f_base = np.arange(0, Fs, Fs / N)

# Compute FFT
V = np.fft.fft(sig_v) / N
I = (np.fft.fft(sig_i) / N) * np.exp(-1j * 2 * np.pi * f_base / (Fs * 2.0))

idx_freq = np.round(N * np.array(f0_vector) / Fs).astype(int)

# Plot FFT magnitude
plt.figure()
plt.subplot(211)
plt.semilogx(f_base[idx_freq], 20 * np.log10(np.abs(V[idx_freq])), '.', label='Voltage')
plt.plot(f_base[idx_freq], 20 * np.log10(np.abs(I[idx_freq])), 'r.', label='Current')
plt.title('Acquired signal')
plt.xlabel('Frequency [Hz]')
plt.ylabel('Magnitude [dB]')
plt.legend()
plt.grid(True)

# Plot FFT phase
plt.subplot(212)
plt.semilogx(f_base[idx_freq], np.angle(V[idx_freq]), label='Voltage')
plt.plot(f_base[idx_freq], np.angle(I[idx_freq]), 'r', label='Current')
plt.title('Acquired signal')
plt.xlabel('Frequency [Hz]')
plt.ylabel('Phase [rad]')
plt.legend()
plt.grid(True)

# Compute impedance
V_peak = 2 * np.abs(V[idx_freq])
I_peak = 2 * np.abs(I[idx_freq])
Z_vector = V[idx_freq] / I[idx_freq]

# Close communication
if 'g' in locals():
    g.close()
    del g

# Plot impedance magnitude and phase
plt.figure()
plt.subplot(211)
plt.semilogx(f_base[idx_freq], 20 * np.log10(np.abs(Z_vector)), '-b.')
plt.xlabel('Frequency [Hz]')
plt.ylabel('Magnitude [dB]')
plt.grid(True)

plt.subplot(212)
plt.semilogx(f_base[idx_freq], np.rad2deg(np.angle(Z_vector)), '-b.')
plt.xlabel('Frequency [Hz]')
plt.ylabel('Phase [deg]')
plt.grid(True)

# Plot impedance in complex plane
plt.figure()
plt.plot(np.real(Z_vector), -np.imag(Z_vector), '.-')
plt.axis('equal')
plt.xlabel('Re(Z) [Ω]')
plt.ylabel('-Im(Z) [Ω]')
plt.grid(True)

plt.show()