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
    f"{raiz}/static",
    f"{raiz}/ops",
    f"{raiz}/data/db",
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
(Path(raiz) / ".gitignore").write_text(w("""
__pycache__/
*.pyc
*.pyo
.env
.venv/
env/
uploads/
dist/
build/
.vscode/
.idea/
*.log
*.pid
docker-compose.override.yml
.DS_Store
Thumbs.db
data/db/
"""), encoding="utf-8")

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
if db_type == "mongo":
    ext = """
from flask_pymongo import PyMongo
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

mongo = PyMongo()
jwt = JWTManager()
limiter = Limiter(key_func=get_remote_address)
"""
else:
    ext = """
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

db = SQLAlchemy()
jwt = JWTManager()
limiter = Limiter(key_func=get_remote_address)
"""
(Path(raiz) / "app" / "extensions.py").write_text(w(ext), encoding="utf-8")

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
if db_type != "mongo":
    (Path(raiz) / "app" / "models" / "user.py").write_text(w("""
from datetime import datetime
from app.extensions import db

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(180), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(32), nullable=False, default="user")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
"""), encoding="utf-8")

    (Path(raiz) / "app" / "models" / "item.py").write_text(w("""
from datetime import datetime
from app.extensions import db

class Item(db.Model):
    __tablename__ = "items"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, index=True)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(12,2), nullable=False)
    stock = db.Column(db.Integer, nullable=False, default=0)
    active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
"""), encoding="utf-8")

# ---------- Utils upload ----------
(Path(raiz) / "app" / "utils" / "upload.py").write_text(w("""
import os
from werkzeug.utils import secure_filename

def allowed_file(filename: str, allowed_exts: set):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_exts

def save_upload(file, app):
    allowed_exts = app.config.get("ALLOWED_EXTENSIONS", set())
    if file and allowed_file(file.filename, allowed_exts):
        filename = secure_filename(file.filename)
        upload_folder = app.config.get("UPLOAD_FOLDER", "uploads")
        os.makedirs(upload_folder, exist_ok=True)
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
        return filename
    return None
"""), encoding="utf-8")

# ---------- Controllers: auth ----------
if db_type == "mongo":
    auth_ctrl = """
from flask import request, jsonify, current_app
from app.extensions import mongo, limiter
from app.schemas.user_schema import RegisterSchema, LoginSchema
from passlib.hash import bcrypt
from flask_jwt_extended import create_access_token, set_access_cookies

register_schema = RegisterSchema()
login_schema = LoginSchema()

@limiter.limit("8/minute")
def register():
    data = request.get_json(silent=True) or {}
    errors = register_schema.validate(data)
    if errors: return jsonify({"msg": "Erro de validação", "erros": errors}), 400
    if mongo.db.users.find_one({"email": data["email"]}):
        return jsonify({"msg": "Email já registrado"}), 400
    mongo.db.users.insert_one({"nome": data["nome"], "email": data["email"], "password": bcrypt.hash(data["password"]), "role": "user"})
    return jsonify({"msg": "Usuário registrado com sucesso."}), 201

@limiter.limit("15/minute")
def login():
    data = request.get_json(silent=True) or {}
    errors = login_schema.validate(data)
    if errors: return jsonify({"msg": "Erro de validação", "erros": errors}), 400
    u = mongo.db.users.find_one({"email": data["email"]})
    if not u or not bcrypt.verify(data["password"], u.get("password","")):
        return jsonify({"msg": "Credenciais inválidas"}), 401
    claims = {"role": u.get("role","user")}
    token = create_access_token(identity=str(u["_id"]), additional_claims=claims)
    if current_app.config.get("JWT_IN_COOKIES", False):
        resp = jsonify({"msg":"ok"}); set_access_cookies(resp, token); return resp, 200
    return jsonify({"token": token, "user": {"_id": str(u["_id"]), "nome": u["nome"], "email": u["email"], "role": u.get("role","user")}}), 200
"""
else:
    auth_ctrl = """
from flask import request, jsonify, current_app
from app.extensions import db, limiter
from app.models.user import User
from app.schemas.user_schema import RegisterSchema, LoginSchema
from passlib.hash import bcrypt
from flask_jwt_extended import create_access_token, set_access_cookies

register_schema = RegisterSchema()
login_schema = LoginSchema()

@limiter.limit("8/minute")
def register():
    data = request.get_json(silent=True) or {}
    errors = register_schema.validate(data)
    if errors: return jsonify({"msg": "Erro de validação", "erros": errors}), 400
    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"msg": "Email já registrado"}), 400
    u = User(nome=data["nome"], email=data["email"], password=bcrypt.hash(data["password"]), role="user")
    db.session.add(u); db.session.commit()
    return jsonify({"msg": "Usuário registrado com sucesso."}), 201

@limiter.limit("15/minute")
def login():
    data = request.get_json(silent=True) or {}
    errors = login_schema.validate(data)
    if errors: return jsonify({"msg": "Erro de validação", "erros": errors}), 400
    u = User.query.filter_by(email=data["email"]).first()
    if not u or not bcrypt.verify(data["password"], u.password):
        return jsonify({"msg": "Credenciais inválidas"}), 401
    claims = {"role": u.role or "user"}
    token = create_access_token(identity=str(u.id), additional_claims=claims)
    if current_app.config.get("JWT_IN_COOKIES", False):
        resp = jsonify({"msg":"ok"}); set_access_cookies(resp, token); return resp, 200
    return jsonify({"token": token, "user": {"id": u.id, "nome": u.nome, "email": u.email, "role": u.role}}), 200
"""
(Path(raiz) / "app" / "controllers" / "auth_controller.py").write_text(w(auth_ctrl), encoding="utf-8")

