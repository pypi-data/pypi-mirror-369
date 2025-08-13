# gerador-api-segura-v3

CLI para gerar uma **API Flask Segura** (Mongo/MariaDB/PostgreSQL) com JWT, RBAC, Rate Limiting, CORS, Talisman, Swagger protegido, logs, Prometheus e Docker.

> Este pacote empacota seu script `gerador_api_segura_v3.py` e o executa como um comando de terminal.

## Instalação local em modo desenvolvimento

```bash
# dentro da pasta do projeto
python -m pip install -U build
python -m pip install -U hatchling
python -m pip install -e .
```

Execute o gerador:
```bash
gerador-api-segura
```

<!-- ## Publicação no TestPyPI e PyPI

1) **Criar conta e token** (uma vez)
- Crie contas no https://test.pypi.org e https://pypi.org
- Em *Account settings* → *API tokens*, crie um token e **salve** o valor.

2) **Instalar ferramentas**
```bash
python -m pip install -U build twine
```

3) **Gerar artefatos**
```bash
python -m build
# vai criar dist/*.whl e dist/*.tar.gz
```

4) **Subir no TestPyPI (recomendado primeiro)**
```bash
# use o token, formato de usuário: __token__
twine upload --repository testpypi dist/*
# digite o token quando pedir senha ou use TWINE_PASSWORD
```

5) **Instalar do TestPyPI (opcional)**
```bash
python -m pip install --index-url https://test.pypi.org/simple/ --no-deps gerador-api-segura-v3
# ou via pipx para isolar:
pipx install --index-url https://test.pypi.org/simple/ --pip-args='--no-deps' gerador-api-segura-v3
```

6) **Publicar no PyPI**
```bash
twine upload dist/*
```

Depois, qualquer pessoa poderá instalar com:
```bash
pipx install gerador-api-segura-v3
# ou
python -m pip install gerador-api-segura-v3
```

## Personalizações e versão *Pro*
- Refatore o script para uma função `main()` e (opcional) troque `input()` por flags com `argparse` ou `typer`.
- Adicione testes do CLI e CI de publicação automática.
- Use *Semantic Versioning* (ex.: `0.1.0`, `0.2.0`, ...). -->

## Licença
MIT
