from __future__ import annotations

import argparse
import re
import sys
from importlib import resources
from importlib.metadata import version, PackageNotFoundError

from . import data  # <-- precisa de src/gerador_api_segura_v3/data/__init__.py

def _run_embedded_script(extra_globals: dict | None = None) -> int:
    script_path = resources.files(data).joinpath("gerador_api_segura_v3.py")
    code = script_path.read_text(encoding="utf-8-sig")
    # Correções defensivas de aspas escapadas (se seu arquivo veio com \"\"\" etc.)
    code = code.replace('\\"""', '"""')
    code = re.sub(r'\\+(?=""")', "", code)
    g = {"__name__": "__main__"}
    if extra_globals:
        g.update(extra_globals)
    exec(compile(code, str(script_path), "exec"), g)
    return 0

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="gerador-api-segura",
        description="Gera um projeto API Flask Seguro (JWT, RBAC, Rate Limiting, CORS, Talisman, Swagger protegido, logs, Prometheus e Docker).",
    )
    parser.add_argument("--version", action="store_true", help="Mostra a versão e sai")
    parser.add_argument("--dest", default=".", help="Diretório de saída do projeto")
    parser.add_argument("--db", choices=["mongo", "mariadb", "postgres"], default="postgres",
                        help="Banco padrão do template")
    # Adicione outras flags que seu script principal entenda; elas irão em CLI_OPTS.
    args = parser.parse_args(argv)

    if args.version:
        try:
            print(version("gerador-api-segura-v3"))
        except PackageNotFoundError:
            print("0.0.0")
        return 0

    # Passe as opções para o script embutido, se ele quiser consumi-las.
    return _run_embedded_script({"CLI_OPTS": vars(args)})

if __name__ == "__main__":
    sys.exit(main())