# ---------- Controllers: items (CRUD com RBAC) ----------
if db_type == "mongo":
    items_ctrl = """
from flask import request, jsonify
from flask_jwt_extended import jwt_required
from app.extensions import mongo, limiter
from app.schemas.item_schema import ItemCreateSchema, ItemUpdateSchema
from app.security.rbac import roles_required
from bson import ObjectId
from datetime import datetime

create_schema = ItemCreateSchema()
update_schema = ItemUpdateSchema()

@limiter.limit("30/minute")
@jwt_required()
def list_items():
    q = {}
    if request.args.get("only_active") == "true":
        q["active"] = True
    items = []
    for it in mongo.db.items.find(q):
        it["_id"] = str(it["_id"])
        items.append(it)
    return jsonify(items), 200

@limiter.limit("60/minute")
@jwt_required()
def get_item(item_id):
    try:
        it = mongo.db.items.find_one({"_id": ObjectId(item_id)})
    except Exception:
        return jsonify({"msg": "ID inválido"}), 400
    if not it: return jsonify({"msg":"Item não encontrado"}), 404
    it["_id"] = str(it["_id"])
    return jsonify(it), 200

@limiter.limit("10/minute")
@jwt_required()
@roles_required("admin")
def create_item():
    data = request.get_json(silent=True) or {}
    errs = create_schema.validate(data)
    if errs: return jsonify({"msg":"Erro de validação","erros":errs}), 400
    data["created_at"] = datetime.utcnow()
    res = mongo.db.items.insert_one(data)
    it = mongo.db.items.find_one({"_id": res.inserted_id})
    it["_id"] = str(it["_id"])
    return jsonify(it), 201

@limiter.limit("10/minute")
@jwt_required()
@roles_required("admin")
def update_item(item_id):
    data = request.get_json(silent=True) or {}
    errs = update_schema.validate(data)
    if errs: return jsonify({"msg":"Erro de validação","erros":errs}), 400
    try:
        oid = ObjectId(item_id)
    except Exception:
        return jsonify({"msg":"ID inválido"}), 400
    r = mongo.db.items.update_one({"_id": oid}, {"$set": data})
    if r.matched_count == 0: return jsonify({"msg":"Item não encontrado"}), 404
    it = mongo.db.items.find_one({"_id": oid})
    it["_id"] = str(it["_id"])
    return jsonify(it), 200

@limiter.limit("10/minute")
@jwt_required()
@roles_required("admin")
def delete_item(item_id):
    try:
        oid = ObjectId(item_id)
    except Exception:
        return jsonify({"msg":"ID inválido"}), 400
    r = mongo.db.items.delete_one({"_id": oid})
    if r.deleted_count == 0: return jsonify({"msg":"Item não encontrado"}), 404
    return jsonify({"msg":"Removido"}), 200
"""
else:
    items_ctrl = """
from flask import request, jsonify
from flask_jwt_extended import jwt_required
from app.extensions import db, limiter
from app.models.item import Item
from app.schemas.item_schema import ItemCreateSchema, ItemUpdateSchema
from app.security.rbac import roles_required
from decimal import Decimal

create_schema = ItemCreateSchema()
update_schema = ItemUpdateSchema()

@limiter.limit("30/minute")
@jwt_required()
def list_items():
    only_active = request.args.get("only_active") == "true"
    q = Item.query
    if only_active: q = q.filter_by(active=True)
    data = [{
        "id": it.id, "name": it.name, "description": it.description,
        "price": float(it.price), "stock": it.stock, "active": it.active,
        "created_at": it.created_at.isoformat()
    } for it in q.order_by(Item.id.asc()).all()]
    return jsonify(data), 200

@limiter.limit("60/minute")
@jwt_required()
def get_item(item_id):
    it = Item.query.get(int(item_id))
    if not it: return jsonify({"msg":"Item não encontrado"}), 404
    data = {"id": it.id, "name": it.name, "description": it.description,
            "price": float(it.price), "stock": it.stock, "active": it.active,
            "created_at": it.created_at.isoformat()}
    return jsonify(data), 200

@limiter.limit("10/minute")
@jwt_required()
@roles_required("admin")
def create_item():
    data = request.get_json(silent=True) or {}
    errs = create_schema.validate(data)
    if errs: return jsonify({"msg":"Erro de validação","erros":errs}), 400
    it = Item(name=data["name"], description=data.get("description"),
              price=Decimal(str(data["price"])), stock=int(data["stock"]),
              active=bool(data.get("active", True)))
    db.session.add(it); db.session.commit()
    return jsonify({"id": it.id, "name": it.name, "description": it.description,
                    "price": float(it.price), "stock": it.stock, "active": it.active,
                    "created_at": it.created_at.isoformat()}), 201

@limiter.limit("10/minute")
@jwt_required()
@roles_required("admin")
def update_item(item_id):
    data = request.get_json(silent=True) or {}
    errs = update_schema.validate(data)
    if errs: return jsonify({"msg":"Erro de validação","erros":errs}), 400
    it = Item.query.get(int(item_id))
    if not it: return jsonify({"msg":"Item não encontrado"}), 404
    if "name" in data: it.name = data["name"]
    if "description" in data: it.description = data["description"]
    if "price" in data: it.price = Decimal(str(data["price"]))
    if "stock" in data: it.stock = int(data["stock"])
    if "active" in data: it.active = bool(data["active"])
    db.session.commit()
    return jsonify({"id": it.id, "name": it.name, "description": it.description,
                    "price": float(it.price), "stock": it.stock, "active": it.active,
                    "created_at": it.created_at.isoformat()}), 200

@limiter.limit("10/minute")
@jwt_required()
@roles_required("admin")
def delete_item(item_id):
    it = Item.query.get(int(item_id))
    if not it: return jsonify({"msg":"Item não encontrado"}), 404
    db.session.delete(it); db.session.commit()
    return jsonify({"msg":"Removido"}), 200
"""
(Path(raiz) / "app" / "controllers" / "items_controller.py").write_text(w(items_ctrl), encoding="utf-8")

