import serial
import time

# Configura la porta seriale di Arduino
arduino = serial.Serial('/dev/ttyACM0', 115200, timeout=1)

# Funzione per leggere i dati dalla seriale
def get_data_from_arduino():
    if arduino.in_waiting > 0:
        return arduino.readline().decode('utf-8').strip()
    return None

while True:
    data = get_data_from_arduino()
    if data:
        print("Dati ricevuti:", data)
    time.sleep(1)  # Pausa di 1 secondo
