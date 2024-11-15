from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import serial
import time
import asyncio

# Crea l'app FastAPI
app = FastAPI()

# Configurazione seriale per Arduino
arduino = serial.Serial('/dev/ttyACM0', 115200, timeout=1)


# Funzione per leggere la distanza dal sensore
def get_distance_from_arduino():
    print("Richiesta di lettura della distanza dal sensore ultrasonico")
    arduino.write(b"5\n")
    time.sleep(0.5)
    if arduino.in_waiting > 0:
        print("Dati disponibili")
        distance = arduino.readline().decode('utf-8').strip()  # Leggi la distanza
        return distance
    print("Nessun dato disponibile")
    return None


# WebSocket endpoint per inviare i dati in tempo reale
@app.websocket("/ws/distance")
async def websocket_distance(websocket: WebSocket):
    await websocket.accept()  # Accetta la connessione WebSocket

    while True:
        try:
            # Ottieni la distanza da Arduino
            distance = get_distance_from_arduino()

            if distance:
                # Invia la distanza al client via WebSocket
                await websocket.send_text(distance)

            await asyncio.sleep(1)  # Fai una pausa per evitare sovraccarico della CPU

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
