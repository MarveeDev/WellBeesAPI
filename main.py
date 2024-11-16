from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import serial
import time
import asyncio
from openai import OpenAI


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

                # Se il messaggio contiene "in_temperature", estrai il valore
                if "in_temperature:" in data:
                    # Estrai il valore della temperatura

                    in_temperature_value = data.split("in_temperature:")[1].strip()
                    print("sto chiamando l'AI")
                    print(askAI("temperatura interna: "+ in_temperature_value))
                    print(f"Inviando temperatura interna: {in_temperature_value}")
                    # Invia il valore della temperatura al client via WebSocket
                    await websocket.send_text(in_temperature_value)

                # Se il messaggio contiene "out_temperature", estrai il valore
                if "out_temperature:" in data:
                    # Estrai il valore della temperatura
                    out_temperature_value = data.split("out_temperature:")[1].strip()
                    print(f"Inviando temperatura esterna: {out_temperature_value}")
                    # Invia il valore della temperatura al client via WebSocket
                    await websocket.send_text(out_temperature_value)

                # Se il messaggio contiene "in_humidity", estrai il valore
                if "in_humidity:" in data:
                    # Estrai il valore dell'umidità
                    humidity_value = data.split("in_humidity:")[1].strip()
                    print(f"Inviando umidità interna: {humidity_value}")
                    # Invia il valore dell'umidità al client via WebSocket
                    await websocket.send_text(humidity_value)

                # Se il messaggio contiene "out_humidity", estrai il valore
                if "out_humidity:" in data:
                    # Estrai il valore dell'umidità
                    humidity_value = data.split("out_humidity:")[1].strip()
                    print(f"Inviando umidità esterna: {humidity_value}")
                    # Invia il valore dell'umidità al client via WebSocket
                    await websocket.send_text(humidity_value)

                # Se il messaggio contiene "light", estrai il valore
                if "light:" in data:
                    # Estrai il valore della luminosità
                    light_value = data.split("light:")[1].strip()
                    print(f"Inviando luminosità: {light_value}")
                    # Invia il valore della luminosità al client via WebSocket
                    await websocket.send_text(light_value)

                # Se il messaggio contiene "

            await asyncio.sleep(0.1)  # Fai una pausa per evitare sovraccarico della CPU

        except WebSocketDisconnect:
            print("Client disconnesso")
            break  # Esci dal ciclo se il client si disconnette
        except Exception as e:
            print(f"Errore nella connessione WebSocket: {e}")
            break

def askAI(question):
    # key = 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
    completion = AIClient.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": """mi devi aiutare a simulare un sistema regolato da AI:
            Il contesto è una casa domotica, basata sul benessere all'interno della casa.
            Le feature sono:
            - Regolazione della luce in base alla presenza o meno di persone in stanza (per esempio: se una persona è abituata ad andare in cucina alle 19, alle 19 tu accendi lievemente la luce. se dopo 5 minuti non è ancora arrivata la spegni finchè non entra) (sensore di movimento e luci regolabili)
            - Regolazione qualità dell'aria (con ventole se si è in casa, tirando giu le taparelle lasciando le righe e aprendo le finestre se sei fuori casa) (si passano valori tipo umidità dell'aria ecc)
            - Termosifoni (regola in base alla temperatura interna ed esterna le valvole dei caloriferi)
            
            NOTA BENE, dovrai rispondere solamente con {"Componente": "Azione"}
            Esempio: se io ti do {"temperatura": "30"}
            tu dovrai rispondere
            {
                 "finestraStanza": "20" (20 è il grado di apertura)
                 "termosifoneStanza": "0" (spegni il termosifone)
            }
            
            quando poi ti manderò la temperatura e sarà scesa a 21 (hai osservato che è la temperatura media scelta dall'utente)
            {
                 "finestraCamera": "0"
            }.
            
            Eccoti il mio input: """ + question}
        ]
    )
    return completion.choices[0].message.content


# Aggiungi un endpoint per il test
@app.get("/")
async def root():
    return {"message": "Hello"}