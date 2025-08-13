# gerador_api_segura_v3.py
import os, sys, platform, subprocess
from pathlib import Path
from textwrap import dedent

print("==== Gerador: API Flask Segura v3 (Mongo | MariaDB | PostgreSQL) ====")

# ---------- Inputs ----------
raiz = input("Nome da pasta raiz do projeto: ").strip()
if not raiz:
    print("Nome da pasta não pode ser vazio."); sys.exit(1)

db_type = (input("Tipo de banco [mongo|mariadb|postgres]: ") or "mongo").strip().lower()
if db_type not in {"mongo", "mariadb", "postgres"}:
    print("Use: mongo, mariadb ou postgres."); sys.exit(1)

cors_origins = input("CORS (vírgulas) [http://localhost:5173,http://localhost:3000]: ") or "http://localhost:5173,http://localhost:3000"
api_host = input("Host da API [0.0.0.0]: ") or "0.0.0.0"
api_port = input("Porta da API [5000]: ") or "5000"

# DB params
if db_type == "mongo":
    mongo_host = input("Host Mongo [localhost]: ") or "localhost"
    mongo_port = input("Porta Mongo [27017]: ") or "27017"
    mongo_db   = input("Database [servicesdb]: ") or "servicesdb"
    mongo_user = input("Usuário Mongo [root]: ") or "root"
    mongo_pass = input("Senha Mongo [root]: ") or "root"
    DB_URI = f"mongodb://{mongo_user}:{mongo_pass}@{mongo_host}:{mongo_port}/{mongo_db}?authSource=admin"
else:
    sql_host = input("Host SQL [localhost]: ") or "localhost"
    sql_port = input("Porta SQL [3306|5432]: ") or ("3306" if db_type=="mariadb" else "5432")
    sql_db   = input("Database [servicesdb]: ") or "servicesdb"
    sql_user = input("Usuário SQL [app]: ") or "app"
    sql_pass = input("Senha SQL [app]: ") or "app"
    if db_type == "mariadb":
        DB_URI = f"mysql+pymysql://{sql_user}:{sql_pass}@{sql_host}:{sql_port}/{sql_db}"
    else:
        DB_URI = f"postgresql+psycopg2://{sql_user}:{sql_pass}@{sql_host}:{sql_port}/{sql_db}"

# ---------- Helpers ----------
def w(s: str) -> str:
    # normaliza indentação e garante quebra final real (não literal "\n")
    return dedent(s).lstrip("\n").rstrip() + "\n"

# ---------- Estrutura ----------
pastas = [
    f"{raiz}/app",
    f"{raiz}/app/routes",
    f"{raiz}/app/controllers",
    f"{raiz}/app/models",
    f"{raiz}/app/schemas",
    f"{raiz}/app/services",
    f"{raiz}/app/utils",
    f"{raiz}/app/security",
    f"{raiz}/uploads",
    f"{raiz}/tests",
    f"{raiz}/ops",
    f"{raiz}/data/db",
    f"{raiz}/app/static",
    f"{raiz}/nginx",
]
for p in pastas: Path(p).mkdir(parents=True, exist_ok=True)

# ---------- Requirements ----------
req_common = """
Flask==3.0.3
python-dotenv==1.0.1
Flask-Cors==4.0.1
Flask-JWT-Extended==4.6.0
passlib[bcrypt]==1.7.4
marshmallow==3.21.3
Flask-Swagger-UI==4.11.1
Flask-Limiter==3.8.0
Flask-Talisman==1.1.0
werkzeug==3.0.3
gunicorn==22.0.0
sentry-sdk==2.9.0
prometheus-flask-exporter==0.23.0
pip-audit==2.7.3
pytest==8.2.2
requests==2.32.3
"""
if db_type == "mongo":
    req_db = "Flask-PyMongo==2.3.0\npymongo==4.8.0\n"
else:
    req_db = "Flask-SQLAlchemy==3.1.1\n" + ("PyMySQL==1.1.1\n" if db_type=="mariadb" else "psycopg2-binary==2.9.9\n")
