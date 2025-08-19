
import json
import os

PROFILES_FILE = "comparateur_profiles.json"

def load_profiles():
    if os.path.exists(PROFILES_FILE):
        with open(PROFILES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return {}

def save_profiles(profiles):
    with open(PROFILES_FILE, "w", encoding="utf-8") as f:
        json.dump(profiles, f, indent=4)

def get_values_for_profile(profile_name):
    profiles = load_profiles()
    return profiles.get(profile_name, {}).get("valeurs", [])

def list_profiles():
    profiles = load_profiles()
    return list(profiles.keys())

def add_or_update_profile(name, fabricant, reference, valeurs):
    profiles = load_profiles()
    profiles[name] = {
        "fabricant": fabricant,
        "reference": reference,
        "valeurs": valeurs
    }
    save_profiles(profiles)