# ---------- Routes ----------
(Path(raiz) / "app" / "routes" / "__init__.py").write_text("", encoding="utf-8")
(Path(raiz) / "app" / "__init__.py").write_text("", encoding="utf-8")

(Path(raiz) / "app" / "routes" / "auth_routes.py").write_text(w("""
from flask import Blueprint
from app.controllers.auth_controller import register, login
auth_bp = Blueprint('auth_bp', __name__)
auth_bp.add_url_rule('/register', view_func=register, methods=['POST'])
auth_bp.add_url_rule('/login', view_func=login, methods=['POST'])
"""), encoding="utf-8")

if db_type == "mongo":
    user_routes = """
from flask import Blueprint, jsonify
from app.extensions import mongo
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId
user_bp = Blueprint('user_bp', __name__)
@user_bp.get('/')
@jwt_required()
def list_users():
    users = []
    for u in mongo.db.users.find({}, {"password":0}):
        u["_id"]=str(u["_id"])
        users.append(u)
    return jsonify(users),200
@user_bp.get('/me')
@jwt_required()
def get_me():
    uid = get_jwt_identity()
    try:
        u = mongo.db.users.find_one({"_id": ObjectId(uid)}, {"password":0})
    except Exception:
        return jsonify({"msg":"Token inválido"}),401
    if not u: return jsonify({"msg":"Usuário não encontrado"}),404
    u["_id"]=str(u["_id"])
    return jsonify(u),200
"""
else:
    user_routes = """
from flask import Blueprint, jsonify
from app.models.user import User
from flask_jwt_extended import jwt_required, get_jwt_identity
user_bp = Blueprint('user_bp', __name__)
@user_bp.get('/')
@jwt_required()
def list_users():
    data = [{"id":u.id,"nome":u.nome,"email":u.email,"role":u.role,"created_at":u.created_at.isoformat()} for u in User.query.order_by(User.id.asc()).all()]
    return jsonify(data),200
@user_bp.get('/me')
@jwt_required()
def get_me():
    uid = int(get_jwt_identity())
    u = User.query.get(uid)
    if not u: return jsonify({"msg":"Usuário não encontrado"}),404
    return jsonify({"id":u.id,"nome":u.nome,"email":u.email,"role":u.role,"created_at":u.created_at.isoformat()}),200
"""
(Path(raiz) / "app" / "routes" / "user_routes.py").write_text(w(user_routes), encoding="utf-8")

