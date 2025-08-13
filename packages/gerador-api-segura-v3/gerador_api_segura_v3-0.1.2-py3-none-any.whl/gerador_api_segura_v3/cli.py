from importlib.resources import files
from . import data
import re

def main():
    script_path = files(data).joinpath("gerador_api_segura_v3.py")
    code = script_path.read_text(encoding="utf-8-sig")  # tolera BOM
    code = code.replace('\\"""', '"""')                 # corrige aspas escapadas
    code = re.sub(r'\\+(?=""")', "", code)              # remove barras extras antes de """
    exec(compile(code, str(script_path), "exec"), {"__name__": "__main__"})