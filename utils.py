from datetime import datetime

def date_du_jour():
    """
    Retourne la date du jour au format jj-mm-aaaa.
    """
    return datetime.now().strftime("%d-%m-%Y")