(Path(raiz) / "app" / "routes" / "upload_routes.py").write_text(w("""
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
from app.utils.upload import save_upload
upload_bp = Blueprint('upload_bp', __name__)
@upload_bp.post('/upload')
@jwt_required()
def upload_file():
    if 'file' not in request.files:
        return jsonify({"msg":"Arquivo não enviado"}),400
    file = request.files['file']
    filename = save_upload(file, current_app)
    if filename: return jsonify({"msg":"Upload com sucesso","filename":filename}),201
    return jsonify({"msg":"Tipo de arquivo não permitido ou erro ao salvar"}),400
"""), encoding="utf-8")

(Path(raiz) / "app" / "routes" / "items_routes.py").write_text(w("""
from flask import Blueprint
from app.controllers.items_controller import list_items, get_item, create_item, update_item, delete_item
items_bp = Blueprint('items_bp', __name__)
items_bp.add_url_rule('/', view_func=list_items, methods=['GET'])
items_bp.add_url_rule('/', view_func=create_item, methods=['POST'])
items_bp.add_url_rule('/<item_id>', view_func=get_item, methods=['GET'])
items_bp.add_url_rule('/<item_id>', view_func=update_item, methods=['PUT','PATCH'])
items_bp.add_url_rule('/<item_id>', view_func=delete_item, methods=['DELETE'])
"""), encoding="utf-8")

