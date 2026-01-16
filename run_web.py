"""
FAILAS: run_web.py
PASKIRTIS: Specialus paleidimo failas Streamlit aplikacijos kompiliavimui į .exe.
RYŠIAI:
  - Importuoja streamlit.web.cli
  - Nukreipia vykdymą į app.py
KONTEKSTAS:
  - Streamlit negali būti leidžiamas tiesiogiai kaip skriptas be šio "wrapperio".
"""
import sys
import os
from streamlit.web import cli as stcli

def resolve_path(path):
    """Sutvarko kelius sukompiliuotoje aplinkoje."""
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, path)

if __name__ == '__main__':
    # Nustatome app.py kelią
    # DĖMESIO: Kai kompiliuosite, turite įtraukti app.py kaip duomenų failą,
    # arba nurodyti absoliutų kelią.
    
    # Paprasčiausias būdas exe aplinkoje:
    if getattr(sys, 'frozen', False):
        # Jei exe, app.py turi būti įdėtas į vidų arba šalia
        app_path = os.path.join(sys._MEIPASS, "app.py")
    else:
        app_path = "app.py"

    # Imituojame "streamlit run app.py" komandą
    sys.argv = [
        "streamlit",
        "run",
        app_path,
        "--global.developmentMode=false"
    ]
    
    sys.exit(stcli.main())