(Path(raiz) / "requirements.txt").write_text(w(req_common + req_db), encoding="utf-8")

# ---------- .gitignore ----------
(Path(raiz) / ".gitignore").write_text(w(
    """
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# Virtual environment
.venv/

# Environment variables
.env

# IDE
.vscode/
.idea/
"""
), encoding="utf-8")

# ---------- .env ----------
env = {
    "FLASK_ENV": "development",
    "API_HOST": api_host,
    "API_PORT": api_port,
    "API_PREFIX": "/api/v1",
    "CORS_ORIGINS": cors_origins,
    "JWT_SECRET_KEY": "troque_esta_chave",
    "JWT_ACCESS_TOKEN_EXPIRES": "3600",
    "JWT_IN_COOKIES": "false",
    "UPLOAD_FOLDER": "uploads",
    "MAX_CONTENT_LENGTH": "10000000",
    "ALLOWED_EXTENSIONS": "png,jpg,jpeg,gif,pdf",
    "ADMIN_IP_WHITELIST": "127.0.0.1,::1",
    "RBAC_DEFAULT_ROLE": "user",
    "SENTRY_DSN": "",
    "PROMETHEUS_METRICS": "true",
    "DOCS_REQUIRE_ADMIN": "true",
    "HSTS_SECONDS": "31536000",
    "CONTENT_SECURITY_POLICY": "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self'",
}
if db_type == "mongo":
    env.update({"DB_TYPE": "mongo", "MONGO_URI": DB_URI})
else:
    env.update({"DB_TYPE": db_type, "SQLALCHEMY_DATABASE_URI": DB_URI, "SQLALCHEMY_TRACK_MODIFICATIONS": "False"})
(Path(raiz) / ".env").write_text("\n".join(f"{k}={v}" for k,v in env.items()) + "\n", encoding="utf-8")

# ---------- Dockerfile ----------
(Path(raiz) / "Dockerfile").write_text(w(f"""
FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN useradd -m appuser
USER appuser
COPY . .
ENV PYTHONUNBUFFERED=1
ENV FLASK_RUN_HOST=0.0.0.0
EXPOSE {api_port}
CMD ["python", "app.py"]
"""), encoding="utf-8")

# ---------- docker-compose ----------
if db_type == "mongo":
    db_service = f"""
  db:
    image: mongo:7
    restart: always
    container_name: mongodb
    ports:
      - "{mongo_port}:27017"
    environment:
      MONGO_INITDB_ROOT_USERNAME: {mongo_user}
      MONGO_INITDB_ROOT_PASSWORD: {mongo_pass}
      MONGO_INITDB_DATABASE: {mongo_db}
    healthcheck:
      test: ["CMD", "mongosh", "--username={mongo_user}", "--password={mongo_pass}", "--eval", "db.adminCommand('ping')"]
      interval: 10s
      timeout: 5s
      retries: 10
    volumes:
      - ./data/db:/data/db
"""
else:
    if db_type == "mariadb":
        db_service = f"""
  db:
    image: mariadb:11
    restart: always
    container_name: mariadb
    environment:
      MARIADB_ROOT_PASSWORD: {sql_pass}
      MARIADB_DATABASE: {sql_db}
      MARIADB_USER: {sql_user}
      MARIADB_PASSWORD: {sql_pass}
    ports:
      - "{sql_port}:3306"
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost", "-p{sql_pass}"]
      interval: 10s
      timeout: 5s
      retries: 10
    volumes:
      - ./data/db:/var/lib/mysql
"""
    else:
        db_service = f"""
  db:
    image: postgres:16
    restart: always
    container_name: postgres
    environment:
      POSTGRES_PASSWORD: {sql_pass}
      POSTGRES_USER: {sql_user}
      POSTGRES_DB: {sql_db}
    ports:
      - "{sql_port}:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U {sql_user} -d {sql_db}"]
      interval: 10s
      timeout: 5s
      retries: 10
    volumes:
      - ./data/db:/var/lib/postgresql/data
"""
compose = f"""
version: '3.8'
services:{db_service}
  web:
    build: .
    container_name: flaskapi
    env_file: [.env]
    command: gunicorn -w 4 -b 0.0.0.0:{api_port} app:app
    ports:
      - "{api_port}:{api_port}"
    depends_on:
      db:
        condition: service_healthy
    volumes:
      - ./:/app

  # nginx reverso com TLS (opcional)
  # nginx:
  #   image: nginx:alpine
  #   container_name: nginx_proxy
  #   ports: ["80:80","443:443"]
  #   volumes:
  #     - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
  #     - ./nginx/certs:/etc/nginx/certs:ro
  #   depends_on: [web]
"""
(Path(raiz) / "docker-compose.yml").write_text(w(compose), encoding="utf-8")

