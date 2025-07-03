import pyvisa
import time

def spi_gainV(g, data):
    g.write('SOUR:DIG:DATA:BIT 0, 2,(@501)')
    for bit in data:
        g.write(f'SOUR:DIG:DATA:BIT {bit}, 0,(@502)')
        time.sleep(0.01)
        g.write('SOUR:DIG:DATA:BIT 1, 0,(@503)')
        time.sleep(0.01)
        g.write('SOUR:DIG:DATA:BIT 0, 0,(@503)')
        time.sleep(0.01)
    g.write('SOUR:DIG:DATA:BIT 1, 2,(@501)')

def spi_gainI(g, data):
    g.write('SOUR:DIG:DATA:BIT 0, 3,(@501)')
    for bit in data:
        g.write(f'SOUR:DIG:DATA:BIT {bit}, 0,(@502)')
        time.sleep(0.01)
        g.write('SOUR:DIG:DATA:BIT 1, 0,(@503)')
        time.sleep(0.01)
        g.write('SOUR:DIG:DATA:BIT 0, 0,(@503)')
        time.sleep(0.01)
    g.write('SOUR:DIG:DATA:BIT 1, 3,(@501)')

print('Attempting to create handle object for communication with DAQ')
rm = pyvisa.ResourceManager()
#g = rm.open_resource('USB0::0x0957::0x0F18::TW54410533::0::INSTR')  # U2351A
g = rm.open_resource('USB0::0x0957::0x1518::TW52200019::0::INSTR')  # U2331A
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

# Il canale di output è impostato per SPI
g.write('CONF:DIG:DIR OUTP,(@501)')
g.write('CONF:DIG:DIR OUTP,(@502)')
g.write('CONF:DIG:DIR OUTP,(@503)')
g.write('SOUR:DIG:DATA:BIT 1, 2,(@501)')
time.sleep(1)
g.write('SOUR:DIG:DATA:BIT 1, 3,(@501)')

GainV = []
GainI = []
while True:
    user_input = input("Inserisci il comando (gainv, gaini, exit): ").strip().lower()
    if user_input == 'gainv':
        gainV_select = int(input("Inserisci il valore di gain per la tensione tra 0 e 255 : "))
        GainV = [int(bit) for bit in format(gainV_select, '08b')]
        spi_gainV(g, GainV)
    elif user_input == 'gaini':
        gainI_select = int(input("Inserisci il valore di gain per la corrente tra 0 e 255 : "))
        GainI = [int(bit) for bit in format(gainI_select, '08b')]
        spi_gainI(g, GainI)
    elif user_input == 'exit':
        break
    else:
        print("Comando non riconosciuto. Riprova.")




