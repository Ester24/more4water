import pyvisa
import matplotlib.pyplot as plt
import time
import pandas as pd
import numpy as np
from pathlib import Path

class Agilent_U2351A:
    def __init__(self, resource: str = 'USB0::0x0957::0x0F18::TW54410533::0::INSTR', output_dir: str = "output_csv"):
        """Initialize the Agilent U2351A device."""
        self.rm = pyvisa.ResourceManager()
        self.resource = resource
        self.device = None
        self.output_dir = Path(output_dir)  # Usa pathlib per gestire il percorso
        self.output_dir.mkdir(parents=True, exist_ok=True)  # Crea la directory se non esiste

    def __enter__(self):
        """Establish a connection to the device."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        """Close the connection to the device."""
        self.close()
     
    def connect(self):
        """Establish a connection to the device.
        
            If no resource is provided, it will list all available
            resources and connect to the first one.
        """
        try:
            if not self.resource:
                resources = self.rm.list_resources()
                if not resources:
                    raise ValueError("No resources found.")
                self.resource = resources[0]

            # Open connection to the device
            self.device = self.rm.open_resource(self.resource)
        
            # Open connection to server
            self.device.open()

        except Exception as e:
            print(f'Connection failed: {e}')
            self.device = None

    def idn(self):
        """Verify the IDN of the device.
        
            This method sends the *IDN? command to the device 
            and prints the response to verify if the device is connected.
        """
        if self.device:
            try:
                idn = self.device.query('*IDN?')
                print(f"IDN: {idn}")
            except Exception as e:
                print(f'Failed to verify IDN: {e}')
        else:
            print("No device connected.")

    def reset(self):
        """This method resets and clear the device."""
        if self.device:
            try:
                self.device.write('*RST;*CLS')
                print("Device reset.")
            except Exception as e:
                print(f'Failed to reset device: {e}')
        else:
            print("No device connected.")

    def send_data(self, data):
        """Send data to the device.

        data: array of data to be sent to the device. Data is generated in the following way:
            msb = np.floor(signal_vector / (2**8)).astype(int)  # Most significant byte
            lsb = (signal_vector - (msb * (2**8))).astype(int)  # Least significant byte
            data = np.vstack((lsb, msb)).reshape((2 * N_gen,), order='F') 
        """
        if self.device:
            try:
                self.device.write_binary_values(f'DATA #8{"{:08d}".format(len(data))}', data, datatype="B", termination='', header_fmt='empty')
            except Exception as e:
                print(f'Failed to send data to the device: {e}')
        else:
            print("No device connected.")        
    
    def prog_gen(self):
        """Program the signal generator."""
        if self.device:
            try:
                print("Setting parameter of signal generator...")
                self.device.write('ROUT:ENAB OFF,(@201)') # Disable output for channel 201
                self.device.write('ROUT:ENAB OFF,(@202)') # Disable output for channel 202
                self.device.write('ROUT:ENAB ON,(@201)') # Enable output for channel 201
            except Exception as e:
                print(f'Failed to program the signal generator: {e}')
        else:
            print("No device connected.")
   
    def config_gen(self, Fs_gen):
        """Configure the signal generator.
            Fs_gen: generation sampling frequency
        """
        print("Configuring signal generator...")
        self.device.write('OUTP:WAV:ITER 1') # Genrate a single waveform
        self.device.write(f'OUTP:WAV:SRAT {Fs_gen}') # Set the sample rate of the signal generator
        self.device.write('APPL:USER (@201)') # Send the user define pattern to the signal generator
        """Check frequency and amplitude of the signal generator."""
        self.device.write('OUTP:WAV:SRAT?') # Query the sample rate of the signal generator
        print(f'Sample rate: {self.device.read()}')
        self.device.write('APPL? (@201)')
        print(f'User define pattern: {self.device.read()}')
        self.device.write('SOUR:VOLT 3.49, (@202)') # Set the output voltage to 3.6V for battery test
        # self.device.write('SOUR:VOLT 0, (@202)') # Set the output voltage to 0V for resistor test
        self.check_error()
        print('Parameter configured.')
    
    def set_spi_channel(self):
        """Set the SPI channel."""
        if self.device:
            try:
                self.device.write('CONF:DIG:DIR OUTP,(@501)') # Set the channel 501 as the output
                self.device.write('CONF:DIG:DIR OUTP,(@502)') # Set the channel 502 as the output
                self.device.write('CONF:DIG:DIR OUTP,(@503)') # Set the channel 503 as the output
                self.device.write('SOUR:DIG:DATA:BIT 1, 1,(@501)') # Set bit 1 of channel 501 as high
                self.device.write('SOUR:DIG:DATA:BIT 1, 2,(@501)') # Set bit 2 of channel 501 as high
                self.device.write('SOUR:DIG:DATA:BIT 1, 3,(@501)') # Set bit 3 of channel 501 as high
            except Exception as e:
                print(f'Failed to set the SPI channel: {e}')
    
    def prog_trigger(self):
        if self.device:
            try:
                #self.device.write('CONF:DIG:DIR OUTP,(@501)')  # Set the channel 501 as the output
                self.device.write('OUTP:TRIG:SOUR EXTD')  # Set the EXTD_AO_TRIG pin as the output triggering
                self.device.write('OUTP:TRIG:DTRG:POL POS')  # Set a positive edge trigger
                self.device.write('OUTP:TRIG:TYP POST')  # Generate waveform immediately after receiving trigger
            except Exception as e:
                print(f'Failed to program the trigger: {e}')
        else:
            print("No device connected.")
    
    def prog_acq(self, N, Fs, A_DAQ1, A_DAQ2):
        """Setting DAQ acquisition parameters.

            N: number of points to be acquired
            Fs: acquisition sampling frequency
            A_DAQ1: acquisition amplitude range, ch1
            A_DAQ2: acquisistion amplitude range, ch2

        """
        print("Setting acquisition parameters...")
        self.device.write(f'ACQ:POIN {N}') # Set the number of points to be acquired
        self.device.write('ACQ:POIN?') # Query the number of points to be acquired
        print(f'Number of points: {self.device.read()}')
        self.device.write(f'ACQ:SRAT {Fs}') # Set the sample rate of the acquisition
        self.device.write('ACQ:SRAT?') # Query the sample rate of the acquisition
        print(f'Sample rate: {self.device.read()}')

        """Set the trigger source."""
        self.device.write('TRIG:SOUR NONE')
        self.device.write('OUTPut:TRIGger:SOURce?')
        print(f'Trigger source setted: {self.device.read()}')
        self.device.write('TRIG:SOUR EXTD') # Digital trigger
        self.device.write('TRIG:DTRG:POL POS')
        self.device.write('TRIG:TYP POST') # Post trigger

        """Set channel to be acquired."""
        # current_ch = '(@101,108)'  # U2351A
        current_ch = '(@101,104)'  # U2331A
        self.device.write(f'ROUT:SCAN {current_ch}')
        self.device.write('ROUT:SCAN?')
        sc_l_imp = self.device.read()
        print(f'Scan list set: {sc_l_imp}')
        # self.device.write(f'ROUT:CHAN:STYP DIFF,(@108)') # Differential mode U2351A
        self.device.write(f'ROUT:CHAN:STYP DIFF,(@104)') # Differential mode U2331A
        self.device.write(f'ROUT:CHAN:STYP DIFF,(@101)') # Differential mode
        self.device.write(f'ROUT:CHAN:POL BIP,{current_ch}') # Bipolar mode
        self.device.write(f'ROUT:CHAN:RANG {A_DAQ1},(@101)') # Range of channel 1
        # self.device.write(f'ROUT:CHAN:RANG {A_DAQ2},(@108)') # Range of channel 2 U2351A
        self.device.write(f'ROUT:CHAN:RANG {A_DAQ2},(@104)') # Range of channel 2 U2331A
        self.device.write(f'ROUT:CHAN:RANG? {current_ch}')
        print(f'Range set: {self.device.read()}')
        self.check_error()
        print("Acquisition parameters setted.")

    def start_acquisition(self):
        """Start the acquisition."""
        if self.device:
            try:
                self.device.write('DIG') # Start the acquisition single-shot
                self.device.write('OUTP ON')  # Generate signal on channel 201
                self.check_error()
                self.device.write('SOUR:DIG:DATA:BIT 1, 0,(@501)') # Send trigger signal to the device

                acq_flag = False  # flag che indica la fine dell'acquisizione
                acq_timer = 0  # timer dell'acquisizione (per controllo errori)
                while not acq_flag and acq_timer < 1e5:
                    acq_timer += 1
                    self.device.write('WAV:COMP?')
                    x = self.device.read()
                    if x.strip() == 'YES':
                        acq_flag = True

                if acq_timer == 1e5:
                    print('Errore di comunicazione')
                    return False
                return True
            except Exception as e:
                print(f'Failed to start the acquisition: {e}')
        else:
            print("No device connected.")
        return False
        "WIP"
        raise NotImplementedError("Stop acquisition not implemented yet.")

        """Stop the acquisition."""
        if self.device:
            try:
                self.device.write("OUTP OFF")  # Stop the output signal
                self.device.write("DIG:STOP")  # Stop the acquisition
                self.check_error()
            except Exception as e:
                print(f"Failed to stop the acquisition: {e}")
        else:
            print("No device connected.")

    def read_data(self):
        """Read the acquired data."""
        if self.device:
            try:
                self.device.write('WAV:DATA?')
                sig = self.device.read_raw()[10:]
                return np.frombuffer(sig, dtype=np.int16)
            except Exception as e:
                print(f'Failed to read the acquired data: {e}')
                return None
        else:
            print("No device connected.")
            return None

    def signal_processing_multisine(self, signal_acq, N, Fs, f0_vector, A_DAQ1, A_DAQ2, i):
        if self.device:
            try:
                """Process the acquired signal.

                    signal_acq: acquired signal from read_data()
                    N: number of points acquired, integer
                    Fs: acquisition sampling frequency, integer
                    f0_vector: frequency vector
                    A_DAQ1: acquisition amplitude range, ch1, integer
                    A_DAQ2: acquisistion amplitude range, ch2, integer
                    i = index of the current measurement
                """

                """Extract the acquired channels."""
                sig_v = signal_acq[0::2] * (A_DAQ1 / 2**15) # [V] (conversione ampiezze ADC) per il canale 1
                sig_i = -signal_acq[1::2] * (A_DAQ2 / 2**15) # [V] (conversione ampiezze ADC) per il canale 2

                """Calcola le statistiche dei segnali acquisiti."""
                mean_sig_v = np.mean(sig_v) # Media del segnale V   
                mean_sig_i = np.mean(sig_i)
                std_sig_v = np.std(sig_v) # Deviazione standard del segnale V
                std_sig_i = np.std(sig_i)

                """Stampa le statistiche dei segnali acquisiti."""
                print(f'Media del segnale V: {mean_sig_v}')
                print(f'Media del segnale I: {mean_sig_i}')
                print(f'Deviazione standard del segnale V: {std_sig_v}')
                print(f'Deviazione standard del segnale I: {std_sig_i}')

                """Verifica la presenza di saturazione nei segnali acquisiti."""
                if np.max(np.abs(sig_v)) > (0.95 * A_DAQ1):
                    print('--- Saturazione V ---')
                if np.max(np.abs(sig_i)) > (0.95 * A_DAQ2):
                    print('--- Saturazione I ---')

                self.res_trig_out()

                # Time base for plotting
                t_base = np.arange(0, N/Fs, 1/Fs)

                # Percorsi per salvare i file CSV
                sig_v_i_filename = self.output_dir / f'sig_V_I_multi_{i}.csv'
                z_vector_filename = self.output_dir / f'z_vector_multi_{i}.csv'

                # Save sig_v to CSV
                df_sig_V_I = pd.DataFrame({'Time [s]': np.round(t_base, 5), 'Voltage [V]': np.round(sig_v, 6),
                                           'Current [I]': np.round(sig_i, 6)})
                df_sig_V_I.to_csv(sig_v_i_filename, index=False)

                # Remove transient and mean
                sig_v = sig_v[N//2:] - np.mean(sig_v[N//2:])
                pendenzaV = 9.9108
                intercettaV = -0.4180
                #sig_v_rtm = sig_v / 10  # Compensate for voltage gain
                sig_v_rtm = (sig_v / pendenzaV) - (intercettaV / pendenzaV)

                # sig_i = sig_i[N//2:] / (0.1 * 91)  # Compensate for shunt resistance and current gain
                pendenzaI = 88.758
                intercettaI = -0.028
                sig_i = ((sig_i[N//2:] / pendenzaI) * 10) - (intercettaI / pendenzaI)
                sig_i_rtm = sig_i - np.mean(sig_i)

                t_base = t_base[N//2:]

                # Update record length
                N = N // 2
                f_base = np.arange(0, Fs, Fs / N)

                # Compute FFT
                V = np.fft.fft(sig_v_rtm) / N
                I = (np.fft.fft(sig_i_rtm) / N) * np.exp(-1j * 2 * np.pi * f_base / (Fs * 2.0))

                idx_freq = np.round(N * np.array(f0_vector) / Fs).astype(int)

                # Compute impedance
                V_peak = 2 * np.abs(V[idx_freq])
                I_peak = 2 * np.abs(I[idx_freq])
                Z_vector = V[idx_freq] / I[idx_freq]
                
                # Save Z_vector to CSV
                df_z_vector = pd.DataFrame({
                    'Frequency [Hz]': np.round(f_base[idx_freq], 5),
                    'Re(Z)': np.round(np.real(Z_vector), 5),
                    'Im(Z)': np.round(np.imag(Z_vector), 5)
                })
                df_z_vector.to_csv(z_vector_filename, index=False)
            except Exception as e:
                print(f'Failed to process the acquired signal: {e}')
        else:
            print("No device connected.")
    
    def signal_processing_single_sine(self, signal_acq, N, Fs, f0, A_DAQ1, A_DAQ2, i):
        if self.device:
            try:
                """Process the acquired signal for single sine.

                    signal_acq: acquired signal from read_data()
                    N: number of points acquired, integer
                    Fs: acquisition sampling frequency, integer
                    f0: current frequency
                    A_DAQ1: acquisition amplitude range, ch1, integer
                    A_DAQ2: acquisistion amplitude range, ch2, integer
                    i = index of the current measurement
                """

                """Extract the acquired channels."""
                sig_v = signal_acq[0::2] * (A_DAQ1 / 2**15) # [V] (conversione ampiezze ADC) per il canale 1
                sig_i = -signal_acq[1::2] * (A_DAQ2 / 2**15) # [V] (conversione ampiezze ADC) per il canale 2

                """Calcola le statistiche dei segnali acquisiti."""
                mean_sig_v = np.mean(sig_v) # Media del segnale V   
                mean_sig_i = np.mean(sig_i)
                std_sig_v = np.std(sig_v) # Deviazione standard del segnale V
                std_sig_i = np.std(sig_i)

                """Stampa le statistiche dei segnali acquisiti."""
                print(f'Media del segnale V: {mean_sig_v}')
                print(f'Media del segnale I: {mean_sig_i}')
                print(f'Deviazione standard del segnale V: {std_sig_v}')
                print(f'Deviazione standard del segnale I: {std_sig_i}')

                """Verifica la presenza di saturazione nei segnali acquisiti."""
                if np.max(np.abs(sig_v)) > (0.95 * A_DAQ1):
                    print('--- Saturazione V ---')
                if np.max(np.abs(sig_i)) > (0.95 * A_DAQ2):
                    print('--- Saturazione I ---')

                self.res_trig_out()

                # Time base for plotting
                t_base = np.arange(0, N/Fs, 1/Fs)

                sig_V_I_filename = f'sig_V_I_single_{i}.csv'
                
                # Save sig_v to CSV
                df_sig_V_I = pd.DataFrame({'Time [s]': np.round(t_base, 5), 'Frequency [Hz]' : np.round(f0, 2),
                                            'Voltage [V]': np.round(sig_v, 6),
                                           'Current [I]': np.round(sig_i, 6)})
                
                try:
                    # Prova a leggere il file per verificare se esiste
                    pd.read_csv(self.output_dir / sig_V_I_filename)
                    # Se il file esiste, aggiungi i dati senza intestazione
                    df_sig_V_I.to_csv(self.output_dir / sig_V_I_filename, mode='a', header=False, index=False)
                except FileNotFoundError:
                    # Se il file non esiste, crealo con l'intestazione
                    df_sig_V_I.to_csv(self.output_dir / sig_V_I_filename, mode='w', header=True, index=False)

                # Remove transient and mean
                sig_v = sig_v[N//2:] - np.mean(sig_v[N//2:])
                pendenza = 9.9108
                intercetta = -0.4180
                #sig_v_rtm = sig_v / 10  # Compensate for voltage gain
                sig_v_rtm = (sig_v / pendenza) - (intercetta / pendenza)

                # sig_i = sig_i[N//2:] / (0.1 * 91)  # Compensate for shunt resistance and current gain
                pendenzaI = 88.758
                intercettaI = -0.028
                sig_i = ((sig_i[N//2:] / pendenzaI) * 10) - (intercettaI / pendenzaI)
                sig_i_rtm = sig_i - np.mean(sig_i)

                t_base = t_base[N//2:]

                # Update record length
                N = N // 2
                f_base = np.arange(0, Fs, Fs / N)

                # Compute FFT
                V = np.fft.fft(sig_v_rtm) / N
                I = (np.fft.fft(sig_i_rtm) / N) * np.exp(-1j * 2 * np.pi * f_base / (Fs * 2.0))

                idx_freq = np.round(N * f0 / Fs).astype(int)

                # Compute impedance (un solo valore per questa frequenza)
                Z_value = V[idx_freq] / I[idx_freq]

                # Nome del file CSV per z_vector
                z_vector_filename = f'z_vector_single_{i}.csv'

                # Salva una riga per ogni frequenza (append)
                df_z_vector = pd.DataFrame([{
                    'Frequency [Hz]': np.round(f_base[idx_freq], 5),
                    'Re(Z)': np.round(np.real(Z_value), 5),
                    'Im(Z)': np.round(np.imag(Z_value), 5)
                }])

                try:
                    # Prova a leggere il file per verificare se esiste
                    pd.read_csv(self.output_dir / z_vector_filename)
                    # Se il file esiste, aggiungi la riga senza intestazione
                    df_z_vector.to_csv(self.output_dir / z_vector_filename, mode='a', header=False, index=False)
                except FileNotFoundError:
                    # Se il file non esiste, crealo con l'intestazione
                    df_z_vector.to_csv(self.output_dir / z_vector_filename, mode='w', header=True, index=False)

                print(f"Data saved to {self.output_dir / sig_V_I_filename}, and {self.output_dir / z_vector_filename}")

            except Exception as e:
                print(f'Failed to process the acquired signal: {e}')
        else:
            print("No device connected.")

    def signal_processing_seq_mls(self, signal_acq, N, Fs, f0_vector, A_DAQ1, A_DAQ2, i):
        if self.device:
            try:
                """Process the acquired signal for MLS.

                    signal_acq: acquired signal from read_data()
                    N: number of points acquired, integer
                    Fs: acquisition sampling frequency, integer
                    f0_vector: frequency vector
                    Ts_gen: generation sampling period
                    Ts: acquisition sampling period
                    A_DAQ1: acquisition amplitude range, ch1, integer
                    A_DAQ2: acquisistion amplitude range, ch2, integer
                    i = index of the current measurement
                """

                """Extract the acquired channels."""
                sig_v = signal_acq[0::2] * (A_DAQ1 / 2**15) # [V] (conversione ampiezze ADC) per il canale 1
                sig_i = -signal_acq[1::2] * (A_DAQ2 / 2**15) # [V] (conversione ampiezze ADC) per il canale 2

                """Calcola le statistiche dei segnali acquisiti."""
                mean_sig_v = np.mean(sig_v) # Media del segnale V   
                mean_sig_i = np.mean(sig_i)
                std_sig_v = np.std(sig_v) # Deviazione standard del segnale V
                std_sig_i = np.std(sig_i)

                """Stampa le statistiche dei segnali acquisiti."""
                print(f'Media del segnale V: {mean_sig_v}')
                print(f'Media del segnale I: {mean_sig_i}')
                print(f'Deviazione standard del segnale V: {std_sig_v}')
                print(f'Deviazione standard del segnale I: {std_sig_i}')

                """Verifica la presenza di saturazione nei segnali acquisiti."""
                if np.max(np.abs(sig_v)) > (0.95 * A_DAQ1):
                    print('--- Saturazione V ---')
                if np.max(np.abs(sig_i)) > (0.95 * A_DAQ2):
                    print('--- Saturazione I ---')

                self.res_trig_out()

                # Time base for plotting
                t_base = np.arange(0, N/Fs, 1/Fs)

                # Percorsi per salvare i file CSV
                sig_v_i_filename = self.output_dir / f'sig_V_I_mls_{i}.csv'
                z_vector_filename = self.output_dir / f'z_vector_mls_{i}.csv'

                # Save sig_v to CSV
                df_sig_V_I = pd.DataFrame({'Time [s]': np.round(t_base, 5), 'Voltage [V]': np.round(sig_v, 6),
                                           'Current [I]': np.round(sig_i, 6)})
                df_sig_V_I.to_csv(sig_v_i_filename, index=False)

                # Remove transient and mean
                sig_v = sig_v[N//2:] - np.mean(sig_v[N//2:])
                pendenza = 9.9108
                intercetta = -0.4180
                #sig_v_rtm = sig_v / 10  # Compensate for voltage gain
                sig_v_rtm = (sig_v / pendenza) - (intercetta / pendenza)

                # sig_i = sig_i[N//2:] / (0.1 * 91)  # Compensate for shunt resistance and current gain
                pendenzaI = 88.758
                intercettaI = -0.028
                sig_i = ((sig_i[N//2:] / pendenzaI) * 10) - (intercettaI / pendenzaI)
                sig_i_rtm = sig_i - np.mean(sig_i)

                corr = np.correlate(sig_v_rtm, sig_i_rtm, mode='full')
                delay_samples = np.argmax(corr) - len(sig_v_rtm) + 1

                t_base = t_base[N//2:]

                # Update record length
                N = int(N // 2)
                f_base = np.arange(0, Fs, Fs / N)

                V = np.fft.fft(sig_v_rtm) / N
                tau = delay_samples / Fs
                I = (np.fft.fft(sig_i_rtm) / N) * np.exp(-1j * 2 * np.pi * f_base * tau)
                #I = (np.fft.fft(sig_i_rtm) / N) * np.exp(-1j * 2 * np.pi * f_base / (Fs * 2.0))

                # V = V / np.sinc(f_base.T * Ts_gen * 2) * np.sinc(f_base.T * Ts)
                # I = I / np.sinc(f_base.T * Ts_gen * 2) * np.sinc(f_base.T * Ts)

                idx_freq = np.round(N * np.array(f0_vector) / Fs).astype(int)

                Z_vector = V[idx_freq] / I[idx_freq]
                                
                # Save Z_vector to CSV
                df_z_vector = pd.DataFrame({
                    'Frequency [Hz]': np.round(f_base[idx_freq], 2),
                    'Re(Z)': np.round(np.real(Z_vector), 5),
                    'Im(Z)': np.round(np.imag(Z_vector), 5)
                })
                df_z_vector.to_csv(z_vector_filename, index=False)

            except Exception as e:
                print(f'Failed to process the acquired signal: {e}')
        else:
            print("No device connected.")
    
    def plot_multisine(self, i):
        if self.device:
            try:
                """Plot the acquired signals and computed impedance from CSV files.
                    i: index of the current measurement
                """

                # Read sig_v from CSV
                df_sig_v = pd.read_csv(self.output_dir / f'sig_V_I_multi_{i}.csv')
                t_base = df_sig_v['Time [s]']
                sig_v = df_sig_v['Voltage [V]']

                # Read sig_i from CSV
                df_sig_i = pd.read_csv(self.output_dir / f'sig_V_I_multi_{i}.csv')
                sig_i = df_sig_i['Current [I]']

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
                """ N = len(t_base)
                sig_v = sig_v[N//2:] - np.mean(sig_v[N//2:])
                sig_v = sig_v / 10  # Compensate for voltage gain verificare se deve essere compensato

                sig_i = sig_i[N//2:] / (0.1 * 91)  # Compensate for shunt resistance and current gain
                sig_i = sig_i - np.mean(sig_i)

                t_base = t_base[N//2:] """
                

                """ # Plot without mean and transient
                plt.figure()
                plt.plot(t_base, sig_v, label='Voltage')
                plt.plot(t_base, sig_i, 'r', label='Current')
                plt.title('Acquired signal without mean and transient')
                plt.xlabel('Time [s]')
                plt.ylabel('Amplitude [V]')
                plt.legend()
                plt.grid(True) """


                # Read Z_vector from CSV
                df_z_vector = pd.read_csv(self.output_dir / f'z_vector_multi_{i}.csv')
                f_base = df_z_vector['Frequency [Hz]']
                Z_real = df_z_vector['Re(Z)']
                Z_imag = df_z_vector['Im(Z)']

                Z_vector = np.array(Z_real) + 1j * np.array(Z_imag)
                Z_magnitude = np.abs(Z_vector)
                Z_phase = np.angle(Z_vector)

                
                # Plot impedance magnitude and phase
                plt.figure()
                plt.subplot(211)
                plt.semilogx(f_base, 20 * np.log10(Z_magnitude), '-b.')
                plt.xlabel('Frequency [Hz]')
                plt.ylabel('Magnitude [dB]')
                plt.grid(True)

                plt.subplot(212)
                plt.semilogx(f_base, Z_phase, '-b.')
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
            except Exception as e:
                print(f'Failed to plot the acquired signals: {e}')
        else:
            print("No device connected.")
       
    def plot_single_sine(self, f0_vector, i):
        if self.device:
            try:
                """Plot the acquired single sine signals and computed impedance from CSV files."""

                while True:
                    f0_req = input('Inserire la frequenza da visualizzare tra le seguenti:' f'{print(f0_vector)}' 
                                   ', o all per stamparle tutte:').strip().lower()
                    if f0_req == 'all':
                        for f0 in f0_vector:
                            # Read sig_v from CSV
                            df_sig_V_I = pd.read_csv(self.output_dir / f'sig_V_I_single_{i}.csv')
                            freq = df_sig_V_I['Frequency [Hz]']
                            if freq.iloc[0] == f0:
                                t_base = df_sig_V_I['Time [s]']
                                sig_v = df_sig_V_I['Voltage [V]']
                                sig_i = df_sig_V_I['Current [I]']

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
                                N = len(t_base)
                                sig_v = sig_v[N//2:] - np.mean(sig_v[N//2:])
                                sig_v = sig_v / 10  # Compensate for voltage gain verificare se deve essere compensato

                                sig_i = sig_i[N//2:] / (0.1 * 91)  # Compensate for shunt resistance and current gain
                                sig_i = sig_i - np.mean(sig_i)

                                t_base = t_base[N//2:]
                                

                                """ # Plot without mean and transient
                                plt.figure()
                                plt.plot(t_base, sig_v, label='Voltage')
                                plt.plot(t_base, sig_i, 'r', label='Current')
                                plt.title('Acquired signal without mean and transient')
                                plt.xlabel('Time [s]')
                                plt.ylabel('Amplitude [V]')
                                plt.legend()
                                plt.grid(True) """


                    # Read Z_vector from CSV
                            df_z_vector = pd.read_csv(self.output_dir / f'z_vector_single_{i}.csv')
                            f_base = df_z_vector['Frequency [Hz]']
                            Z_real = df_z_vector['Re(Z)']
                            Z_imag = df_z_vector['Im(Z)']

                            Z_vector = np.array(Z_real) + 1j * np.array(Z_imag)
                            Z_magnitude = np.abs(Z_vector)
                            Z_phase = np.angle(Z_vector)

                            
                            # Plot impedance magnitude and phase
                            plt.figure()
                            plt.subplot(211)
                            plt.semilogx(f_base, 20 * np.log10(Z_magnitude), '-b.')
                            plt.xlabel('Frequency [Hz]')
                            plt.ylabel('Magnitude [dB]')
                            plt.grid(True)

                            plt.subplot(212)
                            plt.semilogx(f_base, Z_phase, '-b.')
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
                        else:
                            df_sig_V_I = pd.read_csv(self.output_dir / f'sig_V_I_single_{i}.csv')
                            freq = df_sig_V_I['Frequency [Hz]']
                            if f0_req in freq.values:
                                t_base = df_sig_V_I['Time [s]']
                                sig_v = df_sig_V_I['Voltage [V]']
                                sig_i = df_sig_V_I['Current [I]']

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
                                N = len(t_base)
                                sig_v = sig_v[N//2:] - np.mean(sig_v[N//2:])
                                sig_v = sig_v / 10  # Compensate for voltage gain verificare se deve essere compensato

                                sig_i = sig_i[N//2:] / (0.1 * 91)  # Compensate for shunt resistance and current gain
                                sig_i = sig_i - np.mean(sig_i)

                                t_base = t_base[N//2:]
                                

                                """ # Plot without mean and transient
                                plt.figure()
                                plt.plot(t_base, sig_v, label='Voltage')
                                plt.plot(t_base, sig_i, 'r', label='Current')
                                plt.title('Acquired signal without mean and transient')
                                plt.xlabel('Time [s]')
                                plt.ylabel('Amplitude [V]')
                                plt.legend()
                                plt.grid(True) """


                                # Read Z_vector from CSV
                                df_z_vector = pd.read_csv(self.output_dir / f'z_vector_single_{i}.csv')
                                f_base = df_z_vector['Frequency [Hz]']
                                Z_real = df_z_vector['Re(Z)']
                                Z_imag = df_z_vector['Im(Z)']

                                Z_vector = np.array(Z_real) + 1j * np.array(Z_imag)
                                Z_magnitude = np.abs(Z_vector)
                                Z_phase = np.angle(Z_vector)

                                
                                # Plot impedance magnitude and phase
                                plt.figure()
                                plt.subplot(211)
                                plt.semilogx(f_base, 20 * np.log10(Z_magnitude), '-b.')
                                plt.xlabel('Frequency [Hz]')
                                plt.ylabel('Magnitude [dB]')
                                plt.grid(True)

                                plt.subplot(212)
                                plt.semilogx(f_base, Z_phase, '-b.')
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
            except Exception as e:
                print(f'Failed to plot the acquired signals: {e}')
        else:
            print("No device connected.")
    
    def plot_mls(self, i):
        if self.device:
            try:
                """Plot the acquired signals and computed impedance from CSV files."""

                # Read sig_v from CSV
                df_sig_v = pd.read_csv(self.output_dir / f'sig_V_I_mls_{i}.csv')
                t_base = df_sig_v['Time [s]']
                sig_v = df_sig_v['Voltage [V]']

                # Read sig_i from CSV
                df_sig_i = pd.read_csv(self.output_dir / f'sig_V_I_mls_{i}.csv')
                sig_i = df_sig_i['Current [I]']

                # Plot acquired signal
                plt.figure(10)
                plt.plot(t_base, sig_v, label='Voltage')
                plt.plot(t_base, sig_i, label='Current')
                plt.title('Acquired signal')
                plt.xlabel('Time [s]')
                plt.ylabel('Amplitude [V]')
                plt.legend()
                plt.grid(True)

                # Read Z_vector from CSV
                df_z_vector = pd.read_csv(self.output_dir / f'z_vector_mls_{i}.csv')
                f_base = df_z_vector['Frequency [Hz]']
                Z_real = df_z_vector['Re(Z)']
                Z_imag = df_z_vector['Im(Z)']

                Z_vector = np.array(Z_real) + 1j * np.array(Z_imag)
                Z_magnitude = np.abs(Z_vector)
                Z_phase = np.angle(Z_vector)

                
                # Plot impedance magnitude and phase
                plt.figure()
                plt.subplot(211)
                plt.semilogx(f_base, 20 * np.log10(Z_magnitude), '-b.')
                plt.xlabel('Frequency [Hz]')
                plt.ylabel('Magnitude [dB]')
                plt.grid(True)

                plt.subplot(212)
                plt.semilogx(f_base, Z_phase, '-b.')
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
            except Exception as e:
                print(f'Failed to plot the acquired signals: {e}')
        else:
            print("No device connected.")
    
    def res_trig_out(self):
        if self.device:
            try:
                self.device.write('SOUR:DIG:DATA:BIT 0, 0,(@501)')
                print('Acquisizione terminata.')
                print('Impostazione output a zero')
                self.device.write('OUTP OFF')
                self.device.write('SOUR:VOLT -0.0231, (@201)')
            except Exception as e:
                print(f'Failed to reset the trigger: {e}')
        else:
            print("No device connected.")
        
    def pot_galv_switch(self, mode):
        """Switch between potentiostat and galvanostat modes.
            mode: 'pot' for potentiostat, 'galv' for galvanostat, 'off' for off mode
        """
        if self.device:
            try:
                """Define SPI vector for state switching."""
                datap = [0, 0, 0, 0, 1, 0, 1, 1] # Potentiostat mode
                datag = [0, 0, 0, 0, 1, 0, 0, 0] # Galvanostat mode
                dataoff = [0, 0, 0, 0, 0, 0, 0, 0] # Off mode
                
                if mode == 'pot':
                    data = datap
                elif mode == 'galv':
                    data = datag
                elif mode == 'off':
                    data = dataoff
                else:
                    raise ValueError("Invalid mode. Choose 'pot', 'galv', or 'off'.")
                self.device.write('SOUR:DIG:DATA:BIT 0, 1,(@501)')
                for bit in data:
                    self.device.write(f'SOUR:DIG:DATA:BIT {bit}, 0,(@502)')
                    time.sleep(0.01)
                    self.device.write('SOUR:DIG:DATA:BIT 1, 0,(@503)')
                    time.sleep(0.01)
                    self.device.write('SOUR:DIG:DATA:BIT 0, 0,(@503)')
                    time.sleep(0.01)
                self.device.write('SOUR:DIG:DATA:BIT 1, 1,(@501)')
            except Exception as e:
                print(f'Failed to send SPI data: {e}')
        else:
            print("No device connected.")

    def gainV(self, gain_v):
        """Set the gain for voltage between 0 and 10."""
        if self.device:
            try:
                gainV_select = int(gain_v)
                Rab = 100000
                D = np.floor(int((256/Rab)*(gainV_select*10**4 - 203)))
                GainV = [int(bit) for bit in format(D, '08b')]
                self.device.write('SOUR:DIG:DATA:BIT 0, 2,(@501)')
                for bit in GainV:
                    self.device.write(f'SOUR:DIG:DATA:BIT {bit}, 0,(@502)')
                    time.sleep(0.01)
                    self.device.write('SOUR:DIG:DATA:BIT 1, 0,(@503)')
                    time.sleep(0.01)
                    self.device.write('SOUR:DIG:DATA:BIT 0, 0,(@503)')
                    time.sleep(0.01)
                self.device.write('SOUR:DIG:DATA:BIT 1, 2,(@501)')
            except Exception as e:
                print(f'Failed to set gain for voltage: {e}')
        else:
            print("No device connected.")
    
    def gainI(self, gain_i):
        if self.device:
            try:
                gainI_select = int(gain_i)
                Rab = 10000
                D = np.floor(int((256/Rab)*((19800/(gainI_select - 1)) - 150)))
                GainI = [int(bit) for bit in format(D, '08b')]
                self.device.write('SOUR:DIG:DATA:BIT 0, 3,(@501)')
                for bit in GainI:
                    self.device.write(f'SOUR:DIG:DATA:BIT {bit}, 0,(@502)')
                    time.sleep(0.01)
                    self.device.write('SOUR:DIG:DATA:BIT 1, 0,(@503)')
                    time.sleep(0.01)
                    self.device.write('SOUR:DIG:DATA:BIT 0, 0,(@503)')
                    time.sleep(0.01)
                self.device.write('SOUR:DIG:DATA:BIT 1, 3,(@501)')
            except Exception as e:
                print(f'Failed to set gain for current: {e}')
        else:
            print("No device connected.")
    
    def check_error(self):
        """Check for errors."""
        error = self.device.query('SYST:ERR?')
        print(f"Error: {error}")

    def close(self):
        """Close the connection to the device."""
        if self.device:
            try:
                self.device.close()
                self.device = None
                print("Connection closed.")
            except Exception as e:
                print(f'Failed to close the connection: {e}')