# ---------- NGINX (opcional) ----------
(Path(raiz) / "nginx" / "nginx.conf").write_text(w(f"""
events {{}}
http {{
  server {{
    listen 80;
    return 301 https://$host$request_uri;
  }}
  server {{
    listen 443 ssl http2;
    ssl_certificate     /etc/nginx/certs/fullchain.pem;
    ssl_certificate_key /etc/nginx/certs/privkey.pem;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer" always;
    location / {{
      proxy_pass http://web:{api_port};
      proxy_set_header Host $host;
      proxy_set_header X-Real-IP $remote_addr;
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
      proxy_set_header X-Forwarded-Proto $scheme;
    }}
  }}
}}
"""), encoding="utf-8")

# ---------- app/config.py ----------
(Path(raiz) / "app" / "config.py").write_text(w("""
import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()
def _split_csv(v: str): return [x.strip() for x in v.split(",") if x.strip()]

class BaseConfig:
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "5000"))
    API_PREFIX = os.getenv("API_PREFIX", "/api/v1")

    DB_TYPE = os.getenv("DB_TYPE", "mongo")
    MONGO_URI = os.getenv("MONGO_URI")
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv("SQLALCHEMY_TRACK_MODIFICATIONS", "False").lower() == "true"

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "troque_esta_chave")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", "3600")))
    JWT_IN_COOKIES = os.getenv("JWT_IN_COOKIES", "false").lower() == "true"

    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads")
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", "10000000"))
    ALLOWED_EXTENSIONS = set(_split_csv(os.getenv("ALLOWED_EXTENSIONS", "png,jpg,jpeg,gif,pdf")))

    CORS_ORIGINS = _split_csv(os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000"))
    ADMIN_IP_WHITELIST = set(_split_csv(os.getenv("ADMIN_IP_WHITELIST", "127.0.0.1,::1")))
    RBAC_DEFAULT_ROLE = os.getenv("RBAC_DEFAULT_ROLE", "user")

    SENTRY_DSN = os.getenv("SENTRY_DSN", "")
    PROMETHEUS_METRICS = os.getenv("PROMETHEUS_METRICS", "true").lower() == "true"
    DOCS_REQUIRE_ADMIN = os.getenv("DOCS_REQUIRE_ADMIN", "true").lower() == "true"

    HSTS_SECONDS = int(os.getenv("HSTS_SECONDS", "31536000"))
    CONTENT_SECURITY_POLICY = os.getenv("CONTENT_SECURITY_POLICY", "default-src 'self'")

class DevelopmentConfig(BaseConfig):
    DEBUG = True

class ProductionConfig(BaseConfig):
    DEBUG = False

class TestingConfig(BaseConfig):
    TESTING = True

def get_config():
    env = os.getenv("FLASK_ENV", "development").lower()
    if env == "production": return ProductionConfig
    if env == "testing": return TestingConfig
    return DevelopmentConfig
"""), encoding="utf-8")

