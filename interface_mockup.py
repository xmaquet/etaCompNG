
import tkinter as tk
from tkinter import ttk

class EtatCompVB6Mockup:
    def __init__(self, root):
        self.root = root
        self.root.title("EtatComp - Maquette VB6")
        self.root.geometry("800x600")

        self.create_mockup_ui()

    def create_mockup_ui(self):
        # Section mesure actuelle
        tk.Label(self.root, text="Mesure actuelle :", font=("Arial", 12)).place(x=20, y=20)
        tk.Label(self.root, text="---", font=("Arial", 16), bg="white", width=10, relief="sunken").place(x=150, y=15)

        # Zone de tolérance
        tk.Label(self.root, text="Tolérance min :", font=("Arial", 10)).place(x=20, y=60)
        tk.Entry(self.root, width=10).place(x=120, y=60)
        tk.Label(self.root, text="Tolérance max :", font=("Arial", 10)).place(x=220, y=60)
        tk.Entry(self.root, width=10).place(x=320, y=60)

        # Référence / cible
        tk.Label(self.root, text="Valeur cible :", font=("Arial", 10)).place(x=20, y=90)
        tk.Entry(self.root, width=10).place(x=120, y=90)

        # Tableau des mesures
        columns = ("#", "Valeur", "Ecart", "Hystérésis", "Conformité")
        tree = ttk.Treeview(self.root, columns=columns, show="headings", height=10)
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        tree.place(x=20, y=130)

        # Boutons de commande
        y_btn = 360
        tk.Button(self.root, text="Démarrer série", width=15).place(x=20, y=y_btn)
        tk.Button(self.root, text="Arrêter série", width=15).place(x=160, y=y_btn)
        tk.Button(self.root, text="Charger réf.", width=15).place(x=300, y=y_btn)
        tk.Button(self.root, text="Exporter CSV", width=15).place(x=440, y=y_btn)
        tk.Button(self.root, text="Exporter PDF", width=15).place(x=580, y=y_btn)

        # Statistiques
        tk.Label(self.root, text="Moyenne :", font=("Arial", 10)).place(x=20, y=410)
        tk.Label(self.root, text="Écart type :", font=("Arial", 10)).place(x=20, y=435)
        tk.Label(self.root, text="Min :", font=("Arial", 10)).place(x=220, y=410)
        tk.Label(self.root, text="Max :", font=("Arial", 10)).place(x=220, y=435)

        # Simuler les zones de texte statiques
        for x, y in [(100, 410), (100, 435), (280, 410), (280, 435)]:
            tk.Label(self.root, text="---", bg="white", width=10, relief="sunken").place(x=x, y=y)

if __name__ == "__main__":
    root = tk.Tk()
    app = EtatCompVB6Mockup(root)
    root.mainloop()
