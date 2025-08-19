
import tkinter as tk
from tkinter import ttk, messagebox
import serial
import threading
import json
import os
import subprocess
from datetime import datetime
from core import Series
from save import save_series

class EtatCompGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("EtatComp - Prototype")
        self.series = Series()
        self.running = False

        self.load_config()
        self.create_widgets()

        self.ser = None
        self.thread = None

    def load_config(self):
        with open('config.json', 'r') as f:
            config = json.load(f)
        self.port = config.get("port", "COM3")
        self.baudrate = config.get("baudrate", 4800)
        self.parity = {'N': serial.PARITY_NONE, 'E': serial.PARITY_EVEN, 'O': serial.PARITY_ODD}.get(config.get("parity", "E"))
        self.bytesize = {7: serial.SEVENBITS, 8: serial.EIGHTBITS}.get(config.get("bytesize", 7))
        self.stopbits = serial.STOPBITS_ONE

    def create_widgets(self):
        self.label_val = tk.Label(self.root, text="Dernière mesure : ---", font=("Helvetica", 16))
        self.label_val.pack(pady=10)

        self.tree = ttk.Treeview(self.root, columns=("Valeur", "Horodatage"), show="headings", height=10)
        self.tree.heading("Valeur", text="Valeur")
        self.tree.heading("Horodatage", text="Horodatage")
        self.tree.pack(padx=10, pady=10)

        frame_btns = tk.Frame(self.root)
        frame_btns.pack(pady=10)

        self.btn_start = tk.Button(frame_btns, text="Démarrer série", command=self.start_series)
        self.btn_start.pack(side="left", padx=5)

        self.btn_stop = tk.Button(frame_btns, text="Arrêter / Enregistrer", command=self.stop_series, state="disabled")
        self.btn_stop.pack(side="left", padx=5)

        self.btn_open_data = tk.Button(frame_btns, text="📂 Ouvrir séries", command=self.open_data_folder)
        self.btn_open_data.pack(side="left", padx=5)

    def start_series(self):
        try:
            self.ser = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                bytesize=self.bytesize,
                parity=self.parity,
                stopbits=self.stopbits,
                timeout=1
            )
            self.running = True
            self.btn_start.config(state="disabled")
            self.btn_stop.config(state="normal")
            self.series = Series()
            self.thread = threading.Thread(target=self.read_serial)
            self.thread.start()
        except serial.SerialException as e:
            messagebox.showerror("Erreur série", str(e))

    def stop_series(self):
        self.running = False
        if self.ser:
            self.ser.close()
        self.btn_start.config(state="normal")
        self.btn_stop.config(state="disabled")

        session_info = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "heure": datetime.now().strftime("%H:%M:%S"),
            "serie_id": datetime.now().strftime("%H%M%S"),
            "operateur": "Inconnu",
            "comparateur": "TESA",
            "nb_mesures": len(self.series.measures)
        }
        save_series(self.series, session_info)

    def read_serial(self):
        while self.running:
            if self.ser.in_waiting:
                line = self.ser.readline().decode('ascii', errors='ignore').strip()
                if line:
                    try:
                        value = float(line)
                        self.series.add(value)
                        ts = self.series.measures[-1].timestamp.strftime("%H:%M:%S.%f")
                        self.tree.insert("", "end", values=(value, ts))
                        self.label_val.config(text=f"Dernière mesure : {value}")
                    except ValueError:
                        pass

    def open_data_folder(self):
        folder_path = os.path.abspath("data")
        if os.name == "nt":
            os.startfile(folder_path)
        elif os.name == "posix":
            subprocess.Popen(["xdg-open", folder_path])
        else:
            messagebox.showinfo("Ouvrir dossier", f"Ouvrez manuellement : {folder_path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = EtatCompGUI(root)
    root.mainloop()