# ---------- app/extensions.py ----------
(Path(raiz) / "app" / "extensions.py").write_text(w("""
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Disponíveis para ambos os mundos:
jwt = JWTManager()
limiter = Limiter(key_func=get_remote_address)

# SQL
try:
    from flask_sqlalchemy import SQLAlchemy
    db = SQLAlchemy()
except Exception:  # pacote pode não existir se for Mongo
    db = None

# Mongo
try:
    from flask_pymongo import PyMongo
    mongo = PyMongo()
except Exception:
    mongo = None
"""), encoding="utf-8")

# ---------- RBAC / Firewall ----------
(Path(raiz) / "app" / "security" / "rbac.py").write_text(w("""
from functools import wraps
from flask import jsonify, request, current_app
from flask_jwt_extended import verify_jwt_in_request, get_jwt

def roles_required(*roles):
    def deco(fn):
        @wraps(fn)
        def wrap(*a, **k):
            verify_jwt_in_request()
            claims = get_jwt() or {}
            role = claims.get("role", current_app.config.get("RBAC_DEFAULT_ROLE","user"))
            if role not in roles:
                return jsonify({"msg": "Acesso negado: papel insuficiente"}), 403
            return fn(*a, **k)
        return wrap
    return deco

def admin_ip_required(fn):
    @wraps(fn)
    def wrap(*a, **k):
        wl = current_app.config.get("ADMIN_IP_WHITELIST", set())
        ip = request.headers.get("X-Forwarded-For", request.remote_addr or "").split(",")[0].strip()
        if ip not in wl:
            return jsonify({"msg": "Acesso negado pelo firewall de IP"}), 403
        return fn(*a, **k)
    return wrap
"""), encoding="utf-8")

# ---------- Rate key (usuário/IP) ----------
(Path(raiz) / "app" / "security" / "rate.py").write_text(w("""
from flask import request
from flask_jwt_extended import get_jwt_identity

def key_user_or_ip():
    try:
        uid = get_jwt_identity()
        if uid:
            return f"user:{uid}"
    except Exception:
        pass
    ip = request.headers.get("X-Forwarded-For", request.remote_addr or "")
    return ip.split(",")[0].strip()
"""), encoding="utf-8")

# ---------- Schemas ----------
(Path(raiz) / "app" / "schemas" / "user_schema.py").write_text(w("""
from marshmallow import Schema, fields, validate

class RegisterSchema(Schema):
    nome = fields.String(required=True, validate=validate.Length(min=2, max=120))
    email = fields.Email(required=True)
    password = fields.String(required=True, load_only=True, validate=validate.Length(min=6, max=128))

class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True, load_only=True, validate=validate.Length(min=6, max=128))
"""), encoding="utf-8")

(Path(raiz) / "app" / "schemas" / "item_schema.py").write_text(w("""
from marshmallow import Schema, fields, validate

class ItemCreateSchema(Schema):
    name = fields.String(required=True, validate=validate.Length(min=2, max=120))
    description = fields.String(required=False, allow_none=True, validate=validate.Length(max=1000))
    price = fields.Float(required=True, validate=validate.Range(min=0))
    stock = fields.Integer(required=True, validate=validate.Range(min=0))
    active = fields.Boolean(required=False, missing=True)

class ItemUpdateSchema(Schema):
    name = fields.String(validate=validate.Length(min=2, max=120))
    description = fields.String(allow_none=True, validate=validate.Length(max=1000))
    price = fields.Float(validate=validate.Range(min=0))
    stock = fields.Integer(validate=validate.Range(min=0))
    active = fields.Boolean()
"""), encoding="utf-8")

# ---------- Models (SQL) ----------
(Path(raiz) / "app" / "models" / "models_sql.py").write_text(w("""
from datetime import datetime
from passlib.hash import bcrypt
from sqlalchemy import func
from ..extensions import db

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(32), default="user", nullable=False)
    created_at = db.Column(db.DateTime, default=func.now(), nullable=False)

    def set_password(self, password: str):
        self.password_hash = bcrypt.hash(password)

    def check_password(self, password: str) -> bool:
        return bcrypt.verify(password, self.password_hash)

class Item(db.Model):
    __tablename__ = "items"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False, default=0.0)
    stock = db.Column(db.Integer, nullable=False, default=0)
    active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, default=func.now(), nullable=False)
"""), encoding="utf-8")

