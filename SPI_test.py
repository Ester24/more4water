import pyvisa
import time

def spi_imp(g, data):
    g.write('SOUR:DIG:DATA:BIT 0, 1,(@501)')
    for bit in data:
        g.write(f'SOUR:DIG:DATA:BIT {bit}, 0,(@502)')
        time.sleep(0.01)
        g.write('SOUR:DIG:DATA:BIT 1, 0,(@503)')
        time.sleep(0.01)
        g.write('SOUR:DIG:DATA:BIT 0, 0,(@503)')
        time.sleep(0.01)
    g.write('SOUR:DIG:DATA:BIT 1, 1,(@501)')


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

# Programmare il trigger
# Il canale di output è impostato per SPI
g.write('CONF:DIG:DIR OUTP,(@501)')
g.write('CONF:DIG:DIR OUTP,(@502)')
g.write('CONF:DIG:DIR OUTP,(@503)')

# Eseguire l'acquisizione
g.write('SYST:ERR?')  # DEBUG: verifica se ci sono errori
x = g.read()
print(x)

# Protocollo SPI
datap = [0, 0, 0, 0, 1, 0, 1, 1]
datag = [0, 0, 0, 0, 1, 0, 0, 0]
dataoff = [0, 0, 0, 0, 0, 0, 0, 0]

g.write('SOUR:DIG:DATA:BIT 1, 1,(@501)')

while True:
    user_input = input("Inserisci il comando (datag, dataoff, datap, exit): ").strip().lower()
    if user_input == 'datag':
        spi_imp(g, datag)
    elif user_input == 'dataoff':
        spi_imp(g, dataoff)
    elif user_input == 'datap':
        spi_imp(g, datap)
    elif user_input == 'exit':
        break
    else:
        print("Comando non riconosciuto. Riprova.")

""" g.write('SOUR:VOLT 8,(@201)')
time.sleep(0.1)
g.write('VOLT:STYP DIFF,(@101)')  # modalità differenziale
g.write('VOLT:POL BIP,(@101)')    # modalità bipolare
g.write('VOLT:RANG 10,(@101)')    # range ch1
g.write('COUN:FUNC TOT,(@301)')
g.write('COUN:GATE:SOUR INT,(@301)')
g.write('COUN:GATE:POL AHI,(@301)')
g.write('COUN:CLK:POL AHI,(@301)')
g.write('COUN:CLK:SOUR INT,(@301)')
g.write('COUN:CLK:INT?')
x = g.read()
print(x)

g.write('COUN:TOT:UDOW:DIR UP,(@301)')
g.write('COUN:GATE:CONT ENAB,(@301)') """

""" t = []
for k in range(10):
    g.write('COUN:TOT:IVAL 0,(@301)')
    g.write('COUN:TOT:INIT (@301)')
    g.write('MEAS? (@101)')
    x = g.read()
    time.sleep(1)
    g.write('MEAS:COUN:DATA? (@301)')
    x = g.read()
    g.write('COUN:ABOR')
    t.append(float(x) / 12000000) """