# ---------- Admin routes com RBAC + IP firewall + rate key + audit ----------
(Path(raiz) / "app" / "routes" / "admin_routes.py").write_text(w("""
from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.security.rbac import roles_required, admin_ip_required
from app.security.rate import key_user_or_ip
from app.extensions import limiter

admin_bp = Blueprint('admin_bp', __name__)

def _audit(action: str, status: str, detail: dict | None = None):
    try:
        uid = get_jwt_identity()
    except Exception:
        uid = None
    payload = {"actor": uid, "action": action, "status": status, "detail": detail or {}}
    current_app.logger.info(f"[ADMIN-AUDIT] {payload}")

def _valid_role(role: str) -> bool:
    return role in {"admin", "user", "manager", "viewer"}

def _locate_user(by_id: str | None, by_email: str | None):
    db_type = current_app.config.get("DB_TYPE", "mongo")
    if db_type == "mongo":
        from app.extensions import mongo
        from bson import ObjectId
        if by_id:
            try:
                u = mongo.db.users.find_one({"_id": ObjectId(by_id)})
                if u: return u, "mongo"
            except Exception:
                return None, "mongo"
        if by_email:
            u = mongo.db.users.find_one({"email": by_email})
            if u: return u, "mongo"
        return None, "mongo"
    else:
        from app.models.user import User
        if by_id:
            try:
                u = User.query.get(int(by_id))
                if u: return u, "sql"
            except Exception:
                return None, "sql"
        if by_email:
            u = User.query.filter_by(email=by_email).first()
            if u: return u, "sql"
        return None, "sql"

def _update_user_role(obj, adapter: str, role: str):
    if adapter == "mongo":
        from app.extensions import mongo
        user_id = obj.get("_id")
        r = mongo.db.users.update_one({"_id": user_id}, {"$set": {"role": role}})
        return r.modified_count == 1
    else:
        from app.extensions import db
        obj.role = role
        db.session.commit()
        return True

@admin_bp.get('/stats')
@jwt_required()
@roles_required('admin')
@admin_ip_required
@limiter.limit("10/minute", key_func=key_user_or_ip)
def stats():
    detail = {"ip": request.headers.get("X-Forwarded-For", request.remote_addr), "path": request.path}
    _audit("stats", "ok", detail)
    return jsonify({"uptime": "ok", "admins_online": 1}), 200

@admin_bp.get('/users')
@jwt_required()
@roles_required('admin')
@admin_ip_required
@limiter.limit("20/minute", key_func=key_user_or_ip)
def list_users_admin():
    db_type = current_app.config.get("DB_TYPE", "mongo")
    if db_type == "mongo":
        from app.extensions import mongo
        users = []
        for u in mongo.db.users.find({}, {"password": 0}):
            u["_id"] = str(u["_id"])
            users.append(u)
    else:
        from app.models.user import User
        users = [{
            "id": u.id, "nome": u.nome, "email": u.email, "role": u.role,
            "created_at": u.created_at.isoformat()
        } for u in User.query.order_by(User.id.asc()).all()]
    _audit("list_users", "ok", {"count": len(users)})
    return jsonify(users), 200

@admin_bp.post('/users/promote')
@jwt_required()
@roles_required('admin')
@admin_ip_required
@limiter.limit("5/minute", key_func=key_user_or_ip)
def promote_user():
    data = request.get_json(silent=True) or {}
    user_id = data.get("user_id"); email = data.get("email"); role = (data.get("role") or "").strip()
    if not user_id and not email:
        _audit("promote", "bad_request", {"reason": "missing user_id/email"})
        return jsonify({"msg": "Informe user_id ou email"}), 400
    if role == "" or not _valid_role(role):
        _audit("promote", "bad_request", {"reason": "invalid role"})
        return jsonify({"msg": "Papel inválido"}), 400
    obj, adapter = _locate_user(user_id, email)
    if not obj:
        _audit("promote", "not_found", {"user_id": user_id, "email": email})
        return jsonify({"msg": "Usuário não encontrado"}), 404
    ok = _update_user_role(obj, adapter, role)
    _audit("promote", "ok" if ok else "failed", {"user_id": user_id, "email": email, "role": role})
    return jsonify({"msg": "Papel atualizado", "role": role}), 200

@admin_bp.post('/users/demote')
@jwt_required()
@roles_required('admin')
@admin_ip_required
@limiter.limit("5/minute", key_func=key_user_or_ip)
def demote_user():
    data = request.get_json(silent=True) or {}
    user_id = data.get("user_id"); email = data.get("email"); role = (data.get("role") or "user").strip()
    if not user_id and not email:
        _audit("demote", "bad_request", {"reason": "missing user_id/email"})
        return jsonify({"msg": "Informe user_id ou email"}), 400
    if role == "" or not _valid_role(role):
        _audit("demote", "bad_request", {"reason": "invalid role"})
        return jsonify({"msg": "Papel inválido"}), 400
    obj, adapter = _locate_user(user_id, email)
    if not obj:
        _audit("demote", "not_found", {"user_id": user_id, "email": email})
        return jsonify({"msg": "Usuário não encontrado"}), 404
    ok = _update_user_role(obj, adapter, role)
    _audit("demote", "ok" if ok else "failed", {"user_id": user_id, "email": email, "role": role})
    return jsonify({"msg": "Papel atualizado", "role": role}), 200
"""), encoding="utf-8")