# ---------- Services (Auth) ----------
(Path(raiz) / "app" / "services" / "auth_service.py").write_text(w("""
from flask import current_app
from flask_jwt_extended import create_access_token
from passlib.hash import bcrypt
from datetime import timedelta
from ..extensions import db, mongo
from ..models.models_sql import User as SQLUser

def _ttl():
    exp = current_app.config.get("JWT_ACCESS_TOKEN_EXPIRES")
    if isinstance(exp, timedelta):
        return exp
    try:
        return timedelta(seconds=int(exp))
    except Exception:
        return timedelta(hours=1)

def register_user(nome: str, email: str, password: str) -> dict:
    dbt = current_app.config.get("DB_TYPE")
    if dbt == "mongo":
        # Mongo
        u = mongo.db.users.find_one({"email": email})
        if u:
            return {"error": "E-mail já cadastrado"}
        mongo.db.users.insert_one({
            "nome": nome, "email": email,
            "password_hash": bcrypt.hash(password),
            "role": "user"
        })
        return {"ok": True}
    else:
        # SQL
        if SQLUser.query.filter_by(email=email).first():
            return {"error": "E-mail já cadastrado"}
        u = SQLUser(nome=nome, email=email, role="user")
        u.set_password(password)
        db.session.add(u)
        db.session.commit()
        return {"ok": True}

def authenticate(email: str, password: str):
    dbt = current_app.config.get("DB_TYPE")
    if dbt == "mongo":
        u = mongo.db.users.find_one({"email": email})
        if not u or not bcrypt.verify(password, u.get("password_hash","")):
            return None
        identity = str(u["_id"])
        claims = {"role": u.get("role","user"), "email": email}
        return create_access_token(identity=identity, additional_claims=claims, expires_delta=_ttl())
    else:
        u = SQLUser.query.filter_by(email=email).first()
        if not u or not u.check_password(password):
            return None
        identity = str(u.id)
        claims = {"role": u.role, "email": u.email}
        return create_access_token(identity=identity, additional_claims=claims, expires_delta=_ttl())
"""), encoding="utf-8")

# ---------- Routes: Auth ----------
(Path(raiz) / "app" / "routes" / "auth_routes.py").write_text(w("""
from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..schemas.user_schema import RegisterSchema, LoginSchema
from ..services.auth_service import register_user, authenticate

bp_auth = Blueprint("auth", __name__, url_prefix="/auth")
_reg = RegisterSchema()
_log = LoginSchema()

@bp_auth.post("/register")
def register():
    try:
        data = _reg.load(request.get_json() or {})
    except ValidationError as e:
        return {"msg":"Erro de validação","erros":e.messages}, 400
    r = register_user(**data)
    if "error" in r:
        return {"msg": r["error"]}, 400
    return {"msg": "Usuário cadastrado com sucesso"}, 201

@bp_auth.post("/login")
def login():
    try:
        data = _log.load(request.get_json() or {})
    except ValidationError as e:
        return {"msg":"Erro de validação","erros":e.messages}, 400
    token = authenticate(data["email"], data["password"])
    if not token:
        return {"msg": "Credenciais inválidas"}, 401
    return {"access_token": token}

@bp_auth.get("/me")
@jwt_required()
def me():
    return {"identity": get_jwt_identity()}
"""), encoding="utf-8")

