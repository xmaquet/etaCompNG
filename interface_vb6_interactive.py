
import tkinter as tk
from tkinter import ttk, messagebox
import serial
import threading
import json
import os
import subprocess
from datetime import datetime
from statistics import mean, stdev
from core import Series
from save import save_series

class EtatCompInteractive:
    def __init__(self, root):
        self.root = root
        self.root.title("EtatComp - IHM interactive")
        self.root.geometry("900x600")
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
        # Entrées tolérances et cible
        tk.Label(self.root, text="Tolérance min :").place(x=20, y=20)
        self.entry_tol_min = tk.Entry(self.root, width=10)
        self.entry_tol_min.place(x=120, y=20)

        tk.Label(self.root, text="Tolérance max :").place(x=220, y=20)
        self.entry_tol_max = tk.Entry(self.root, width=10)
        self.entry_tol_max.place(x=320, y=20)

        tk.Label(self.root, text="Valeur cible :").place(x=420, y=20)
        self.entry_cible = tk.Entry(self.root, width=10)
        self.entry_cible.place(x=510, y=20)

        # Mesure actuelle
        tk.Label(self.root, text="Mesure actuelle :", font=("Arial", 12)).place(x=20, y=60)
        self.label_val = tk.Label(self.root, text="---", font=("Arial", 16), bg="white", width=10, relief="sunken")
        self.label_val.place(x=160, y=55)

        # Tableau des mesures
        columns = ("#", "Valeur", "Ecart", "Conforme")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings", height=15)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)
        self.tree.place(x=20, y=100)

        # Statistiques
        tk.Label(self.root, text="Moyenne :").place(x=20, y=430)
        self.lbl_moyenne = tk.Label(self.root, text="---", bg="white", width=10, relief="sunken")
        self.lbl_moyenne.place(x=100, y=430)

        tk.Label(self.root, text="Écart type :").place(x=220, y=430)
        self.lbl_ecarttype = tk.Label(self.root, text="---", bg="white", width=10, relief="sunken")
        self.lbl_ecarttype.place(x=300, y=430)

        
        # Informations de session
        tk.Label(self.root, text="Opérateur :").place(x=20, y=500)
        self.entry_operateur = tk.Entry(self.root, width=20)
        self.entry_operateur.place(x=100, y=500)

        tk.Label(self.root, text="Comparateur :").place(x=300, y=500)
        self.entry_comparateur = tk.Entry(self.root, width=20)
        self.entry_comparateur.place(x=400, y=500)

        # Boutons
        y_btn = 470
        tk.Button(self.root, text="Démarrer série", command=self.start_series, width=15).place(x=20, y=y_btn)
        tk.Button(self.root, text="Arrêter série", command=self.stop_series, width=15).place(x=170, y=y_btn)
        tk.Button(self.root, text="📂 Ouvrir séries", command=self.open_data_folder, width=15).place(x=320, y=y_btn)

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
            self.series = Series()
            self.thread = threading.Thread(target=self.read_serial)
            self.thread.start()
        except serial.SerialException as e:
            messagebox.showerror("Erreur série", str(e))

    def stop_series(self):
        self.running = False
        if self.ser:
            self.ser.close()

        session_info = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "heure": datetime.now().strftime("%H:%M:%S"),
            "serie_id": datetime.now().strftime("%H%M%S"),
            "operateur": self.entry_operateur.get() or "Inconnu",
            "comparateur": self.entry_comparateur.get() or "TESA",
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
                        self.label_val.config(text=f"{value:.3f}")
                        idx = len(self.series.measures)
                        ecart = self.compute_ecart(value)
                        conforme = self.verifie_conformite(value)
                        self.tree.insert("", "end", values=(idx, f"{value:.3f}", f"{ecart:+.3f}", "✅" if conforme else "❌"))
                        self.update_stats()
                    except ValueError:
                        pass

    def compute_ecart(self, value):
        try:
            ref = float(self.entry_cible.get())
            return value - ref
        except ValueError:
            return 0.0

    def verifie_conformite(self, value):
        try:
            tmin = float(self.entry_tol_min.get())
            tmax = float(self.entry_tol_max.get())
            return tmin <= value <= tmax
        except ValueError:
            return True  # pas de test si mal défini

    def update_stats(self):
        values = [m.value for m in self.series.measures]
        if values:
            self.lbl_moyenne.config(text=f"{mean(values):.3f}")
            if len(values) > 1:
                self.lbl_ecarttype.config(text=f"{stdev(values):.3f}")
            else:
                self.lbl_ecarttype.config(text="—")

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
    app = EtatCompInteractive(root)
    root.mainloop()
