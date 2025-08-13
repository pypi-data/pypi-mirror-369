```markdown
# gerador-api-segura-v3

**CLI** para gerar uma **API Flask Segura** com suporte a **MongoDB / MariaDB / PostgreSQL**, incluindo:
- Autenticação **JWT**
- **RBAC** (papéis) e firewall por IP para rotas admin
- **Rate Limiting**
- **CORS**
- **Flask-Talisman** (CSP, HSTS, headers de segurança)
- **Swagger UI** (com proteção opcional por JWT admin)
- **Logs** (arquivo giratório)
- **Métricas Prometheus**
- **Docker/Docker Compose** e **NGINX** (opcional)

> O pacote empacota e expõe seu script `gerador_api_segura_v3.py` como um comando de terminal.

---

## ⚙️ Requisitos

- **Python 3.10+** (recomendado 3.12/3.13)
- (Opcional) **Docker** e **Docker Compose**

---

## 🚀 Como usar (recomendado: `pipx`)

Sem criar `venv` e sem “sujar” o Python do sistema:

```bash
pip install -U pipx
pipx ensurepath   # se pedir, feche e reabra o terminal/PowerShell
pipx run gerador-api-segura-v3==0.1.12 --dest MinhaAPI
```

Troque `MinhaAPI` pelo nome da pasta do seu projeto.  
O gerador pergunta interativamente o necessário (DB, porta, etc).  
Você também pode passar `--db mongo|mariadb|postgres`.

### Instalar o comando permanentemente (opcional)

```bash
pipx install gerador-api-segura-v3==0.1.12
gerador-api-segura --version
# ou, dependendo do entrypoint disponível:
gerador-api-segura-v3 --version
```

### 🧪 Exemplos rápidos

```bash
# Projeto padrão (PostgreSQL)
pipx run gerador-api-segura-v3==0.1.12 --dest MinhaAPI

# MongoDB
pipx run gerador-api-segura-v3==0.1.12 --dest MinhaAPI --db mongo

# MariaDB
pipx run gerador-api-segura-v3==0.1.12 --dest MinhaAPI --db mariadb
```

As flags `--dest` e `--db` são opcionais; o gerador pergunta se você não informar.

---

## 🧰 Alternativa: usar venv

### Windows (PowerShell)

```powershell
# 1) criar a venv na pasta atual
python -m venv .venv

# 2) ativar
.\.venv\Scripts\Activate.ps1

# 3) atualizar o pip (sempre pelo -m)
python -m pip install -U pip

# 4) instalar o gerador
python -m pip install "gerador-api-segura-v3>=0.1.12"

# 5) rodar o gerador
# opção A (sempre funciona)
python -m gerador_api_segura_v3 --dest MinhaAPI --db postgres

# opção B (executável da venv)
.\.venv\Scripts\gerador-api-segura.exe --dest MinhaAPI --db postgres

# sair da venv
deactivate
```

Se o PowerShell bloquear a ativação:  
`Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` e ative novamente.

### Linux / macOS

```bash
# 1) criar
python3 -m venv .venv

# 2) ativar
source .venv/bin/activate

# 3) atualizar pip
python -m pip install -U pip

# 4) instalar o gerador
python -m pip install "gerador-api-segura-v3>=0.1.12"

# 5) rodar
# opção A (sempre funciona)
python -m gerador_api_segura_v3 --dest MinhaAPI --db mongo

# opção B (executável da venv)
./.venv/bin/gerador-api-segura --dest MinhaAPI --db mongo

# sair
deactivate
```

---

## ⚡ One-liner (sem pipx, sem venv)

Instalar e rodar em um comando:

```bash
python -m pip install -U gerador-api-segura-v3 ; python -m gerador_api_segura_v3 --dest MinhaAPI
```

---

## 🔁 Atualizar / Remover

### pipx

```bash
pipx upgrade gerador-api-segura-v3
pipx uninstall gerador-api-segura-v3
```

### pip (global/venv)

```bash
python -m pip install -U gerador-api-segura-v3
python -m pip uninstall gerador-api-segura-v3
```

---

## 🛠️ Solução de problemas

### “Comando não reconhecido” após pipx install

Rode `pipx ensurepath` e reabra o terminal/PowerShell.

### Conflito entre global e venv

Prefira `python -m gerador_api_segura_v3 ...` (usa o Python ativo).

### Quero ver de onde vem o comando

- **Windows**: `Get-Command gerador-api-segura* -ErrorAction SilentlyContinue`
- **Linux/macOS**: `which gerador-api-segura`

### Verificar versão instalada

```bash
python - << "PY"
import importlib.metadata as m
print("gerador-api-segura-v3:", m.version("gerador-api-segura-v3"))
PY
```

---

## 🔧 Desenvolvimento local

Instalação em modo desenvolvimento (a partir do código-fonte):

```bash
# dentro da pasta do projeto
python -m pip install -U build hatchling
python -m pip install -e .
gerador-api-segura --version
```

---

## 📦 Sobre o pacote

Este repositório/pacote contém o CLI do gerador.  
Ele chama o script empacotado `gerador_api_segura_v3.py` e gera a estrutura do projeto Flask com os recursos de segurança e devops listados acima.

---

## 📄 Licença

MIT
```
