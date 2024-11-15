from fastapi import FastAPI
import serial
import time
import threading

# Crea l'istanza dell'app FastAPI
app = FastAPI()

# Configura la connessione seriale con Arduino (modifica con la tua porta)
arduino = serial.Serial('/dev/ttyAMA0', 115200, timeout=1)

# Funzione per inviare valori ad Arduino
def send_values_to_arduino():
    """Funzione per inviare un ciclo di valori ad Arduino"""
    for i in range(10):  # Loop che invia valori da 0 a 9
        print(f"Inviando valore {i} a Arduino...")
        arduino.write(f"{i}\n".encode())  # Invia il valore come stringa, seguito da una nuova linea
        time.sleep(1)  # Attende 1 secondo prima di inviare il prossimo valore

    print("Invio valori completato!")

# Endpoint per iniziare l'invio di valori a Arduino
@app.get("/start-sending-to-arduino")
async def start_sending():
    """Endpoint che avvia l'invio dei valori ad Arduino"""
    # Avvia un thread separato per inviare i valori ad Arduino in parallelo
    threading.Thread(target=send_values_to_arduino).start()
    return {"message": "Inizio invio dei valori ad Arduino!"}

# Funzione per leggere la risposta da Arduino (se necessario)
def read_from_arduino():
    """Leggi la risposta di Arduino sulla seriale"""
    if arduino.in_waiting > 0:
        line = arduino.readline().decode('utf-8').strip()
        return line
    return None