# ---------- Swagger ----------
(Path(raiz) / "static" / "swagger.yaml").write_text(w("""
openapi: 3.0.0
info:
  title: API Flask Segura v3
  version: 1.0.0
servers:
  - url: /api/v1
paths:
  /auth/register:
    post:
      summary: Registro de usuário
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                nome: { type: string }
                email: { type: string, format: email }
                password: { type: string, format: password }
      responses:
        '201': { description: Usuário criado }
        '400': { description: Erro validação }
  /auth/login:
    post:
      summary: Login
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                email: { type: string, format: email }
                password: { type: string, format: password }
      responses:
        '200': { description: Token JWT }
        '401': { description: Credenciais inválidas }
  /users/:
    get:
      summary: Lista usuários (JWT)
      security: [ { bearerAuth: [] } ]
      responses: { '200': { description: OK } }
  /users/me:
    get:
      summary: Meus dados (JWT)
      security: [ { bearerAuth: [] } ]
      responses: { '200': { description: OK } }
  /d4ta/items/:
    get:
      summary: Lista itens (JWT)
      security: [ { bearerAuth: [] } ]
      responses: { '200': { description: OK } }
    post:
      summary: Cria item (admin)
      security: [ { bearerAuth: [] } ]
      responses: { '201': { description: Criado }, '403': { description: Proibido } }
  /d4ta/items/{id}:
    get:
      summary: Detalhe (JWT)
      security: [ { bearerAuth: [] } ]
      parameters:
        - in: path
          name: id
          required: true
          schema: { type: string }
      responses: { '200': { description: OK }, '404': { description: Não encontrado } }
    put:
      summary: Atualiza (admin)
      security: [ { bearerAuth: [] } ]
      parameters:
        - in: path
          name: id
          required: true
          schema: { type: string }
      responses: { '200': { description: OK }, '403': { description: Proibido } }
    delete:
      summary: Remove (admin)
      security: [ { bearerAuth: [] } ]
      parameters:
        - in: path
          name: id
          required: true
          schema: { type: string }
      responses: { '200': { description: OK }, '403': { description: Proibido } }
  /d4ta/adm-access/stats:
    get:
      summary: Estatísticas admin (JWT + RBAC + IP whitelist)
      security: [ { bearerAuth: [] } ]
      responses: { '200': { description: OK } }
  /d4ta/adm-access/users:
    get:
      summary: Lista usuários (admin + IP whitelist)
      security: [ { bearerAuth: [] } ]
      responses: { '200': { description: OK } }
  /d4ta/adm-access/users/promote:
    post:
      summary: Promove papel (admin + IP whitelist)
      security: [ { bearerAuth: [] } ]
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                user_id: { type: string }
                email: { type: string, format: email }
                role: { type: string, enum: [admin, manager, viewer, user] }
      responses: { '200': { description: OK }, '400': { description: Erro }, '404': { description: Não encontrado } }
  /d4ta/adm-access/users/demote:
    post:
      summary: Rebaixa papel (admin + IP whitelist)
      security: [ { bearerAuth: [] } ]
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                user_id: { type: string }
                email: { type: string, format: email }
                role: { type: string, enum: [admin, manager, viewer, user], default: user }
      responses: { '200': { description: OK }, '400': { description: Erro }, '404': { description: Não encontrado } }
components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
"""), encoding="utf-8")