# ---------- Routes: Items ----------
(Path(raiz) / "app" / "routes" / "item_routes.py").write_text(w("""
from flask import Blueprint, request, jsonify, current_app
from marshmallow import ValidationError
from flask_jwt_extended import jwt_required
from ..schemas.item_schema import ItemCreateSchema, ItemUpdateSchema
from ..extensions import db, mongo
from ..models.models_sql import Item as SQLItem

bp_items = Blueprint("items", __name__, url_prefix="/items")
_cr = ItemCreateSchema()
_up = ItemUpdateSchema()

@bp_items.get("/")
@jwt_required()
def list_items():
    dbt = current_app.config.get("DB_TYPE")
    if dbt == "mongo":
        docs = list(mongo.db.items.find({}))
        for d in docs:
            d["_id"] = str(d["_id"])
        return jsonify(docs)
    else:
        items = SQLItem.query.order_by(SQLItem.id.desc()).all()
        return jsonify([{
            "id": i.id, "name": i.name, "description": i.description,
            "price": i.price, "stock": i.stock, "active": i.active
        } for i in items])

@bp_items.post("/")
@jwt_required()
def create_item():
    try:
        data = _cr.load(request.get_json() or {})
    except ValidationError as e:
        return {"msg":"Erro de validação","erros":e.messages}, 400
    dbt = current_app.config.get("DB_TYPE")
    if dbt == "mongo":
        ins = mongo.db.items.insert_one(data)
        return {"_id": str(ins.inserted_id)}, 201
    else:
        it = SQLItem(**data)
        db.session.add(it); db.session.commit()
        return {"id": it.id}, 201

@bp_items.put("/<int:item_id>")
@jwt_required()
def update_item_sql(item_id):
    dbt = current_app.config.get("DB_TYPE")
    if dbt == "mongo":
        return {"msg":"Use /items/<id> (string) para Mongo"}, 400
    try:
        data = _up.load(request.get_json() or {})
    except ValidationError as e:
        return {"msg":"Erro de validação","erros":e.messages}, 400
    it = SQLItem.query.get_or_404(item_id)
    for k,v in data.items(): setattr(it, k, v)
    db.session.commit()
    return {"msg": "OK"}

@bp_items.put("/<string:item_id>")
@jwt_required()
def update_item_mongo(item_id):
    dbt = current_app.config.get("DB_TYPE")
    if dbt != "mongo":
        return {"msg":"Use /items/<int:id> para SQL"}, 400
    from bson import ObjectId
    try:
        data = _up.load(request.get_json() or {})
    except ValidationError as e:
        return {"msg":"Erro de validação","erros":e.messages}, 400
    mongo.db.items.update_one({"_id": ObjectId(item_id)}, {"$set": data})
    return {"msg":"OK"}

@bp_items.delete("/<int:item_id>")
@jwt_required()
def delete_item_sql(item_id):
    dbt = current_app.config.get("DB_TYPE")
    if dbt == "mongo":
        return {"msg":"Use /items/<id> (string) para Mongo"}, 400
    it = SQLItem.query.get_or_404(item_id)
    db.session.delete(it); db.session.commit()
    return {"msg":"OK"}

@bp_items.delete("/<string:item_id>")
@jwt_required()
def delete_item_mongo(item_id):
    dbt = current_app.config.get("DB_TYPE")
    if dbt != "mongo":
        return {"msg":"Use /items/<int:id> para SQL"}, 400
    from bson import ObjectId
    mongo.db.items.delete_one({"_id": ObjectId(item_id)})
    return {"msg":"OK"}
"""), encoding="utf-8")

# ---------- Routes: Health & Docs ----------
(Path(raiz) / "app" / "routes" / "misc_routes.py").write_text(w("""
from flask import Blueprint, jsonify, current_app, send_from_directory
from ..security.rbac import admin_ip_required

bp_misc = Blueprint("misc", __name__)

@bp_misc.get("/health")
def health():
    return {"status":"ok"}

@bp_misc.get("/docs/spec")
def swagger_spec():
    # serve o arquivo gerado em app/static/swagger.json
    return send_from_directory(current_app.static_folder, "swagger.json", mimetype="application/json")
"""), encoding="utf-8")

