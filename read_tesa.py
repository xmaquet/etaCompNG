import json
import serial

# Charger la configuration depuis config.json
with open('config.json', 'r') as f:
    config = json.load(f)

# Extraire les paramètres
PORT = config.get("port", "COM3")
BAUDRATE = config.get("baudrate", 4800)
PARITY_MAP = {'N': serial.PARITY_NONE, 'E': serial.PARITY_EVEN, 'O': serial.PARITY_ODD}
PARITY = PARITY_MAP.get(config.get("parity", "E"), serial.PARITY_EVEN)
BYTESIZE_MAP = {7: serial.SEVENBITS, 8: serial.EIGHTBITS}
BYTESIZE = BYTESIZE_MAP.get(config.get("bytesize", 7), serial.SEVENBITS)
STOPBITS = serial.STOPBITS_ONE

try:
    with serial.Serial(
        port=PORT,
        baudrate=BAUDRATE,
        bytesize=BYTESIZE,
        parity=PARITY,
        stopbits=STOPBITS,
        timeout=1
    ) as ser:
        print(f"Connecté à {PORT} ({BAUDRATE} bauds) — Lecture en cours... (Ctrl+C pour arrêter)")
        while True:
            if ser.in_waiting:
                line = ser.readline().decode('ascii', errors='ignore').strip()
                if line:
                    print(f"Mesure reçue : {line}")
except serial.SerialException as e:
    print(f"Erreur série : {e}")