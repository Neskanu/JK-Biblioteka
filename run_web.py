import sys
import os
from streamlit.web import cli as stcli

def resolve_path(path):
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, path)

if __name__ == "__main__":
    # Nustatome app.py kelią
    sys.argv = [
        "streamlit",
        "run",
        # Svarbu: nurodome pilną kelią iki app.py supakuotame faile
        resolve_path("app.py"),
        "--global.developmentMode=false",
    ]
    sys.exit(stcli.main())