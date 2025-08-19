
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

class EtatCompInteractiveTabs:
    def __init__(self, root):
        self.root = root
        self.root.title("EtatComp - IHM interactive avec caractéristiques")
        self.root.geometry("1000x650")
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
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True)

        self.frame_carac = tk.Frame(notebook)
        self.frame_mesure = tk.Frame(notebook)

        notebook.add(self.frame_carac, text="Caractéristiques")
        notebook.add(self.frame_mesure, text="Série de mesures")

        # Onglet Caractéristiques
        self.entry_operateur = self._add_labeled_entry(self.frame_carac, "Opérateur", 0)
        self.entry_date = self._add_labeled_entry(self.frame_carac, "Date contrôle", 1, default=datetime.now().strftime("%Y-%m-%d"))
        self.entry_detenteur = self._add_labeled_entry(self.frame_carac, "Détenteur", 2)
        self.entry_temp = self._add_labeled_entry(self.frame_carac, "Température (°C)", 3)
        self.entry_humidite = self._add_labeled_entry(self.frame_carac, "Humidité (%)", 4)

        self.entry_num = self._add_labeled_entry(self.frame_carac, "N° Comparateur", 5)
        self.entry_ref = self._add_labeled_entry(self.frame_carac, "Référence", 6)
        self.entry_fab = self._add_labeled_entry(self.frame_carac, "Fabricant", 7)

        tk.Label(self.frame_carac, text="Observations :").grid(row=8, column=0, sticky="nw", padx=10, pady=10)
        self.text_obs = tk.Text(self.frame_carac, width=60, height=5)
        self.text_obs.grid(row=8, column=1, padx=10, pady=10)

        # Scénario série
        self.entry_nb_series = self._add_labeled_entry(self.frame_carac, "Nombre de séries", 9)
        self.entry_nb_mesures = self._add_labeled_entry(self.frame_carac, "Mesures par série", 10)

        
        # Profil comparateur
        tk.Label(self.frame_carac, text="Profil comparateur :").grid(row=11, column=0, sticky="e", padx=10, pady=4)
        import profiles
        self.combo_profil = ttk.Combobox(self.frame_carac, values=profiles.list_profiles(), state="readonly")
        self.combo_profil.grid(row=11, column=1, padx=10, pady=4)
        self.combo_profil.bind("<<ComboboxSelected>>", self.load_profile_values)

        tk.Button(self.frame_carac, text="Charger série depuis profil", command=self.insert_values_from_profile).grid(row=12, column=1, sticky="w", padx=10, pady=5)

        tk.Button(self.frame_carac, text="Enregistrer comme profil", command=self.save_current_as_profile).grid(row=12, column=1, sticky="e", padx=10, pady=5)


        # Onglet Mesure
        self.entry_tol_min = self._add_labeled_entry(self.frame_mesure, "Tolérance min", 0)
        self.entry_tol_max = self._add_labeled_entry(self.frame_mesure, "Tolérance max", 1)
        self.entry_cible = self._add_labeled_entry(self.frame_mesure, "Valeur cible", 2)

        tk.Label(self.frame_mesure, text="Mesure actuelle :", font=("Arial", 12)).grid(row=3, column=0, padx=10, pady=10)
        self.label_val = tk.Label(self.frame_mesure, text="---", font=("Arial", 14), bg="white", width=12, relief="sunken")
        self.label_val.grid(row=3, column=1, padx=10)

        # Tableau
        columns = ("#", "Valeur", "Ecart", "Conforme")
        self.tree = ttk.Treeview(self.frame_mesure, columns=columns, show="headings", height=12)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        self.tree.grid(row=4, column=0, columnspan=3, padx=10, pady=10)

        # Statistiques
        self.lbl_moyenne = self._add_labeled_label(self.frame_mesure, "Moyenne", 5)
        self.lbl_ecarttype = self._add_labeled_label(self.frame_mesure, "Écart type", 6)

        # Boutons
        btn_frame = tk.Frame(self.frame_mesure)
        btn_frame.grid(row=7, column=0, columnspan=3, pady=10)
        tk.Button(btn_frame, text="Démarrer série", command=self.start_series, width=15).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Arrêter série", command=self.stop_series, width=15).pack(side="left", padx=5)
        tk.Button(btn_frame, text="📂 Ouvrir séries", command=self.open_data_folder, width=15).pack(side="left", padx=5)

    def _add_labeled_entry(self, parent, label, row, default=""):
        tk.Label(parent, text=label + " :").grid(row=row, column=0, sticky="e", padx=10, pady=4)
        entry = tk.Entry(parent, width=30)
        entry.grid(row=row, column=1, padx=10, pady=4)
        entry.insert(0, default)
        return entry

    def _add_labeled_label(self, parent, label, row):
        tk.Label(parent, text=label + " :").grid(row=row, column=0, sticky="e", padx=10, pady=4)
        val = tk.Label(parent, text="---", bg="white", width=10, relief="sunken")
        val.grid(row=row, column=1, padx=10, pady=4)
        return val

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
            "date": self.entry_date.get(),
            "heure": datetime.now().strftime("%H:%M:%S"),
            "serie_id": datetime.now().strftime("%H%M%S"),
            "operateur": self.entry_operateur.get(),
            "detenteur": self.entry_detenteur.get(),
            "temperature": self.entry_temp.get(),
            "humidite": self.entry_humidite.get(),
            "comparateur_num": self.entry_num.get(),
            "comparateur_ref": self.entry_ref.get(),
            "comparateur_fab": self.entry_fab.get(),
            "observations": self.text_obs.get("1.0", "end").strip(),
            "nb_series": self.entry_nb_series.get(),
            "nb_mesures_par_serie": self.entry_nb_mesures.get(),
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
            return True

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



    def load_profile_values(self, event=None):
        import profiles
        profil = self.combo_profil.get()
        values = profiles.get_values_for_profile(profil)
        self.entry_fab.delete(0, tk.END)
        self.entry_ref.delete(0, tk.END)
        data = profiles.load_profiles().get(profil, {})
        self.entry_fab.insert(0, data.get("fabricant", ""))
        self.entry_ref.insert(0, data.get("reference", ""))

    def insert_values_from_profile(self):
        import profiles
        profil = self.combo_profil.get()
        values = profiles.get_values_for_profile(profil)
        for idx, val in enumerate(values, 1):
            self.series.add(val)
            ecart = self.compute_ecart(val)
            conforme = self.verifie_conformite(val)
            self.tree.insert("", "end", values=(idx, f"{val:.3f}", f"{ecart:+.3f}", "✅" if conforme else "❌"))
        self.update_stats()




    def save_current_as_profile(self):
        import profiles
        nom = self.combo_profil.get().strip()
        if not nom:
            messagebox.showwarning("Profil", "Veuillez saisir un nom de profil.")
            return
        try:
            valeurs = [m.value for m in self.series.measures]
            if not valeurs:
                messagebox.showwarning("Profil", "Aucune mesure disponible pour créer un profil.")
                return
            fabricant = self.entry_fab.get().strip()
            reference = self.entry_ref.get().strip()
            profiles.add_or_update_profile(nom, fabricant, reference, valeurs)
            self.combo_profil["values"] = profiles.list_profiles()
            messagebox.showinfo("Profil", f"Profil '{nom}' enregistré.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'enregistrer le profil : {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = EtatCompInteractiveTabs(root)
    root.mainloop()
