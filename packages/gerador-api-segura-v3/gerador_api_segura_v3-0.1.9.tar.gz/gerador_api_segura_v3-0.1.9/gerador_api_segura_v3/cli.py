from __future__ import annotations
import argparse, re, sys
from importlib import resources
from importlib.metadata import version, PackageNotFoundError
from . import data  # precisa de data/__init__.py

def _run_embedded_script(extra_globals: dict | None = None) -> int:
    script_path = resources.files(data).joinpath("gerador_api_segura_v3.py")
    code = script_path.read_text(encoding="utf-8-sig")
    code = code.replace('\\"""', '"""')        # dessanitiza aspas
    code = re.sub(r'\\+(?=""")', "", code)     # remove barras antes de """
    g = {"__name__": "__main__", "__file__": str(script_path)}
    if extra_globals:
        g.update(extra_globals)
    try:
        exec(compile(code, str(script_path), "exec"), g)
        return 0
    except SystemExit as e:
        return int(e.code) if isinstance(e.code, int) else 1
    except Exception as e:
        print(f"[CLI] Erro ao executar script embutido: {e}", file=sys.stderr)
        return 1

def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    p = argparse.ArgumentParser(
        prog="gerador-api-segura",
        description=("Gera um projeto Flask seguro (JWT, RBAC, Rate Limiting, CORS, "
                     "Talisman, Swagger protegido, logs, Prometheus e Docker)."),
    )
    p.add_argument("--version", action="store_true", help="Mostra a versão e sai")
    p.add_argument("--dest", default=".", help="Diretório de saída do projeto")
    p.add_argument("--db", choices=["mongo", "mariadb", "postgres"], default="postgres",
                   help="Banco padrão do template")
    args = p.parse_args(argv)

    if args.version:
        try:
            print(version("gerador-api-segura-v3"))
        except PackageNotFoundError:
            print("0.0.0")
        return 0

    # Disponibiliza as flags para o script gerador (se ele quiser consumi-las).
    return _run_embedded_script({"CLI_OPTS": vars(args)})

if __name__ == "__main__":
    sys.exit(main())