# ---------- app.py (Talisman, CORS, logs, docs protegidas, métricas) ----------
app_py = f"""
import os, logging
from logging.handlers import RotatingFileHandler
from flask import Flask, jsonify
from flask_cors import CORS
from flask_talisman import Talisman
from flask_swagger_ui import get_swaggerui_blueprint
from app.config import get_config
from app.extensions import {'mongo, ' if db_type=='mongo' else ''}{'db, ' if db_type!='mongo' else ''}jwt, limiter
{"from pymongo import ASCENDING" if db_type=='mongo' else ""}
from flask_jwt_extended import get_jwt
from sentry_sdk.integrations.flask import FlaskIntegration
import sentry_sdk
from prometheus_flask_exporter import PrometheusMetrics

def create_app():
    Config = get_config()
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config["MAX_CONTENT_LENGTH"] = Config.MAX_CONTENT_LENGTH

    if Config.SENTRY_DSN:
        sentry_sdk.init(dsn=Config.SENTRY_DSN, integrations=[FlaskIntegration()], traces_sample_rate=0.2)

    Talisman(app,
             content_security_policy=Config.CONTENT_SECURITY_POLICY,
             force_https=False,  # habilite True atrás de proxy TLS
             strict_transport_security=True,
             strict_transport_security_max_age=Config.HSTS_SECONDS,
             frame_options="DENY",
             referrer_policy="no-referrer")

    CORS(app, resources={{r"{{}}/*".format(Config.API_PREFIX): {{"origins": Config.CORS_ORIGINS}}}}, supports_credentials=True)

    {"mongo.init_app(app)" if db_type=='mongo' else "db.init_app(app)"}
    jwt.init_app(app)
    limiter.init_app(app)

    with app.app_context():
        {"try:\n        mongo.db.users.create_index([('email', ASCENDING)], unique=True)\n        mongo.db.items.create_index([('name', ASCENDING)])\n    except Exception as e:\n        app.logger.warning(f'Falha ao criar índices: {{e}}')" if db_type=='mongo' else "from app.models.user import User\nfrom app.models.item import Item\n        db.create_all()"}

    log_dir = "logs"; os.makedirs(log_dir, exist_ok=True)
    handler = RotatingFileHandler(os.path.join(log_dir, "app.log"), maxBytes=1_000_000, backupCount=5)
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)

    @app.after_request
    def secure_headers(resp):
        resp.headers.pop('Server', None)
        resp.headers['X-Powered-By'] = 'none'
        return resp

    from app.routes.auth_routes import auth_bp
    from app.routes.user_routes import user_bp
    from app.routes.upload_routes import upload_bp
    from app.routes.items_routes import items_bp
    from app.routes.admin_routes import admin_bp

    api = Config.API_PREFIX
    app.register_blueprint(auth_bp, url_prefix=f"{{api}}/auth")
    app.register_blueprint(user_bp, url_prefix=f"{{api}}/users")
    app.register_blueprint(upload_bp, url_prefix=f"{{api}}/d4ta")
    app.register_blueprint(items_bp, url_prefix=f"{{api}}/d4ta/items")
    app.register_blueprint(admin_bp, url_prefix=f"{{api}}/d4ta/adm-access")

    SWAGGER_URL = "/docs"
    API_URL = "/static/swagger.yaml"
    swagger_bp = get_swaggerui_blueprint(SWAGGER_URL, API_URL, config={{"app_name": "API Flask Segura v3"}})

    if app.config.get("DOCS_REQUIRE_ADMIN", True) and not app.config.get("DEBUG", False):
        @swagger_bp.before_request
        def _docs_guard():
            from flask_jwt_extended import verify_jwt_in_request
            try:
                verify_jwt_in_request()
                claims = get_jwt()
                if claims.get("role") != "admin":
                    return jsonify({{"msg": "Docs restritas a admin"}}), 403
            except Exception:
                return jsonify({{"msg": "Auth requerida para docs"}}), 401

    app.register_blueprint(swagger_bp, url_prefix=SWAGGER_URL)

    if app.config.get("PROMETHEUS_METRICS", True):
        PrometheusMetrics(app, group_by='endpoint')

    @app.get("/health")
    def health(): return {{"status":"ok"}}, 200

    @app.errorhandler(404)
    def not_found(e): return jsonify({{"msg":"Rota não encontrada"}}), 404

    @app.errorhandler(413)
    def payload_too_large(e): return jsonify({{"msg":"Payload muito grande"}}), 413

    @app.errorhandler(Exception)
    def handle_exception(e):
        app.logger.exception("Erro inesperado")
        return jsonify({{"msg":"Erro interno do servidor"}}), 500

    @app.get("/")
    def home(): return {{"msg":"API Online"}}, 200

    return app

app = create_app()
if __name__ == "__main__":
    cfg = get_config()
    app.run(debug=getattr(cfg, "DEBUG", False), host=cfg.API_HOST, port=cfg.API_PORT)
"""
(Path(raiz) / "app.py").write_text(w(app_py), encoding="utf-8")

# ---------- Tests básicos ----------
(Path(raiz) / "tests" / "test_basic.py").write_text(w(f"""
from app import app as flask_app

def test_health():
    c = flask_app.test_client()
    r = c.get("/health")
    assert r.status_code == 200
    assert r.get_json().get("status") == "ok"
"""), encoding="utf-8")

(Path(raiz) / "tests" / "test_items_protected.py").write_text(w("""
from app import app as flask_app

def test_items_requires_jwt():
    c = flask_app.test_client()
    r = c.get("/api/v1/d4ta/items/")
    assert r.status_code in (401, 422)  # sem token
"""), encoding="utf-8")

