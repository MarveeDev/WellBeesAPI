from fastapi import FastAPI, HTTPException
import serial
import time

# Crea l'app FastAPI
app = FastAPI()


arduino = serial.Serial('/dev/ttyAMA0', 11520, timeout=1)


# Funzione per leggere la distanza dal sensore
def get_distance_from_arduino():
    arduino.write(b"get_distance\n")
    time.sleep(0.5)
    if arduino.in_waiting > 0:
        distance = arduino.readline().decode('utf-8').strip()  # Leggi la distanza
        return distance
    return None


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


@app.get("/ultrasonic/{id}/distance")
async def get_ultrasonic_distance(id: int):
    """Funzione per ottenere la distanza dal sensore ultrasonico collegato ad Arduino."""
    distance = get_distance_from_arduino()

    if distance is None:
        raise HTTPException(status_code=500, detail="Errore nella lettura della distanza da Arduino")

    return {"distance": distance}
