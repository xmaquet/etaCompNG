
import os
import csv
import json
from datetime import datetime

def save_series(series, session_info, base_path='data'):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    serie_id = session_info.get("serie_id", "000")
    folder_name = f"{timestamp}_serie_{serie_id}"
    folder_path = os.path.join(base_path, folder_name)
    os.makedirs(folder_path, exist_ok=True)

    # Sauvegarde du fichier mesures.csv
    csv_path = os.path.join(folder_path, "mesures.csv")
    with open(csv_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['timestamp', 'value'])
        for m in series.measures:
            writer.writerow([m.timestamp.strftime('%Y-%m-%d %H:%M:%S.%f'), m.value])

    # Sauvegarde du fichier session.json
    json_path = os.path.join(folder_path, "session.json")
    with open(json_path, 'w') as jsonfile:
        json.dump(session_info, jsonfile, indent=2)

    print(f"Série sauvegardée dans : {folder_path}")
