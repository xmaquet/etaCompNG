
import tkinter as tk
from tkinter import ttk, messagebox
import serial
import threading
import json
import os
import profiles
from statistics import mean, stdev
from datetime import datetime
from save import save_series

class GuidedVerifierApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Vérification guidée du comparateur")
        self.root.geometry("800x500")

        self.current_step = 0
        self.current_values = []
        self.running = False

        self.load_config()
        self.create_widgets()

    def load_config(self):
        with open("config.json", "r") as f:
            conf = json.load(f)
        self.port = conf.get("port", "COM3")
        self.baudrate = conf.get("baudrate", 4800)
        self.parity = {'N': serial.PARITY_NONE, 'E': serial.PARITY_EVEN, 'O': serial.PARITY_ODD}.get(conf.get("parity", "E"))
        self.bytesize = {7: serial.SEVENBITS, 8: serial.EIGHTBITS}.get(conf.get("bytesize", 7))
        self.stopbits = serial.STOPBITS_ONE

    def create_widgets(self):
        frame = tk.Frame(self.root)
        frame.pack(padx=20, pady=20, fill="both", expand=True)

        tk.Label(frame, text="Profil de comparateur :").grid(row=0, column=0, sticky="e")
        self.combo_profil = ttk.Combobox(frame, values=profiles.list_profiles(), state="readonly")
        self.combo_profil.grid(row=0, column=1)
        tk.Button(frame, text="Charger", command=self.load_profile).grid(row=0, column=2, padx=5)

        self.lbl_cible = tk.Label(frame, text="Cible : --- mm", font=("Arial", 16))
        self.lbl_cible.grid(row=1, column=0, columnspan=3, pady=20)

        self.btn_mesurer = tk.Button(frame, text="Mesurer", command=self.acquire_measurement, state="disabled", width=20)
        self.btn_mesurer.grid(row=2, column=0, columnspan=3)

        self.tree = ttk.Treeview(frame, columns=("Cible", "Moyenne", "Écart", "Écart type", "Conforme"), show="headings", height=8)
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        self.tree.grid(row=3, column=0, columnspan=3, pady=10)

        self.btn_export = tk.Button(frame, text="Exporter", command=self.export_results, state="disabled")
        self.btn_export.grid(row=4, column=2, sticky="e", pady=10)

    def load_profile(self):
        self.nom_profil = self.combo_profil.get()
        if not self.nom_profil:
            messagebox.showwarning("Profil", "Veuillez sélectionner un profil.")
            return

        data = profiles.load_profiles().get(self.nom_profil)
        self.valeurs_cibles = data.get("valeurs", [])
        self.tol_min = data.get("tol_min", -0.01)
        self.tol_max = data.get("tol_max", 0.01)
        self.nb_mesures = data.get("nb_mesures_par_point", 3)
        self.resultats = []
        self.current_step = 0

        if not self.valeurs_cibles:
            messagebox.showerror("Profil", "Aucune valeur dans ce profil.")
            return

        self.btn_mesurer["state"] = "normal"
        self.next_cible()

    def next_cible(self):
        if self.current_step < len(self.valeurs_cibles):
            self.lbl_cible.config(text=f"Cible : {self.valeurs_cibles[self.current_step]:.3f} mm")
            self.current_values = []
        else:
            self.lbl_cible.config(text="Mesures terminées")
            self.btn_mesurer["state"] = "disabled"
            self.btn_export["state"] = "normal"

    def acquire_measurement(self):
        try:
            ser = serial.Serial(self.port, self.baudrate, bytesize=self.bytesize, parity=self.parity, stopbits=self.stopbits, timeout=1)
        except serial.SerialException as e:
            messagebox.showerror("Port série", str(e))
            return

        self.current_values = []
        for _ in range(self.nb_mesures):
            line = ser.readline().decode("ascii", errors="ignore").strip()
            try:
                val = float(line)
                self.current_values.append(val)
            except ValueError:
                continue
        ser.close()

        if not self.current_values:
            messagebox.showerror("Mesure", "Aucune donnée reçue.")
            return

        moyenne = mean(self.current_values)
        cible = self.valeurs_cibles[self.current_step]
        ecart = moyenne - cible
        ecart_type = stdev(self.current_values) if len(self.current_values) > 1 else 0.0
        conforme = self.tol_min <= ecart <= self.tol_max

        self.tree.insert("", "end", values=(
            f"{cible:.3f}", f"{moyenne:.3f}", f"{ecart:+.3f}", f"{ecart_type:.3f}", "✅" if conforme else "❌"
        ))

        self.resultats.append({
            "cible": cible,
            "mesures": self.current_values,
            "moyenne": moyenne,
            "ecart": ecart,
            "ecart_type": ecart_type,
            "conforme": conforme
        })

        self.current_step += 1
        self.next_cible()

    def export_results(self):
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        os.makedirs("data", exist_ok=True)
        path = os.path.join("data", f"resultats_{self.nom_profil}_{now}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.resultats, f, indent=4)
        messagebox.showinfo("Export", f"Résultats exportés : {path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = GuidedVerifierApp(root)
    root.mainloop()
