import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import json
import os

DATA_FILE = "comparateur_profiles.json"

class EtatCompApp:
    def __init__(self, root):
        root.title("EtatComp - Contrôle des comparateurs")
        root.geometry("1000x700")
        self.style = ttk.Style()
        self.style.theme_use('clam')

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True)

        self.comparateurs = self.load_comparateurs()
        self.comparateur_index_map = {}

        self.session_tab = ttk.Frame(self.notebook)
        self.mesures_tab = ttk.Frame(self.notebook)
        self.biblio_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.session_tab, text="Session")
        self.notebook.add(self.mesures_tab, text="Mesures")
        self.notebook.add(self.biblio_tab, text="Bibliothèque de comparateurs")

        self.build_session_tab()
        self.build_mesures_tab()
        self.build_biblio_tab()

    def load_comparateurs(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        return {}

    def save_comparateurs(self):
        with open(DATA_FILE, "w") as f:
            json.dump(self.comparateurs, f, indent=2)

    def refresh_biblio(self):
        self.biblio_listbox.delete(0, tk.END)
        self.comparateur_index_map.clear()
        for nom, data in self.comparateurs.items():
            ligne = self.format_comparateur_ligne(nom, data)
            self.biblio_listbox.insert(tk.END, ligne)
            self.comparateur_index_map[ligne] = nom

    def format_comparateur_ligne(self, nom, data):
        return f"{nom} | N° {data.get('numero', '')} | {data.get('reference', '')} | {data.get('fabricant', '')}"

    def show_comparateur_editor(self, nom_initial=None):
        editor = tk.Toplevel()
        editor.title("Éditer un comparateur")
        editor.geometry("400x250")
        editor.grab_set()

        nom_var = tk.StringVar(value=nom_initial or "")
        num_var = tk.StringVar(value=self.comparateurs.get(nom_initial, {}).get("numero", ""))
        ref_var = tk.StringVar(value=self.comparateurs.get(nom_initial, {}).get("reference", ""))
        fab_var = tk.StringVar(value=self.comparateurs.get(nom_initial, {}).get("fabricant", ""))

        ttk.Label(editor, text="Nom du comparateur").pack(pady=5)
        nom_entry = ttk.Entry(editor, textvariable=nom_var)
        nom_entry.pack(fill='x', padx=20)

        ttk.Label(editor, text="N° d'équipement").pack(pady=5)
        num_entry = ttk.Entry(editor, textvariable=num_var)
        num_entry.pack(fill='x', padx=20)

        ttk.Label(editor, text="Référence").pack(pady=5)
        ref_entry = ttk.Entry(editor, textvariable=ref_var)
        ref_entry.pack(fill='x', padx=20)

        ttk.Label(editor, text="Fabricant / Marque").pack(pady=5)
        fab_entry = ttk.Entry(editor, textvariable=fab_var)
        fab_entry.pack(fill='x', padx=20)

        def valider():
            nom = nom_var.get().strip()
            if not nom:
                messagebox.showerror("Erreur", "Le nom du comparateur est requis.")
                return
            self.comparateurs[nom] = {
                "numero": num_var.get().strip(),
                "reference": ref_var.get().strip(),
                "fabricant": fab_var.get().strip(),
                "valeurs": self.comparateurs.get(nom, {}).get("valeurs", ""),
                "nb_series": self.comparateurs.get(nom, {}).get("nb_series", "1"),
                "nb_mesures": self.comparateurs.get(nom, {}).get("nb_mesures", "1")
            }
            if nom_initial and nom != nom_initial:
                del self.comparateurs[nom_initial]
            self.save_comparateurs()
            self.refresh_biblio()
            editor.destroy()

        ttk.Button(editor, text="Valider", command=valider).pack(pady=10)

    def creer_comparateur(self):
        self.show_comparateur_editor()

    def modifier_comparateur(self):
        selection = self.biblio_listbox.curselection()
        if selection:
            ligne = self.biblio_listbox.get(selection[0])
            nom = self.comparateur_index_map.get(ligne)
            if nom:
                self.show_comparateur_editor(nom)

    def supprimer_comparateur(self):
        selection = self.biblio_listbox.curselection()
        if selection:
            ligne = self.biblio_listbox.get(selection[0])
            nom = self.comparateur_index_map.get(ligne)
            if nom and messagebox.askyesno("Supprimer", f"Supprimer le comparateur '{nom}' ?"):
                del self.comparateurs[nom]
                self.save_comparateurs()
                self.refresh_biblio()

    def build_biblio_tab(self):
        frm = self.biblio_tab
        self.biblio_listbox = tk.Listbox(frm, font=("Consolas", 10))
        self.biblio_listbox.pack(fill="both", expand=True, padx=10, pady=10)
        self.refresh_biblio()
        btns = ttk.Frame(frm)
        btns.pack(pady=5)
        ttk.Button(btns, text="Créer", command=self.creer_comparateur).pack(side="left", padx=5)
        ttk.Button(btns, text="Modifier", command=self.modifier_comparateur).pack(side="left", padx=5)
        ttk.Button(btns, text="Supprimer", command=self.supprimer_comparateur).pack(side="left", padx=5)

    def build_session_tab(self):
        frm = self.session_tab
        frm.columnconfigure(0, weight=1)

        zone1 = ttk.LabelFrame(frm, text="Conditions de contrôle")
        zone1.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        zone1.columnconfigure(1, weight=1)

        ttk.Label(zone1, text="Opérateur").grid(row=0, column=0, sticky="w")
        self.ent_operateur = ttk.Entry(zone1)
        self.ent_operateur.grid(row=0, column=1, sticky="ew")

        ttk.Label(zone1, text="Date du contrôle").grid(row=1, column=0, sticky="w")
        self.ent_date = DateEntry(zone1, date_pattern='dd-mm-yyyy')
        self.ent_date.grid(row=1, column=1, sticky="ew")

        ttk.Label(zone1, text="Détenteur").grid(row=2, column=0, sticky="w")
        self.ent_detenteur = ttk.Entry(zone1)
        self.ent_detenteur.grid(row=2, column=1, sticky="ew")

        ttk.Label(zone1, text="Température (°C)").grid(row=3, column=0, sticky="w")
        self.ent_temp = ttk.Entry(zone1)
        self.ent_temp.grid(row=3, column=1, sticky="ew")

        ttk.Label(zone1, text="Humidité (%)").grid(row=4, column=0, sticky="w")
        self.ent_humidite = ttk.Entry(zone1)
        self.ent_humidite.grid(row=4, column=1, sticky="ew")

        zone2 = ttk.LabelFrame(frm, text="Comparateur")
        zone2.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        zone2.columnconfigure(1, weight=1)

        ttk.Label(zone2, text="Sélectionner").grid(row=0, column=0, sticky="w")
        values = []
        for nom, data in self.comparateurs.items():
            ligne = self.format_comparateur_ligne(nom, data)
            values.append(ligne)
            self.comparateur_index_map[ligne] = nom
        self.combo_comparateur = ttk.Combobox(zone2, values=values, width=80)
        self.combo_comparateur.grid(row=0, column=1, sticky="ew")
        self.combo_comparateur.bind("<<ComboboxSelected>>", self.on_comparateur_selected)

        ttk.Label(zone2, text="N° d'équipement").grid(row=1, column=0, sticky="w")
        self.lbl_numero = ttk.Label(zone2, text="")
        self.lbl_numero.grid(row=1, column=1, sticky="w")

        ttk.Label(zone2, text="Référence").grid(row=2, column=0, sticky="w")
        self.lbl_reference = ttk.Label(zone2, text="")
        self.lbl_reference.grid(row=2, column=1, sticky="w")

        ttk.Label(zone2, text="Fabricant / Marque").grid(row=3, column=0, sticky="w")
        self.lbl_fabricant = ttk.Label(zone2, text="")
        self.lbl_fabricant.grid(row=3, column=1, sticky="w")

        zone3 = ttk.LabelFrame(frm, text="Observations")
        zone3.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        self.txt_observations = tk.Text(zone3, height=4)
        self.txt_observations.pack(fill="both", expand=True)

        zone4 = ttk.LabelFrame(frm, text="Déroulement de la session")
        zone4.grid(row=3, column=0, padx=10, pady=10, sticky="ew")
        ttk.Label(zone4, text="Nombre de séries").grid(row=0, column=0, sticky="w")
        self.spin_nb_series = tk.Spinbox(zone4, from_=1, to=20, width=5)
        self.spin_nb_series.grid(row=0, column=1, sticky="w")
        ttk.Label(zone4, text="Mesures par série").grid(row=1, column=0, sticky="w")
        self.spin_nb_mesures = tk.Spinbox(zone4, from_=1, to=50, width=5)
        self.spin_nb_mesures.grid(row=1, column=1, sticky="w")
        ttk.Label(zone4, text="Valeurs cibles (mm, séparées par des virgules)").grid(row=2, column=0, columnspan=2, sticky="w")
        self.ent_valeurs_cibles = ttk.Entry(zone4, width=50)
        self.ent_valeurs_cibles.grid(row=3, column=0, columnspan=2, sticky="ew")
        self.btn_enregistrer_deroulement = ttk.Button(zone4, text="Enregistrer le déroulement pour ce comparateur", command=self.save_deroulement)
        self.btn_enregistrer_deroulement.grid(row=4, column=0, columnspan=2, pady=5)

    def save_deroulement(self):
        ligne = self.combo_comparateur.get()
        nom = self.comparateur_index_map.get(ligne)
        if not nom:
            messagebox.showwarning("Erreur", "Aucun comparateur sélectionné")
            return
        try:
            valeurs = list(map(float, self.ent_valeurs_cibles.get().split(",")))
            if valeurs != sorted(valeurs):
                messagebox.showwarning("Erreur", "Les valeurs cibles doivent être triées par ordre croissant, ex : 0.1, 0.2, 0.3")
                return
            nb_mesures = int(self.spin_nb_mesures.get())
            if len(valeurs) != nb_mesures:
                messagebox.showwarning("Erreur", "Le nombre de valeurs cibles doit être égal au nombre de mesures par série.")
                return
        except Exception:
            messagebox.showerror("Erreur", "Format incorrect : valeurs séparées par des virgules, ex : 0.1, 0.2, 0.3")
            return

        self.comparateurs[nom]["valeurs"] = self.ent_valeurs_cibles.get()
        self.comparateurs[nom]["nb_series"] = self.spin_nb_series.get()
        self.comparateurs[nom]["nb_mesures"] = self.spin_nb_mesures.get()
        self.save_comparateurs()
        self.refresh_biblio()
        messagebox.showinfo("Succès", f"Déroulement enregistré pour '{nom}'")

    def build_mesures_tab(self):
        label = ttk.Label(self.mesures_tab, text="Interface de relevé des mesures en cours de développement")
        label.pack(padx=10, pady=10)

    def on_comparateur_selected(self, event):
        ligne = self.combo_comparateur.get()
        nom = self.comparateur_index_map.get(ligne)
        infos = self.comparateurs.get(nom, {})
        self.lbl_numero.config(text=infos.get("numero", "—"))
        self.lbl_reference.config(text=infos.get("reference", "—"))
        self.lbl_fabricant.config(text=infos.get("fabricant", "—"))
        self.ent_valeurs_cibles.delete(0, tk.END)
        self.ent_valeurs_cibles.insert(0, infos.get("valeurs", ""))
        self.spin_nb_series.delete(0, tk.END)
        self.spin_nb_series.insert(0, infos.get("nb_series", "1"))
        self.spin_nb_mesures.delete(0, tk.END)
        self.spin_nb_mesures.insert(0, infos.get("nb_mesures", "1"))

def save_deroulement(self):
    ligne = self.combo_comparateur.get()
    nom = self.comparateur_index_map.get(ligne)
    if not nom:
        messagebox.showwarning("Erreur", "Aucun comparateur sélectionné")
        return
    try:
        valeurs = list(map(float, self.ent_valeurs_cibles.get().split(",")))
        if valeurs != sorted(valeurs):
            messagebox.showwarning("Erreur", "Les valeurs cibles doivent être triées par ordre croissant, ex : 0.1, 0.2, 0.3")
            return
        nb_mesures = int(self.spin_nb_mesures.get())
        if len(valeurs) != nb_mesures:
            messagebox.showwarning("Erreur", "Le nombre de valeurs cibles doit être égal au nombre de mesures par série.")
            return
    except Exception:
        messagebox.showerror("Erreur", "Format incorrect : valeurs séparées par des virgules, ex : 0.1, 0.2, 0.3")
        return

    self.comparateurs[nom]["valeurs"] = self.ent_valeurs_cibles.get()
    self.comparateurs[nom]["nb_series"] = self.spin_nb_series.get()
    self.comparateurs[nom]["nb_mesures"] = self.spin_nb_mesures.get()
    self.save_comparateurs()
    self.refresh_biblio()
    messagebox.showinfo("Succès", f"Déroulement enregistré pour '{nom}'")

def open_biblio_tab(self):
        self.notebook.select(self.biblio_tab)

if __name__ == "__main__":
    root = tk.Tk()
    app = EtatCompApp(root)
    root.mainloop()
