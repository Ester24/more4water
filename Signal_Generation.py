import numpy as np
from scipy.signal import max_len_seq

class SignalGenerator:
    def __init__(self):
        """
        Inizializza il generatore di segnali con i parametri forniti.
        """
        self.f0_vector = np.array([0.05, 0.1, 0.2, 0.4, 1, 2, 4, 10, 20, 40,
                      100, 200, 400, 1000])
        self.Fs = 1e4
        self.Ts = 1 / self.Fs  # Periodo di campionamento
        self.A_gen = 0.005 #Valore massimo = 1
        self.T_gen = int(40)  # Durata totale del segnale
        self.N = int(self.Fs * self.T_gen)  # Numero totale di campioni
        self.Fs_gen = 2e4  # Frequenza di campionamento del segnale generato
        self.Ts_gen = 1 / self.Fs_gen  # Periodo di campionamento
        self.N_gen = int(np.ceil(self.T_gen/self.Ts_gen))  # Numero di campioni del segnale generato
        self.t_gen = np.arange(0, self.N_gen/self.Fs_gen, 1/self.Fs_gen)  
        self.signal_gen = np.zeros_like(self.t_gen)  # Segnale generato
        self.signal_vector = None  # Vettore dei segnali generati

    def generate_multisine(self, sig, DynamicEISOffset):
        """
        Genera un segnale multiseno sommando sinusoidi alle frequenze specificate in f0_vector.
        """
        if sig == 'multiseno':
            for f0 in self.f0_vector:
                self.signal_gen += self.A_gen * np.sin(2* np.pi * f0 * self.t_gen +
                                    2 * np.pi * np.random.rand())
            # Aggiungi un offset dinamico al segnale
            self.signal_gen += DynamicEISOffset
            # self.signal_vector = np.floor(self.signal_gen * 2**15) + 2**15 #U2351A
            self.signal_vector = np.floor(self.signal_gen * 2**11) + 2**11 #U2331A
        return self.signal_gen, self.signal_vector

    def generate_single_sine(self, frequency, sig):
        """
        Genera un segnale sinusoidale singolo alla frequenza specificata.

        :param frequency: Frequenza del segnale sinusoidale in Hz.
        :param Fs: Frequenza di campionamento in Hz (se None, utilizza self.Fs).
        :param duration: Durata del segnale in secondi (se None, utilizza self.duration).
        """
        if sig == 'seno singolo':
            # Aggiorna i parametri solo per il segnale sinusoidale singolo
            NSamples_per_period = 100  # Numero di campioni per periodo
            self.Fs = NSamples_per_period * frequency  # Frequenza di campionamento in Hz
            self.Fs_gen = int(100 * frequency)
            self.N_periods = 4 # Numero di periodi della sinusoide da acquisire
            self.N = int(NSamples_per_period * self.N_periods)  # Numero totale di campioni
            self.T_gen = self.N_periods / frequency
            self.Ts_gen = 1/ self.Fs_gen
            self.N_gen = int(np.ceil(self.T_gen / self.Ts_gen))
            self.t_gen = np.arange(0, self.N_gen / self.Fs_gen, 1 / self.Fs_gen)
            
            self.signal_gen = self.A_gen *np.sin(2 * np.pi * frequency * self.t_gen)
            # self.signal_vector = np.floor(self.signal_gen * 2**15) + 2**15 #U2351A
            self.signal_vector = np.floor(self.signal_gen * 2**11) + 2**11 #U2331A
        return self.signal_gen, self.signal_vector, self.N_periods

    def generate_mls(self, order, sig):
        if sig == 'mls':
            """
            Genera una sequenza MLS (Maximum Length Sequence) di un dato ordine.

            :param order: Ordine della sequenza MLS, .
            """
            "Genearation parameter"
            self.Fs = 0.2e4  # Frequenza di campionamento in Hz
            self.Ts = 1 / self.Fs  # Periodo di campionamento
            self.Fs_gen = 0.2e4  # Frequenza di campionamento del segnale generato
            self.Ts_gen = 1 / self.Fs_gen # Periodo di campionamento del segnale generato
            
            mls_seq = max_len_seq(order)[0]
            # Ripeti la sequenza per coprire l'intera durata desiderata
            num_repeats = 10  # Numero di ripetizioni della sequenza MLS
            self.T_gen = len(mls_seq) * num_repeats * self.Ts_gen  # Durata totale del segnale
            self.N_gen = int(self.T_gen / self.Ts_gen)  # Numero di campioni del segnale generato
            self.N = int(self.T_gen * self.Fs)  # Numero totale di campioni
            
            """Generazione dell'f0_vector"""
            f = np.arange(0, self.Fs, self.Fs / self.N)
            fids = np.arange(num_repeats, self.N_gen, num_repeats)
            self.f0_vector = f[fids]

            self.t_gen = np.arange(0, self.N_gen / self.Fs_gen, 1 / self.Fs_gen)  # Vettore temporale
            self.signal_gen = np.zeros_like(self.t_gen)  # Segnale generato
            mls_signal = np.tile(mls_seq, num_repeats)  # Ripeti la sequenza MLS
            # Converti i valori da {0, 1} a {-1, 1}
            self.signal_gen = 2 * mls_signal - 1
            self.signal_gen = self.A_gen * self.signal_gen  # Scala il segnale
            # Rappresenta il segnale in livelli a 16 bit
            # self.signal_vector = np.floor(self.signal_gen * 2**15) + 2**15 #U2351A
            self.signal_vector = np.floor(self.signal_gen * 2**11) + 2**11 #U2331A
        return self.signal_gen, self.signal_vector

    @property
    def parameters(self):
        """
        Restituisce i parametri del segnale generato.

        :return: Dizionario contenente i parametri del segnale.
        """
        return {
            'Fs': self.Fs,
            'N': self.N,
            'Ts': self.Ts,
            'f0_vector': self.f0_vector,
            'N_periods': self.N_periods,
            't_gen': self.t_gen,
            'T_gen': self.T_gen,
            'Fs_gen': self.Fs_gen,
            'Ts_gen': self.Ts_gen,
            'N_gen': self.N_gen,
            'signal_gen': self.signal_gen,
            'signal_vector': self.signal_vector
        }


