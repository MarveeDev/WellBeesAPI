from fastapi import FastAPI, HTTPException
import serial
import time

# Crea l'app FastAPI
app = FastAPI()


arduino = serial.Serial('/dev/ttyAMA0', 115200, timeout=1)


# Funzione per leggere la distanza dal sensore
def get_distance_from_arduino():
    print("Richiesta di lettura della distanza dal sensore ultrasonico 2")
    arduino.write(b"get_distance\n")
    if arduino.in_waiting > 0:
        print("Dati disponibili")
        distance = arduino.readline().decode('utf-8').strip()  # Leggi la distanza
        return distance
    print("Nessun dato disponibile")
    return None


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


@app.get("/ultrasonic/{id}/distance")
async def get_ultrasonic_distance(id: int):
    print("Richiesta di lettura della distanza dal sensore ultrasonico")
    """Funzione per ottenere la distanza dal sensore ultrasonico collegato ad Arduino."""
    distance = get_distance_from_arduino()

    print(f"Distanza letta: {distance}")
    if distance is None:
        print("Errore nella lettura della distanza")
        raise HTTPException(status_code=500, detail="Errore nella lettura della distanza da Arduino")

    return {"distance": distance}
