
import tkinter as tk
from tkinter import ttk
import interface_vb6_caracteristiques as libre
import interface_guidage_etape as guide

class InterfaceMixteApp:
    def __init__(self, root):
        self.root = root
        self.root.title("EtatComp - Interface mixte")
        self.root.geometry("1000x700")

        self.tabs = ttk.Notebook(root)
        self.tabs.pack(fill="both", expand=True)

        self.frame_libre = tk.Frame(self.tabs)
        self.frame_guide = tk.Frame(self.tabs)

        self.tabs.add(self.frame_libre, text="Session libre")
        self.tabs.add(self.frame_guide, text="Vérification guidée")

        # Intégration des deux interfaces comme sous-classes
        self.session_libre = libre.EtatCompInteractiveTabs(self.frame_libre)
        self.session_guide = guide.GuidedVerifierApp(self.frame_guide)

if __name__ == "__main__":
    root = tk.Tk()
    app = InterfaceMixteApp(root)
    root.mainloop()
