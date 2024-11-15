import serial
import time

from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}


# Configura la connessione seriale con Arduino (modifica la porta a seconda della tua configurazione)
arduino = serial.Serial('/dev/ttyAMA0', 115200, timeout=1)


def send_to_arduino(value):
    """Invia un valore ad Arduino"""
    arduino.write(f"{value}\n".encode())  # Invia il valore come stringa, con newline
    time.sleep(0.1)  # Breve pausa per dare tempo ad Arduino di rispondere


def read_from_arduino():
    """Leggi la risposta da Arduino"""
    if arduino.in_waiting > 0:
        line = arduino.readline().decode('utf-8').strip()  # Leggi e decodifica la risposta
        return line
    return None


def main():
    print("Inizio comunicazione con Arduino...")

    for i in range(10):  # Ciclo per inviare valori da 0 a 9
        print(f"Inviando valore {i} a Arduino...")
        send_to_arduino(i)  # Invia il valore a Arduino
        response = read_from_arduino()  # Leggi la risposta di Arduino

        if response:
            print(f"Risposta da Arduino: {response}")
        else:
            print("Nessuna risposta ricevuta.")

        time.sleep(1)  # Attendi 1 secondo prima di inviare il prossimo valore


if __name__ == "__main__":
    main()
