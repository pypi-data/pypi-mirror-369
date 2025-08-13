from importlib.resources import files
from . import data

def main():
    script_path = files(data).joinpath("gerador_api_segura_v3.py")
    code = script_path.read_text(encoding="utf-8-sig")  # tolera BOM
    exec(compile(code, str(script_path), "exec"), {"__name__": "__main__"})

