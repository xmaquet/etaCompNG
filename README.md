# etaCompNG

> **etaCompNG** est un projet Python développé avec PyCharm, visant à fournir un environnement de simulation et d’outillage autour des comparateurs et dispositifs de mesure.  
> Ce dépôt centralise le code pour faciliter la maintenance et l’évolution depuis n’importe quel poste de travail.

---

## 🚀 Installation

Clone le dépôt en local :

```bash
git clone https://github.com/xmaquet/etaCompNG.git
cd etaCompNG
```

Crée et active un environnement virtuel :

```bash
python -m venv .venv
# Sous Windows PowerShell
.venv\Scripts\activate
# Sous Linux/macOS
source .venv/bin/activate
```

Installe les dépendances (si `requirements.txt` existe) :

```bash
pip install -r requirements.txt
```

---

## 🛠️ Utilisation

Lance le script principal :

```bash
python main.py
```

*(à adapter selon le point d’entrée réel du projet)*

---

## 📂 Structure du projet

- `main.py` – point d’entrée principal  
- `src/` – code source organisé par modules (si applicable)  
- `tests/` – scripts de tests unitaires (si applicables)  
- `.gitignore` – configuration des fichiers exclus du dépôt  
- `requirements.txt` – dépendances Python (à générer via `pip freeze`)  

---

## 🤝 Contribution

1. Fork le projet  
2. Crée une branche : `git checkout -b feature/ma-nouvelle-fonction`  
3. Commit : `git commit -m "Ajout de ma nouvelle fonction"`  
4. Push : `git push origin feature/ma-nouvelle-fonction`  
5. Ouvre une Pull Request  

---

## 📜 Licence

Projet interne – à compléter selon la licence choisie (MIT, GPL, privée, etc.).