# ---------- Ops ----------
(Path(raiz) / "ops" / "backup_mongo.sh").write_text(w("""
#!/usr/bin/env bash
set -euo pipefail
OUT=${1:-backups/mongo_$(date +%F_%H-%M-%S)}
mkdir -p "$(dirname "$OUT")"
mongodump --uri "$MONGO_URI" --out "$OUT"
echo "Backup Mongo em: $OUT"
"""), encoding="utf-8")
(Path(raiz) / "ops" / "backup_sql.sh").write_text(w("""
#!/usr/bin/env bash
set -euo pipefail
OUT=${1:-backups/sql_$(date +%F_%H-%M-%S).sql}
mkdir -p "$(dirname "$OUT")"
if [[ "$DB_TYPE" == "mariadb" ]]; then
  mysqldump -h "$SQL_HOST" -u "$SQL_USER" -p"$SQL_PASS" "$SQL_DB" > "$OUT"
else
  PGPASSWORD="$SQL_PASS" pg_dump -h "$SQL_HOST" -U "$SQL_USER" -d "$SQL_DB" -F p > "$OUT"
fi
echo "Backup SQL em: $OUT"
"""), encoding="utf-8")
(Path(raiz) / "ops" / "audit.sh").write_text(w("""
#!/usr/bin/env bash
set -euo pipefail
pip freeze > requirements.lock
pip-audit
"""), encoding="utf-8")

# ---------- Virtualenv opcional ----------
def create_and_install_venv(project_dir: str):
    print("\nCriando virtualenv (.venv) e instalando dependências...")
    py = sys.executable
    venv_dir = Path(project_dir, ".venv")
    subprocess.check_call([py, "-m", "venv", str(venv_dir)])
    if platform.system().lower().startswith("win"):
        pip_path = str(venv_dir / "Scripts" / "pip.exe")
        python_path = str(venv_dir / "Scripts" / "python.exe")
    else:
        pip_path = str(venv_dir / "bin" / "pip")
        python_path = str(venv_dir / "bin" / "python")
    subprocess.check_call([pip_path, "install", "-r", str(Path(project_dir, "requirements.txt"))])
    return python_path

use_venv = (input("Criar e usar virtualenv automaticamente? [S/n]: ") or "S").strip().lower() != "n"
venv_python = None
if use_venv:
    try:
        venv_python = create_and_install_venv(raiz)
    except Exception as e:
        print(f"Não foi possível criar venv automaticamente: {e}")
        print("Instalando com pip global...")
        subprocess.call([sys.executable, "-m", "pip", "install", "-r", f"{raiz}/requirements.txt"])
else:
    print("Instalando dependências com pip global...")
    subprocess.call([sys.executable, "-m", "pip", "install", "-r", f"{raiz}/requirements.txt"])

print("\n✔ Estrutura criada com sucesso em:", raiz)
print(w(f"""
Como rodar:

1) cd {raiz}

2) Ajuste o .env (JWT_SECRET_KEY, CORS_ORIGENS, ADMIN_IP_WHITELIST, DB_URI...)

3) Rodar local (dev):
   {"python app.py" if not venv_python else f"{venv_python} app.py"}

4) Docker (prod com gunicorn):
   docker-compose up --build

5) Swagger:
   http://localhost:{api_port}/docs
   (em produção, exige JWT admin por padrão)

CRUD items:
- GET    /api/v1/d4ta/items/           (jwt)
- GET    /api/v1/d4ta/items/<id>       (jwt)
- POST   /api/v1/d4ta/items/           (admin)
- PUT    /api/v1/d4ta/items/<id>       (admin)
- DELETE /api/v1/d4ta/items/<id>       (admin)

Admin seguro:
- GET  /api/v1/d4ta/adm-access/stats
- GET  /api/v1/d4ta/adm-access/users
- POST /api/v1/d4ta/adm-access/users/promote  {{ user_id|email, role }}
- POST /api/v1/d4ta/adm-access/users/demote   {{ user_id|email, role?=user }}

Dicas:
- Promova o primeiro admin direto no banco (campo role='admin').
- Garanta seu IP em ADMIN_IP_WHITELIST antes de chamar rotas admin.
- Para cookies JWT + CSRF, defina JWT_IN_COOKIES=true (Flask-JWT-Extended já cuida do CSRF).
- Para HTTPS real, suba o NGINX com certificados em nginx/certs.
"""))
