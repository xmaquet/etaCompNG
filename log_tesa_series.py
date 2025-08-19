import json
import serial
import os
import signal
import sys
from datetime import datetime
from core import Series
from save import save_series

# Chargement de la configuration série
with open('config.json', 'r') as f:
    config = json.load(f)

PORT = config.get("port", "COM3")
BAUDRATE = config.get("baudrate", 4800)
PARITY_MAP = {'N': serial.PARITY_NONE, 'E': serial.PARITY_EVEN, 'O': serial.PARITY_ODD}
PARITY = PARITY_MAP.get(config.get("parity", "E"), serial.PARITY_EVEN)
BYTESIZE_MAP = {7: serial.SEVENBITS, 8: serial.EIGHTBITS}
BYTESIZE = BYTESIZE_MAP.get(config.get("bytesize", 7), serial.SEVENBITS)
STOPBITS = serial.STOPBITS_ONE

series = Series()

def handle_exit(sig, frame):
    print("\nArrêt demandé. Sauvegarde en cours...")
    session_info = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "heure": datetime.now().strftime("%H:%M:%S"),
        "serie_id": datetime.now().strftime("%H%M%S"),
        "operateur": "Inconnu",
        "comparateur": "TESA",
        "nb_mesures": len(series.measures),
        "valeur_cible": None,
        "tolerance": None
    }
    save_series(series, session_info)
    sys.exit(0)

signal.signal(signal.SIGINT, handle_exit)

try:
    with serial.Serial(
        port=PORT,
        baudrate=BAUDRATE,
        bytesize=BYTESIZE,
        parity=PARITY,
        stopbits=STOPBITS,
        timeout=1
    ) as ser:
        print(f"Lecture TESA démarrée sur {PORT} — appuie sur Ctrl+C pour arrêter et sauvegarder.")
        while True:
            if ser.in_waiting:
                line = ser.readline().decode('ascii', errors='ignore').strip()
                if line:
                    try:
                        value = float(line)
                        series.add(value)
                        print(f"[{len(series.measures)}] Mesure : {value}")
                    except ValueError:
                        print(f"Ignoré : '{line}' (non numérique)")
except serial.SerialException as e:
    print(f"Erreur série : {e}")
