from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import serial
import time
import asyncio

# Crea l'app FastAPI
app = FastAPI()

# Configurazione seriale per Arduino
arduino = serial.Serial('/dev/ttyACM0', 115200, timeout=1)


# Funzione per leggere i dati dalla seriale di Arduino
def get_data_from_arduino():
    if arduino.in_waiting > 0:
        return arduino.readline().decode('utf-8').strip()
    return None


# WebSocket endpoint per inviare i dati in tempo reale
@app.websocket("/ws/distance")
async def websocket_distance(websocket: WebSocket):
    await websocket.accept()  # Accetta la connessione WebSocket

    while True:
        try:
            print("In attesa di dati da Arduino...")
            # Ottieni i dati grezzi dalla porta seriale di Arduino
            data = get_data_from_arduino()

            if data:
                print(f"Ricevuto da Arduino: {data}")
                # Se il messaggio contiene "distance", estrai il valore
                if "distance:" in data:
                    # Estrai il valore della distanza
                    distance_value = data.split("distance:")[1].strip()
                    print(f"Inviando distanza: {distance_value}")
                    # Invia il valore della distanza al client via WebSocket
                    await websocket.send_text(distance_value)

            await asyncio.sleep(0.1)  # Fai una pausa per evitare sovraccarico della CPU

        except WebSocketDisconnect:
            print("Client disconnesso")
            break  # Esci dal ciclo se il client si disconnette
        except Exception as e:
            print(f"Errore nella connessione WebSocket: {e}")
            break


# Aggiungi un endpoint per il test
@app.get("/")
async def root():
    return {"message": "Hello World"}
