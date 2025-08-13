from importlib.resources import files
from . import data
import re

def main():
    script_path = files(data).joinpath("gerador_api_segura_v3.py")
    # Lê tolerando BOM (remove U+FEFF se existir):
    code = script_path.read_text(encoding="utf-8")

    # Normalizações de segurança para builds antigos:
    code = code.replace('\\"""', '"""')      # corrige aspas triplas escapadas
    code = re.sub(r'\\+(?=""")', "", code)   # remove barras extras antes de """

    exec(compile(code, str(script_path), "exec"), {"__name__": "__main__"})
