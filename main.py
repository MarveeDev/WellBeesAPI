from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import serial
import time
import asyncio
from openai import OpenAI
import requests


# Crea l'app FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
AIClient = OpenAI(api_key="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")

# Configura le origini consentite
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Consenti tutte le origini (modifica per produzione)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurazione seriale per Arduino
arduino = serial.Serial('/dev/ttyACM0', 115200, timeout=1)


# Funzione per leggere i dati dalla seriale di Arduino
def get_data_from_arduino():
    if arduino.in_waiting > 0:
        return arduino.readline().decode('utf-8').strip()
    return None


# WebSocket endpoint per inviare i dati in tempo reale
@app.websocket("/ws/getData")
async def websocket_data(websocket: WebSocket):
    await websocket.accept()  # Accetta la connessione WebSocket

    while True:
        try:
            print("In attesa di dati da Arduino...")
            data = get_data_from_arduino()

            if data:
                print(f"Ricevuto da Arduino: {data}")

                if "distance:" in data:
                    distance_value = data.split("distance:")[1].strip()
                    print(f"Inviando distanza: {distance_value}")
                    await websocket.send_text(distance_value)

                if "in_temperature:" in data:
                    in_temperature_value = data.split("in_temperature:")[1].strip()
                    print(f"Inviando temperatura interna: {in_temperature_value}")
                    ai_response = askAI(f"temperatura interna: {in_temperature_value}")
                    if ai_response:
                        print(f"Risposta AI: {ai_response}")
                    else:
                        print("Risposta AI non valida o vuota.")
                    await websocket.send_text(in_temperature_value)

                # Gestisci gli altri dati come sopra

            await asyncio.sleep(0.1)

        except WebSocketDisconnect:
            print("Client disconnesso")
            break
        except Exception as e:
            print(f"Errore nella connessione WebSocket: {e}")
            break


import json




import json
import requests

def askAI(question):
    print("Chiedo ad AI:", question)
    headers = {
        "Content-Type": "application/json",
        "Authorization": "B312eYtyX9p5PP6i05clgVYFE6aVVmHJHicTYR4DdCWjFTbQiVS9sTT3BlbkFJyf36CL8ADXjNEvJyhz8edNsXHYTJ7WdDSDpp7XKwZy4Iz6Htq3h7HsnLotu-9CN_mdIFVGGooA"
    }

    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content": """mi devi aiutare a simulare un sistema regolato da AI:
                Il contesto è una casa domotica, basata sul benessere all'interno della casa.
                Le feature sono:
                - Regolazione della luce in base alla presenza o meno di persone in stanza (per esempio: se una persona è abituata ad andare in cucina alle 19, alle 19 tu accendi lievemente la luce. se dopo 5 minuti non è ancora arrivata la spegni finchè non entra) (sensore di movimento e luci regolabili)
                - Regolazione qualità dell'aria (con ventole se si è in casa, tirando giu le taparelle lasciando le righe e aprendo le finestre se sei fuori casa) (si passano valori tipo umidità dell'aria ecc)
                - Termosifoni (regola in base alla temperatura interna ed esterna le valvole dei caloriferi)

                NOTA BENE, dovrai rispondere solamente con {"Componente": "Azione"}
                Esempio: se io ti do {"temperatura": "30"}
                tu dovrai rispondere
                {{
                    "finestraStanza": "20" (20 è il grado di apertura)
                    "termosifoneStanza": "0" (spegni il termosifone)
                }}

                quando poi ti manderò la temperatura e sarà scesa a 21 (hai osservato che è la temperatura media scelta dall'utente)
                {{
                    "finestraCamera": "0"
                }}.

                Eccoti il mio input: """ + question
            }
        ]
    }

    print("Payload:", payload)

    try:
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        result = response.json()
        print("Risposta AI:", result)
        if "choices" in result and result["choices"]:
            output = result["choices"][0]["message"]["content"].strip().lower()
            print("Output:", output)
            return output
        else:
            print("Formato risposta non valido:", result)
            return "Errore nel parsing AI"
    except json.JSONDecodeError as e:
        print("Errore decodifica JSON:", e)
        return "Errore JSON"
# Aggiungi un endpoint per il test

app.get("/window/{value}")
async def set_window(value: int):
    print(f"Invio comando per impostare la finestra a: {value}")
    arduino.write(f"window:{value}\n".encode())
    return {"message": f"Comando inviato per impostare la finestra a: {value}"}

@app.get("/")
async def root():
    return {"message": "Hello"}