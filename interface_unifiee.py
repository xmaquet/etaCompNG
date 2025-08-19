
import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import profiles
import serial
from datetime import datetime
from statistics import mean, stdev

class EtatCompProfiléApp:
    def __init__(self, root):
        self.root = root
        self.root.title("EtatComp - Vérification profilée")
        self.root.geometry("950x600")

        self.setup_ui()
        self.load_profiles()

    def setup_ui(self):
        self.tabs = ttk.Notebook(self.root)
        self.tabs.pack(fill="both", expand=True)

        self.frame_info = tk.Frame(self.tabs)
        self.frame_mesure = tk.Frame(self.tabs)

        self.tabs.add(self.frame_info, text="1. Caractéristiques & Profil")
        self.tabs.add(self.frame_mesure, text="2. Déroulement de la série")

        self.build_info_tab()
        self.build_mesure_tab()

    def build_info_tab(self):
        f = self.frame_info

        # Champs opérateur / session
        self.entry_operateur = self._add_labeled_entry(f, "Opérateur", 0)
        self.entry_date = self._add_labeled_entry(f, "Date contrôle", 1, default=datetime.now().strftime("%Y-%m-%d"))
        self.entry_detenteur = self._add_labeled_entry(f, "Détenteur", 2)
        self.entry_temp = self._add_labeled_entry(f, "Température (°C)", 3)
        self.entry_humidite = self._add_labeled_entry(f, "Humidité (%)", 4)

        # Profil
        tk.Label(f, text="Profil comparateur :").grid(row=5, column=0, sticky="e", padx=10, pady=4)
        self.combo_profil = ttk.Combobox(f, state="readonly", width=30)
        self.combo_profil.grid(row=5, column=1, padx=10, pady=4)
        self.combo_profil.bind("<<ComboboxSelected>>", self.load_selected_profile)

        self.entry_valeurs = self._add_labeled_entry(f, "Valeurs cibles (mm, séparées par ,)", 6)
        self.entry_fab = self._add_labeled_entry(f, "Fabricant", 7)
        self.entry_ref = self._add_labeled_entry(f, "Référence", 8)

        tk.Button(f, text="💾 Enregistrer ce profil", command=self.save_profile).grid(row=9, column=1, sticky="w", padx=10, pady=5)

    def build_mesure_tab(self):
        f = self.frame_mesure
        self.lbl_cible = tk.Label(f, text="Cible : --- mm", font=("Arial", 16))
        self.lbl_cible.pack(pady=20)

        self.btn_mesurer = tk.Button(f, text="Mesurer", command=self.acquire_measurement, state="disabled", width=25)
        self.btn_mesurer.pack()

        self.tree = ttk.Treeview(f, columns=("Cible", "Moyenne", "Écart", "Écart type", "Conforme"), show="headings", height=10)
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        self.tree.pack(pady=10)

        self.btn_start = tk.Button(f, text="Commencer la série", command=self.start_series)
        self.btn_start.pack(pady=10)

    def _add_labeled_entry(self, parent, label, row, default=""):
        tk.Label(parent, text=label + " :").grid(row=row, column=0, sticky="e", padx=10, pady=4)
        entry = tk.Entry(parent, width=40)
        entry.grid(row=row, column=1, padx=10, pady=4)
        entry.insert(0, default)
        return entry

    def load_profiles(self):
        self.profiles = profiles.load_profiles()
        self.combo_profil["values"] = list(self.profiles.keys())

    def load_selected_profile(self, event=None):
        nom = self.combo_profil.get()
        p = self.profiles.get(nom, {})
        self.entry_fab.delete(0, tk.END)
        self.entry_ref.delete(0, tk.END)
        self.entry_valeurs.delete(0, tk.END)

        self.entry_fab.insert(0, p.get("fabricant", ""))
        self.entry_ref.insert(0, p.get("reference", ""))
        vals = p.get("valeurs", [])
        self.entry_valeurs.insert(0, ", ".join(str(v) for v in vals))

    def save_profile(self):
        nom = self.combo_profil.get().strip()
        if not nom:
            messagebox.showwarning("Profil", "Veuillez indiquer un nom dans la liste déroulante.")
            return
        try:
            valeurs = [float(v.strip()) for v in self.entry_valeurs.get().split(",") if v.strip()]
            fabricant = self.entry_fab.get()
            reference = self.entry_ref.get()
            profiles.add_or_update_profile(nom, fabricant, reference, valeurs)
            self.load_profiles()
            messagebox.showinfo("Profil", f"Profil '{nom}' enregistré.")
        except ValueError:
            messagebox.showerror("Erreur", "Format de valeurs incorrect.")

    def start_series(self):
        nom = self.combo_profil.get()
        if not nom or nom not in self.profiles:
            messagebox.showwarning("Profil", "Veuillez choisir un profil valide.")
            return

        self.resultats = []
        self.current_step = 0
        self.valeurs_cibles = self.profiles[nom]["valeurs"]
        self.tol_min = -0.01
        self.tol_max = 0.01
        self.nb_mesures = 3
        self.next_cible()
        self.btn_mesurer["state"] = "normal"

    def next_cible(self):
        if self.current_step < len(self.valeurs_cibles):
            cible = self.valeurs_cibles[self.current_step]
            self.lbl_cible.config(text=f"Cible : {cible:.3f} mm")
        else:
            self.lbl_cible.config(text="Série terminée")
            self.btn_mesurer["state"] = "disabled"

    def acquire_measurement(self):
        try:
            with open("config.json", "r") as f:
                conf = json.load(f)
            ser = serial.Serial(
                conf.get("port", "COM3"),
                conf.get("baudrate", 4800),
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=1
            )
        except serial.SerialException as e:
            messagebox.showerror("Série", str(e))
            return

        mesures = []
        for _ in range(self.nb_mesures):
            try:
                val = float(ser.readline().decode("ascii").strip())
                mesures.append(val)
            except:
                continue
        ser.close()

        if not mesures:
            messagebox.showerror("Erreur", "Pas de données reçues.")
            return

        cible = self.valeurs_cibles[self.current_step]
        moyenne = mean(mesures)
        ecart = moyenne - cible
        ecart_type = stdev(mesures) if len(mesures) > 1 else 0.0
        conforme = self.tol_min <= ecart <= self.tol_max

        self.tree.insert("", "end", values=(f"{cible:.3f}", f"{moyenne:.3f}", f"{ecart:+.3f}", f"{ecart_type:.3f}", "✅" if conforme else "❌"))
        self.resultats.append({"cible": cible, "moyenne": moyenne, "ecart": ecart, "ecart_type": ecart_type, "conforme": conforme})
        self.current_step += 1
        self.next_cible()

if __name__ == "__main__":
    root = tk.Tk()
    app = EtatCompProfiléApp(root)
    root.mainloop()