# ---------- Swagger JSON mínimo ----------
(Path(raiz) / "app" / "static" / "swagger.json").write_text(w(f"""
{{
  "openapi": "3.0.1",
  "info": {{
    "title": "API Flask Segura v3",
    "version": "1.0.0"
  }},
  "servers": [{{ "url": "http://localhost:{api_port}/api/v1" }}],
  "paths": {{
    "/auth/register": {{"post": {{"summary": "Registrar", "responses": {{"201": {{"description": "OK"}}}}}}}},
    "/auth/login":    {{"post": {{"summary": "Login",     "responses": {{"200": {{"description": "OK"}}}}}}}},
    "/items/":        {{"get":  {{"summary": "Listar",    "responses": {{"200": {{"description": "OK"}}}}}},
                       "post":  {{"summary": "Criar",     "responses": {{"201": {{"description": "Criado"}}}}}}}}
  }}
}}
"""), encoding="utf-8")

# ---------- App Factory ----------
(Path(raiz) / "app" / "__init__.py").write_text(w("""
from flask import Flask, jsonify
from flask_cors import CORS
from flask_talisman import Talisman
from prometheus_flask_exporter import PrometheusMetrics
from .config import get_config
from .extensions import jwt, limiter, db, mongo
from .routes.auth_routes import bp_auth
from .routes.item_routes import bp_items
from .routes.misc_routes import bp_misc
from .security.rate import key_user_or_ip

def create_app():
    app = Flask(__name__, static_folder="static")
    app.config.from_object(get_config())

    # CORS
    CORS(app, resources={r"/*": {"origins": app.config.get("CORS_ORIGINS", ["http://localhost:3000"])}})

    # JWT + rate limit
    jwt.init_app(app)
    limiter.init_app(app)
    limiter.request_filter(lambda: False)
    limiter.key_func = key_user_or_ip

    # DB
    dbt = app.config.get("DB_TYPE")
    if dbt == "mongo":
        if mongo is None:
            raise RuntimeError("Instale dependências de Mongo para usar DB_TYPE=mongo.")
        app.config["MONGO_URI"] = app.config.get("MONGO_URI")
        mongo.init_app(app)
    else:
        if db is None:
            raise RuntimeError("Instale dependências de SQL para usar DB_TYPE=postgres/mariadb.")
        db.init_app(app)
        with app.app_context():
            db.create_all()

    # Segurança HTTP
    csp = app.config.get("CONTENT_SECURITY_POLICY","default-src 'self'")
    Talisman(app, force_https=False, content_security_policy=csp)

    # Prometheus
    if app.config.get("PROMETHEUS_METRICS", True):
        PrometheusMetrics(app)

    # Blueprints (com prefixo)
    prefix = app.config.get("API_PREFIX","/api/v1")
    app.register_blueprint(bp_misc, url_prefix=prefix)
    app.register_blueprint(bp_auth, url_prefix=prefix)
    app.register_blueprint(bp_items, url_prefix=prefix)

    # Docs (Swagger UI)
    try:
        from flask_swagger_ui import get_swaggerui_blueprint
        SWAGGER_URL = "/docs"
        API_URL = f"{prefix}/docs/spec"
        swaggerui_blueprint = get_swaggerui_blueprint(SWAGGER_URL, API_URL, config={"app_name": "API Segura v3"})
        app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
    except Exception:
        pass

    @app.errorhandler(429)
    def ratelimit_handler(e):
        return jsonify({"msg":"limite de requisições excedido"}), 429

    return app
"""), encoding="utf-8")

# ---------- app.py (runner) ----------
(Path(raiz) / "app.py").write_text(w("""
from app import create_app
from app.config import get_config

app = create_app()

if __name__ == "__main__":
    cfg = get_config()
    host = cfg.API_HOST
    port = cfg.API_PORT
    app.run(host=host, port=port)
"""), encoding="utf-8")

# ---------- README ----------
(Path(raiz) / "README.md").write_text(w(f"""
# API Flask Segura v3

Geração automática via **gerador-api-segura-v3** ({db_type}).

## Rodando local

```bash
python -m venv .venv
# Windows
# .\\.venv\\Scripts\\Activate.ps1
# Linux/Mac
# source .venv/bin/activate

pip install -r requirements.txt
cp .env .env.local || true
python app.py
