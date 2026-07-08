# app.py - Sistema de Gestão de Segurança - Shopping Center
# Corrigido para Railway: drop_all/create_all, Historico.data como String, endpoints async com request.json()

import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from sqlalchemy import (
    create_engine, Column, Integer, String, Text, Boolean,
)
from sqlalchemy.orm import sessionmaker, declarative_base
import uvicorn

# -----------------------------------------------------------------------------
# Configuração
# -----------------------------------------------------------------------------
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./seguranca.db")
# Railway entrega postgres://, SQLAlchemy precisa de postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

PORT = int(os.environ.get("PORT", 8000))

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# -----------------------------------------------------------------------------
# Modelos
# -----------------------------------------------------------------------------

class Extintor(Base):
    __tablename__ = "extintores"
    id = Column(Integer, primary_key=True, autoincrement=True)
    numero_extintor = Column(String, default="")
    patrimonio = Column(String, default="")
    classe_incendio = Column(String, default="")
    tipo = Column(String, default="")
    capacidade = Column(String, default="")
    fabricante = Column(String, default="")
    numero_serie = Column(String, default="")
    data_fabricacao = Column(String, default="")
    data_teste_hidrostatico = Column(String, default="")
    data_validade = Column(String, default="")
    localizacao = Column(String, default="")
    pavimento = Column(String, default="")
    setor = Column(String, default="")
    situacao = Column(String, default="")
    status = Column(String, default="")
    observacoes = Column(Text, default="")


class Mangueira(Base):
    __tablename__ = "mangueiras"
    id = Column(Integer, primary_key=True, autoincrement=True)
    numero_mangueira = Column(String, default="")
    tipo = Column(String, default="")
    comprimento = Column(String, default="")
    diametro = Column(String, default="")
    fabricante = Column(String, default="")
    data_fabricacao = Column(String, default="")
    data_ultimo_ensaio = Column(String, default="")
    data_validade = Column(String, default="")
    abrigo_hidrante = Column(String, default="")
    situacao = Column(String, default="")
    status = Column(String, default="")
    observacoes = Column(Text, default="")


class VGA(Base):
    __tablename__ = "vgas"
    id = Column(Integer, primary_key=True, autoincrement=True)
    numero_vga = Column(String, default="")
    localizacao = Column(String, default="")
    pavimento = Column(String, default="")
    vazao = Column(String, default="")
    pressao = Column(String, default="")
    data_ultima_inspecao = Column(String, default="")
    situacao = Column(String, default="")
    status = Column(String, default="")
    observacoes = Column(Text, default="")


class Abrigo(Base):
    __tablename__ = "abrigos"
    id = Column(Integer, primary_key=True, autoincrement=True)
    codigo_abrigo = Column(String, default="")
    localizacao = Column(String, default="")
    pavimento = Column(String, default="")
    setor = Column(String, default="")
    tem_mangueira = Column(String, default="")
    mangueira_alocada = Column(String, default="")
    tem_chave_storz = Column(String, default="")
    chave_storz_alocada = Column(String, default="")
    tem_esguicho = Column(String, default="")
    esguicho_alocada = Column(String, default="")
    tem_tampao = Column(String, default="")
    tampao_alocada = Column(String, default="")
    tem_reducao = Column(String, default="")
    reducao_alocada = Column(String, default="")
    tem_adaptadores = Column(String, default="")
    adaptadores_alocados = Column(String, default="")
    tem_registro = Column(String, default="")
    registro_status = Column(String, default="")
    tem_sinalizacao = Column(String, default="")
    observacoes = Column(Text, default="")


class OutroEquipamento(Base):
    __tablename__ = "outros_equipamentos"
    id = Column(Integer, primary_key=True, autoincrement=True)
    tipo_equipamento = Column(String, default="")
    patrimonio = Column(String, default="")
    localizacao = Column(String, default="")
    data_validade = Column(String, default="")
    situacao = Column(String, default="")
    status = Column(String, default="")
    observacoes = Column(Text, default="")


class KitCrise(Base):
    __tablename__ = "kits_crise"
    id = Column(Integer, primary_key=True, autoincrement=True)
    item = Column(String, default="")
    quantidade = Column(String, default="")
    localizacao = Column(String, default="")
    responsavel = Column(String, default="")
    situacao = Column(String, default="")
    validade = Column(String, default="")


class SDAI(Base):
    __tablename__ = "sdais"
    id = Column(Integer, primary_key=True, autoincrement=True)
    codigo = Column(String, default="")
    central_alarme = Column(String, default="")
    acionadores_manuais = Column(String, default="")
    detectores = Column(String, default="")
    sirenes = Column(String, default="")
    modulos = Column(String, default="")
    fontes = Column(String, default="")
    baterias = Column(String, default="")
    loop = Column(String, default="")
    enderecamento = Column(String, default="")
    data_ultimo_teste = Column(String, default="")
    falhas = Column(Text, default="")
    observacoes = Column(Text, default="")


class CFTV(Base):
    __tablename__ = "cftvs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    codigo = Column(String, default="")
    tipo = Column(String, default="")
    marca = Column(String, default="")
    modelo = Column(String, default="")
    ip = Column(String, default="")
    localizacao = Column(String, default="")
    estado = Column(String, default="")
    garantia = Column(String, default="")
    data_manutencao = Column(String, default="")
    observacoes = Column(Text, default="")


class Loja(Base):
    __tablename__ = "lojas"
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome_loja = Column(String, default="")
    numero = Column(String, default="")
    segmento = Column(String, default="")
    responsavel = Column(String, default="")
    telefone = Column(String, default="")
    email = Column(String, default="")
    hidrantes = Column(String, default="")
    problemas_encontrados = Column(Text, default="")
    data_vistoria = Column(String, default="")
    grau_risco = Column(String, default="")
    observacoes = Column(Text, default="")


class Escada(Base):
    __tablename__ = "escadas"
    id = Column(Integer, primary_key=True, autoincrement=True)
    codigo = Column(String, default="")
    pavimento = Column(String, default="")
    quantidade_portas = Column(Integer, default=0)
    barra_antipanico = Column(String, default="")
    fechadura = Column(String, default="")
    molas = Column(String, default="")
    sinalizacao = Column(String, default="")
    situacao = Column(String, default="")
    data_inspecao = Column(String, default="")
    observacoes = Column(Text, default="")


class Tarefa(Base):
    __tablename__ = "tarefas"
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String, default="")
    descricao = Column(Text, default="")
    prioridade = Column(String, default="")
    categoria = Column(String, default="")
    vencimento = Column(String, default="")
    responsavel = Column(String, default="")
    resolvido = Column(Boolean, default=False)
    criado_em = Column(String, default=lambda: datetime.now().isoformat())
    concluido_em = Column(String, nullable=True)


class Time(Base):
    __tablename__ = "times"
    id = Column(Integer, primary_key=True, autoincrement=True)
    categoria = Column(String, default="")
    nome = Column(String, default="")
    cargo = Column(String, default="")
    empresa = Column(String, default="")
    certificados = Column(String, default="")
    data_validade_certificado = Column(String, default="")
    telefone = Column(String, default="")
    email = Column(String, default="")
    escala = Column(String, default="")
    observacoes = Column(Text, default="")


class Documento(Base):
    __tablename__ = "documentos"
    id = Column(Integer, primary_key=True, autoincrement=True)
    titulo = Column(String, default="")
    tipo = Column(String, default="")
    data_emissao = Column(String, default="")
    data_validade = Column(String, default="")
    orgao_emissor = Column(String, default="")
    arquivo_url = Column(String, default="")
    observacoes = Column(Text, default="")


class Ocorrencia(Base):
    __tablename__ = "ocorrencias"
    id = Column(Integer, primary_key=True, autoincrement=True)
    tipo = Column(String, default="")
    data = Column(String, default="")
    hora = Column(String, default="")
    local = Column(String, default="")
    descricao = Column(Text, default="")
    responsavel = Column(String, default="")
    providencias = Column(Text, default="")
    status = Column(String, default="")


class Contato(Base):
    __tablename__ = "contatos"
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String, default="")
    telefone = Column(String, default="")
    email = Column(String, default="")
    empresa = Column(String, default="")
    funcao = Column(String, default="")
    observacoes = Column(Text, default="")


class Historico(Base):
    __tablename__ = "historicos"
    id = Column(Integer, primary_key=True, autoincrement=True)
    modulo = Column(String, default="")
    item_id = Column(Integer, default=0)
    acao = Column(String, default="")
    data = Column(String, default=lambda: datetime.now().isoformat())
    observacoes = Column(Text, default="")


# -----------------------------------------------------------------------------
# Mapeamento de módulos
# -----------------------------------------------------------------------------
MODULES = {
    "extintores": Extintor,
    "mangueiras": Mangueira,
    "vgas": VGA,
    "abrigos": Abrigo,
    "outros_equipamentos": OutroEquipamento,
    "kits_crise": KitCrise,
    "sdais": SDAI,
    "cftvs": CFTV,
    "lojas": Loja,
    "escadas": Escada,
    "tarefas": Tarefa,
    "times": Time,
    "documentos": Documento,
    "ocorrencias": Ocorrencia,
    "contatos": Contato,
}

DUPLICABLE = {"extintores", "mangueiras", "outros_equipamentos"}

# -----------------------------------------------------------------------------
# App
# -----------------------------------------------------------------------------
app = FastAPI(title="Gestão de Segurança - Shopping Center")


@app.on_event("startup")
def on_startup():
    # CORREÇÃO 1: drop_all ANTES de create_all para garantir schema novo
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def model_to_dict(obj: Any) -> Dict[str, Any]:
    # CORREÇÃO 4: retornar valores crus sem forçar conversão de datetime
    result = {}
    for col in obj.__table__.columns:
        result[col.name] = getattr(obj, col.name)
    return result


def registrar_historico(db, modulo: str, item_id: int, acao: str, observacoes: str = ""):
    try:
        h = Historico(modulo=modulo, item_id=item_id, acao=acao, observacoes=observacoes)
        db.add(h)
        db.commit()
    except Exception:
        db.rollback()


# -----------------------------------------------------------------------------
# Endpoints genéricos por módulo
# -----------------------------------------------------------------------------

def build_router(modulo: str, model):
    @app.get(f"/api/{modulo}")
    async def list_items(status: Optional[str] = Query(None)):
        db = SessionLocal()
        try:
            q = db.query(model)
            if status and hasattr(model, "status"):
                q = q.filter(model.status == status)
            items = q.all()
            return [model_to_dict(i) for i in items]
        finally:
            db.close()

    @app.post(f"/api/{modulo}")
    async def create_item(request: Request):
        db = SessionLocal()
        try:
            data = await request.json()
            obj = model()
            for key, value in data.items():
                if hasattr(obj, key):
                    setattr(obj, key, value)
            db.add(obj)
            db.commit()
            db.refresh(obj)
            registrar_historico(db, modulo, obj.id, "criacao")
            return model_to_dict(obj)
        except Exception as e:
            db.rollback()
            return JSONResponse({"error": str(e)}, status_code=400)
        finally:
            db.close()

    @app.put(f"/api/{modulo}/{{item_id}}")
    async def update_item(item_id: int, request: Request):
        db = SessionLocal()
        try:
            data = await request.json()
            obj = db.query(model).filter(model.id == item_id).first()
            if not obj:
                return JSONResponse({"error": "não encontrado"}, status_code=404)
            for key, value in data.items():
                if hasattr(obj, key):
                    setattr(obj, key, value)
            db.commit()
            db.refresh(obj)
            registrar_historico(db, modulo, obj.id, "atualizacao")
            return model_to_dict(obj)
        except Exception as e:
            db.rollback()
            return JSONResponse({"error": str(e)}, status_code=400)
        finally:
            db.close()

    @app.delete(f"/api/{modulo}/{{item_id}}")
    async def delete_item(item_id: int):
        db = SessionLocal()
        try:
            obj = db.query(model).filter(model.id == item_id).first()
            if not obj:
                return JSONResponse({"error": "não encontrado"}, status_code=404)
            db.delete(obj)
            db.commit()
            registrar_historico(db, modulo, item_id, "exclusao")
            return {"ok": True}
        except Exception as e:
            db.rollback()
            return JSONResponse({"error": str(e)}, status_code=400)
        finally:
            db.close()

    if modulo in DUPLICABLE:
        @app.post(f"/api/{modulo}/{{item_id}}/duplicar")
        async def duplicate_item(item_id: int):
            db = SessionLocal()
            try:
                obj = db.query(model).filter(model.id == item_id).first()
                if not obj:
                    return JSONResponse({"error": "não encontrado"}, status_code=404)
                novo = model()
                for col in obj.__table__.columns:
                    if col.name == "id":
                        continue
                    setattr(novo, col.name, getattr(obj, col.name))
                db.add(novo)
                db.commit()
                db.refresh(novo)
                registrar_historico(db, modulo, novo.id, "duplicacao")
                return model_to_dict(novo)
            except Exception as e:
                db.rollback()
                return JSONResponse({"error": str(e)}, status_code=400)
            finally:
                db.close()


for modulo, model in MODULES.items():
    build_router(modulo, model)


# -----------------------------------------------------------------------------
# Dashboard e Alertas
# -----------------------------------------------------------------------------
@app.get("/api/dashboard")
async def dashboard():
    db = SessionLocal()
    try:
        stats = {}
        for modulo, model in MODULES.items():
            try:
                stats[modulo] = db.query(model).count()
            except Exception:
                stats[modulo] = 0
        # Alertas de vencimento
        alertas = []
        hoje = datetime.now().strftime("%Y-%m-%d")
        for modulo, model in MODULES.items():
            if hasattr(model, "data_validade"):
                try:
                    items = db.query(model).filter(model.data_validade != "", model.data_validade != None).all()
                    for it in items:
                        dv = (it.data_validade or "")[:10]
                        if dv and dv <= hoje:
                            alertas.append({
                                "modulo": modulo,
                                "id": it.id,
                                "data_validade": it.data_validade,
                                "descricao": f"{modulo} #{it.id} vencido em {it.data_validade}",
                            })
                except Exception:
                    pass
        # Últimas movimentações
        try:
            hist = db.query(Historico).order_by(Historico.id.desc()).limit(10).all()
            movimentacoes = [model_to_dict(h) for h in hist]
        except Exception:
            movimentacoes = []
        return {"stats": stats, "alertas": alertas, "movimentacoes": movimentacoes}
    finally:
        db.close()


@app.get("/api/alertas")
async def alertas():
    db = SessionLocal()
    try:
        alertas = []
        hoje = datetime.now().strftime("%Y-%m-%d")
        for modulo, model in MODULES.items():
            if hasattr(model, "data_validade"):
                try:
                    items = db.query(model).filter(model.data_validade != "", model.data_validade != None).all()
                    for it in items:
                        dv = (it.data_validade or "")[:10]
                        if dv and dv <= hoje:
                            alertas.append({
                                "modulo": modulo,
                                "id": it.id,
                                "data_validade": it.data_validade,
                                "descricao": f"{modulo} #{it.id} vencido em {it.data_validade}",
                            })
                except Exception:
                    pass
        return alertas
    finally:
        db.close()


@app.get("/api/historicos")
async def listar_historicos():
    db = SessionLocal()
    try:
        hist = db.query(Historico).order_by(Historico.id.desc()).limit(50).all()
        return [model_to_dict(h) for h in hist]
    finally:
        db.close()


# -----------------------------------------------------------------------------
# Rota raiz - HTML
# -----------------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def index():
    return HTML_CONTENT


# -----------------------------------------------------------------------------
# HTML Frontend
# -----------------------------------------------------------------------------
HTML_CONTENT = r'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Gestão de Segurança - Shopping Center</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
<link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css" rel="stylesheet">
<style>
  body { background:#f1f5f9; }
  .header-bg { background: linear-gradient(135deg,#0f172a,#1e3a5f); color:#fff; padding:18px 20px; }
  .header-bg h1 { margin:0; font-size:1.5rem; font-weight:700; }
  .nav-tabs-scroll { overflow-x:auto; white-space:nowrap; background:#fff; border-bottom:1px solid #e2e8f0; }
  .nav-tabs-scroll .nav-link { display:inline-block; border-radius:0; color:#475569; font-weight:600; padding:12px 18px; }
  .nav-tabs-scroll .nav-link.active { color:#1e3a5f; border-bottom:3px solid #1e3a5f; background:transparent; }
  .kpi-card { border:none; border-radius:12px; box-shadow:0 1px 3px rgba(0,0,0,.08); }
  .kpi-card .card-body { padding:18px; }
  .kpi-num { font-size:1.8rem; font-weight:800; color:#1e3a5f; }
  .kpi-label { color:#64748b; font-size:.85rem; text-transform:uppercase; letter-spacing:.05em; }
  .module-card { border:none; border-radius:12px; box-shadow:0 1px 3px rgba(0,0,0,.08); }
  .table thead th { background:#f8fafc; color:#475569; font-size:.8rem; text-transform:uppercase; letter-spacing:.04em; }
  .btn-sec { background:#1e3a5f; color:#fff; }
  .btn-sec:hover { background:#0f172a; color:#fff; }
  .alert-item { border-left:4px solid #dc2626; }
  .badge-status { font-size:.75rem; }
  .tab-content { padding:20px; }
  .modal-body { max-height:70vh; overflow-y:auto; }
</style>
</head>
<body>
<div class="header-bg">
  <h1>🛡️ Gestão de Segurança - Shopping Center</h1>
</div>

<ul class="nav nav-tabs nav-tabs-scroll" id="mainTabs" role="tablist">
  <li class="nav-item"><button class="nav-link active" data-tab="painel">PAINEL</button></li>
  <li class="nav-item"><button class="nav-link" data-tab="extintores">Extintores</button></li>
  <li class="nav-item"><button class="nav-link" data-tab="mangueiras">Mangueiras</button></li>
  <li class="nav-item"><button class="nav-link" data-tab="vgas">VGAs</button></li>
  <li class="nav-item"><button class="nav-link" data-tab="abrigos">Abrigos</button></li>
  <li class="nav-item"><button class="nav-link" data-tab="outros_equipamentos">Outros Equip.</button></li>
  <li class="nav-item"><button class="nav-link" data-tab="kits_crise">Kit Crise</button></li>
  <li class="nav-item"><button class="nav-link" data-tab="sdais">SDAI</button></li>
  <li class="nav-item"><button class="nav-link" data-tab="cftvs">CFTV</button></li>
  <li class="nav-item"><button class="nav-link" data-tab="lojas">Lojas</button></li>
  <li class="nav-item"><button class="nav-link" data-tab="escadas">Escadas</button></li>
  <li class="nav-item"><button class="nav-link" data-tab="tarefas">Tarefas</button></li>
  <li class="nav-item"><button class="nav-link" data-tab="times">Times</button></li>
  <li class="nav-item"><button class="nav-link" data-tab="documentos">Documentos</button></li>
  <li class="nav-item"><button class="nav-link" data-tab="ocorrencias">Ocorrências</button></li>
  <li class="nav-item"><button class="nav-link" data-tab="contatos">Contatos</button></li>
</ul>

<div class="tab-content" id="tabContent">
  <div id="content-area"></div>
</div>

<!-- Modal -->
<div class="modal fade" id="formModal" tabindex="-1">
  <div class="modal-dialog modal-lg modal-dialog-scrollable">
    <div class="modal-content">
      <div class="modal-header bg-dark text-white">
        <h5 class="modal-title" id="modalTitle">Formulário</h5>
        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
      </div>
      <div class="modal-body">
        <form id="dynamicForm"></form>
      </div>
      <div class="modal-footer">
        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
        <button type="button" class="btn btn-sec" onclick="saveItem()">Salvar</button>
      </div>
    </div>
  </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
<script>
const MODULES_META = {
  extintores: {icon:"🧯", label:"Extintores", dup:true},
  mangueiras: {icon:"🚒", label:"Mangueiras", dup:true},
  vgas: {icon:"💧", label:"VGAs", dup:false},
  abrigos: {icon:"📦", label:"Abrigos", dup:false},
  outros_equipamentos: {icon:"🛠️", label:"Outros Equipamentos", dup:true},
  kits_crise: {icon:"🆘", label:"Kit Crise", dup:false},
  sdais: {icon:"🚨", label:"SDAI", dup:false},
  cftvs: {icon:"📹", label:"CFTV", dup:false},
  lojas: {icon:"🏬", label:"Lojas", dup:false},
  escadas: {icon:"🪜", label:"Escadas", dup:false},
  tarefas: {icon:"✅", label:"Tarefas", dup:false},
  times: {icon:"👥", label:"Times", dup:false},
  documentos: {icon:"📄", label:"Documentos", dup:false},
  ocorrencias: {icon:"⚠️", label:"Ocorrências", dup:false},
  contatos: {icon:"📇", label:"Contatos", dup:false}
};

let currentTab = "painel";
let editingId = null;
let editingModule = null;

function api(modulo){ return "/api/" + modulo; }

async function apiGet(url){
  const r = await fetch(url);
  return await r.json();
}
async function apiSend(url, method, data){
  const r = await fetch(url, {
    method: method,
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify(data)
  });
  return await r.json();
}

function esc(v){ return (v===null||v===undefined)?"":String(v); }

function selectOpts(options, selected){
  let s = "<option value=''>Selecione...</option>";
  options.forEach(o=>{
    s += `<option value="${o}" ${selected===o?"selected":""}>${o}</option>`;
  });
  return s;
}

function field(label, name, type="text", value="", extra=""){
  return `<div class="mb-3"><label class="form-label fw-semibold">${label}</label><input type="${type}" class="form-control" id="f_${name}" value="${esc(value)}" ${extra}></div>`;
}
function textareaField(label, name, value=""){
  return `<div class="mb-3"><label class="form-label fw-semibold">${label}</label><textarea class="form-control" id="f_${name}" rows="3">${esc(value)}</textarea></div>`;
}
function selectField(label, name, options, value=""){
  return `<div class="mb-3"><label class="form-label fw-semibold">${label}</label><select class="form-select" id="f_${name}">${selectOpts(options, value)}</select></div>`;
}
function checkField(label, name, checked=false){
  return `<div class="mb-3 form-check"><input type="checkbox" class="form-check-input" id="f_${name}" ${checked?"checked":""}><label class="form-check-label fw-semibold" for="f_${name}">${label}</label></div>`;
}

function generateFormHTML(modulo, item){
  const v = item || {};
  let html = "";
  if(modulo==="extintores"){
    html += field("Número Extintor","numero_extintor","text",v.numero_extintor);
    html += field("Patrimônio","patrimonio","text",v.patrimonio);
    html += selectField("Classe Incêndio","classe_incendio",["A","B","C","D","K","ABC","BC","Lítio"],v.classe_incendio);
    html += selectField("Tipo","tipo",["CO2","Pó Químico","Água","Espuma"],v.tipo);
    html += field("Capacidade","capacidade","text",v.capacidade);
    html += field("Fabricante","fabricante","text",v.fabricante);
    html += field("Número Série","numero_serie","text",v.numero_serie);
    html += field("Data Fabricação","data_fabricacao","date",v.data_fabricacao);
    html += field("Data Teste Hidrostático","data_teste_hidrostatico","date",v.data_teste_hidrostatico);
    html += field("Data Validade","data_validade","date",v.data_validade);
    html += field("Localização","localizacao","text",v.localizacao);
    html += field("Pavimento","pavimento","text",v.pavimento);
    html += field("Setor","setor","text",v.setor);
    html += selectField("Situação","situacao",["Conforme","Não Conforme","Inspecionar"],v.situacao);
    html += selectField("Status","status",["Disponível","Alocado","Em Manutenção","Inativo"],v.status);
    html += textareaField("Observações","observacoes",v.observacoes);
  } else if(modulo==="mangueiras"){
    html += field("Número Mangueira","numero_mangueira","text",v.numero_mangueira);
    html += selectField("Tipo","tipo",["1 polegada","1.5 pol","2 pol"],v.tipo);
    html += field("Comprimento","comprimento","text",v.comprimento);
    html += field("Diâmetro","diametro","text",v.diametro);
    html += field("Fabricante","fabricante","text",v.fabricante);
    html += field("Data Fabricação","data_fabricacao","date",v.data_fabricacao);
    html += field("Data Último Ensaio","data_ultimo_ensaio","date",v.data_ultimo_ensaio);
    html += field("Data Validade","data_validade","date",v.data_validade);
    html += field("Abrigo Hidrante","abrigo_hidrante","text",v.abrigo_hidrante);
    html += selectField("Situação","situacao",["Conforme","Não Conforme","Inspecionar"],v.situacao);
    html += selectField("Status","status",["Disponível","Alocado","Em Manutenção","Inativo"],v.status);
    html += textareaField("Observações","observacoes",v.observacoes);
  } else if(modulo==="vgas"){
    html += field("Número VGA","numero_vga","text",v.numero_vga);
    html += field("Localização","localizacao","text",v.localizacao);
    html += field("Pavimento","pavimento","text",v.pavimento);
    html += field("Vazão","vazao","text",v.vazao);
    html += field("Pressão","pressao","text",v.pressao);
    html += field("Data Última Inspeção","data_ultima_inspecao","date",v.data_ultima_inspecao);
    html += field("Situação","situacao","text",v.situacao);
    html += field("Status","status","text",v.status);
    html += textareaField("Observações","observacoes",v.observacoes);
  } else if(modulo==="abrigos"){
    html += field("Código Abrigo","codigo_abrigo","text",v.codigo_abrigo);
    html += field("Localização","localizacao","text",v.localizacao);
    html += field("Pavimento","pavimento","text",v.pavimento);
    html += field("Setor","setor","text",v.setor);
    html += selectField("Tem Mangueira","tem_mangueira",["sim","não"],v.tem_mangueira);
    html += field("Mangueira Alocada","mangueira_alocada","text",v.mangueira_alocada);
    html += selectField("Tem Chave Storz","tem_chave_storz",["sim","não"],v.tem_chave_storz);
    html += field("Chave Storz Alocada","chave_storz_alocada","text",v.chave_storz_alocada);
    html += selectField("Tem Esguicho","tem_esguicho",["sim","não"],v.tem_esguicho);
    html += field("Esguicho Alocada","esguicho_alocada","text",v.esguicho_alocada);
    html += selectField("Tem Tampão","tem_tampao",["sim","não"],v.tem_tampao);
    html += field("Tampão Alocada","tampao_alocada","text",v.tampao_alocada);
    html += selectField("Tem Redução","tem_reducao",["sim","não"],v.tem_reducao);
    html += field("Redução Alocada","reducao_alocada","text",v.reducao_alocada);
    html += selectField("Tem Adaptadores","tem_adaptadores",["sim","não"],v.tem_adaptadores);
    html += field("Adaptadores Alocados","adaptadores_alocados","text",v.adaptadores_alocados);
    html += selectField("Tem Registro","tem_registro",["sim","não"],v.tem_registro);
    html += field("Registro Status","registro_status","text",v.registro_status);
    html += selectField("Tem Sinalização","tem_sinalizacao",["Conforme","Não Conforme","Inexistente"],v.tem_sinalizacao);
    html += textareaField("Observações","observacoes",v.observacoes);
  } else if(modulo==="outros_equipamentos"){
    html += field("Tipo Equipamento","tipo_equipamento","text",v.tipo_equipamento);
    html += field("Patrimônio","patrimonio","text",v.patrimonio);
    html += field("Localização","localizacao","text",v.localizacao);
    html += field("Data Validade","data_validade","date",v.data_validade);
    html += field("Situação","situacao","text",v.situacao);
    html += selectField("Status","status",["Disponível","Alocado","Em Manutenção","Inativo"],v.status);
    html += textareaField("Observações","observacoes",v.observacoes);
  } else if(modulo==="kits_crise"){
    html += field("Item","item","text",v.item);
    html += field("Quantidade","quantidade","text",v.quantidade);
    html += field("Localização","localizacao","text",v.localizacao);
    html += field("Responsável","responsavel","text",v.responsavel);
    html += selectField("Situação","situacao",["OK","Repor","Vencido"],v.situacao);
    html += field("Validade","validade","date",v.validade);
  } else if(modulo==="sdais"){
    html += field("Código","codigo","text",v.codigo);
    html += field("Central Alarme","central_alarme","text",v.central_alarme);
    html += field("Acionadores Manuais","acionadores_manuais","text",v.acionadores_manuais);
    html += field("Detectores","detectores","text",v.detectores);
    html += field("Sirenes","sirenes","text",v.sirenes);
    html += field("Módulos","modulos","text",v.modulos);
    html += field("Fontes","fontes","text",v.fontes);
    html += field("Baterias","baterias","text",v.baterias);
    html += field("Loop","loop","text",v.loop);
    html += field("Endereçamento","enderecamento","text",v.enderecamento);
    html += field("Data Último Teste","data_ultimo_teste","date",v.data_ultimo_teste);
    html += textareaField("Falhas","falhas",v.falhas);
    html += textareaField("Observações","observacoes",v.observacoes);
  } else if(modulo==="cftvs"){
    html += field("Código","codigo","text",v.codigo);
    html += selectField("Tipo","tipo",["Câmera","DVR","Monitor"],v.tipo);
    html += field("Marca","marca","text",v.marca);
    html += field("Modelo","modelo","text",v.modelo);
    html += field("IP","ip","text",v.ip);
    html += field("Localização","localizacao","text",v.localizacao);
    html += selectField("Estado","estado",["Ativo","Inativo","Manutenção"],v.estado);
    html += field("Garantia","garantia","text",v.garantia);
    html += field("Data Manutenção","data_manutencao","date",v.data_manutencao);
    html += textareaField("Observações","observacoes",v.observacoes);
  } else if(modulo==="lojas"){
    html += field("Nome Loja","nome_loja","text",v.nome_loja);
    html += field("Número","numero","text",v.numero);
    html += field("Segmento","segmento","text",v.segmento);
    html += field("Responsável","responsavel","text",v.responsavel);
    html += field("Telefone","telefone","text",v.telefone);
    html += field("Email","email","text",v.email);
    html += field("Hidrantes","hidrantes","text",v.hidrantes);
    html += textareaField("Problemas Encontrados","problemas_encontrados",v.problemas_encontrados);
    html += field("Data Vistoria","data_vistoria","date",v.data_vistoria);
    html += selectField("Grau Risco","grau_risco",["Risco 01","Risco 02","Risco 03","Risco 04"],v.grau_risco);
    html += textareaField("Observações","observacoes",v.observacoes);
  } else if(modulo==="escadas"){
    html += field("Código","codigo","text",v.codigo);
    html += field("Pavimento","pavimento","text",v.pavimento);
    html += field("Quantidade Portas","quantidade_portas","number",v.quantidade_portas||0);
    html += selectField("Barra Antipânico","barra_antipanico",["Conforme","Não Conforme"],v.barra_antipanico);
    html += selectField("Fechadura","fechadura",["Conforme","Não Conforme"],v.fechadura);
    html += selectField("Molas","molas",["Conforme","Não Conforme"],v.molas);
    html += selectField("Sinalização","sinalizacao",["Conforme","Não Conforme","Inexistente"],v.sinalizacao);
    html += field("Situação","situacao","text",v.situacao);
    html += field("Data Inspeção","data_inspecao","date",v.data_inspecao);
    html += textareaField("Observações","observacoes",v.observacoes);
  } else if(modulo==="tarefas"){
    html += field("Nome","nome","text",v.nome);
    html += textareaField("Descrição","descricao",v.descricao);
    html += selectField("Prioridade","prioridade",["Baixa","Média","Alta"],v.prioridade);
    html += selectField("Categoria","categoria",["Trabalho","Pessoal","Estudo","Saúde","Finanças","Outros"],v.categoria);
    html += field("Vencimento","vencimento","date",v.vencimento);
    html += field("Responsável","responsavel","text",v.responsavel);
    html += checkField("Resolvido","resolvido",v.resolvido===true||v.resolvido==="true");
  } else if(modulo==="times"){
    html += selectField("Categoria","categoria",["Interno","Terceiro"],v.categoria);
    html += field("Nome","nome","text",v.nome);
    html += field("Cargo","cargo","text",v.cargo);
    html += field("Empresa","empresa","text",v.empresa);
    html += field("Certificados","certificados","text",v.certificados);
    html += field("Data Validade Certificado","data_validade_certificado","date",v.data_validade_certificado);
    html += field("Telefone","telefone","text",v.telefone);
    html += field("Email","email","text",v.email);
    html += field("Escala","escala","text",v.escala);
    html += textareaField("Observações","observacoes",v.observacoes);
  } else if(modulo==="documentos"){
    html += field("Título","titulo","text",v.titulo);
    html += selectField("Tipo","tipo",["Alvará","LVCB","AVCB","Certificado Brigada","Laudo Técnico","Seguro","Contrato","Outros"],v.tipo);
    html += field("Data Emissão","data_emissao","date",v.data_emissao);
    html += field("Data Validade","data_validade","date",v.data_validade);
    html += field("Órgão Emissor","orgao_emissor","text",v.orgao_emissor);
    html += field("Arquivo URL","arquivo_url","text",v.arquivo_url);
    html += textareaField("Observações","observacoes",v.observacoes);
  } else if(modulo==="ocorrencias"){
    html += selectField("Tipo","tipo",["Incêndio","Princípio Incêndio","Vazamento","Alarme Falso","Emergência Médica","Outros"],v.tipo);
    html += field("Data","data","date",v.data);
    html += field("Hora","hora","time",v.hora);
    html += field("Local","local","text",v.local);
    html += textareaField("Descrição","descricao",v.descricao);
    html += field("Responsável","responsavel","text",v.responsavel);
    html += textareaField("Providências","providencias",v.providencias);
    html += selectField("Status","status",["Aberto","Em Andamento","Resolvido"],v.status);
  } else if(modulo==="contatos"){
    html += field("Nome","nome","text",v.nome);
    html += field("Telefone","telefone","text",v.telefone);
    html += field("Email","email","text",v.email);
    html += field("Empresa","empresa","text",v.empresa);
    html += field("Função","funcao","text",v.funcao);
    html += textareaField("Observações","observacoes",v.observacoes);
  }
  return html;
}

function collectFormData(){
  const data = {};
  const form = document.getElementById("dynamicForm");
  form.querySelectorAll("[id^='f_']").forEach(el=>{
    const key = el.id.substring(2);
    if(el.type==="checkbox"){
      data[key] = el.checked;
    } else if(el.type==="number"){
      data[key] = el.value===""?0:parseInt(el.value,10);
    } else {
      data[key] = el.value;
    }
  });
  return data;
}

async function saveItem(){
  if(!editingModule) return;
  const data = collectFormData();
  let url = api(editingModule);
  let method = "POST";
  if(editingId){
    url = api(editingModule) + "/" + editingId;
    method = "PUT";
  }
  try{
    await apiSend(url, method, data);
    bootstrap.Modal.getInstance(document.getElementById("formModal")).hide();
    loadTab(editingModule);
  }catch(e){
    alert("Erro ao salvar: "+e);
  }
}

function openModal(modulo, item){
  editingModule = modulo;
  editingId = item?item.id:null;
  const meta = MODULES_META[modulo] || {label:modulo};
  document.getElementById("modalTitle").textContent = (item?"Editar ":"Adicionar ") + meta.label;
  document.getElementById("dynamicForm").innerHTML = generateFormHTML(modulo, item);
  new bootstrap.Modal(document.getElementById("formModal")).show();
}

async function deleteItem(modulo, id){
  if(!confirm("Confirma exclusão?")) return;
  await apiSend(api(modulo)+"/"+id, "DELETE", {});
  loadTab(modulo);
}

async function duplicateItem(modulo, id){
  await apiSend(api(modulo)+"/"+id+"/duplicar", "POST", {});
  loadTab(modulo);
}

function actionBtns(modulo, item){
  const meta = MODULES_META[modulo] || {dup:false};
  let s = `<button class="btn btn-sm btn-outline-primary" onclick="openModal('${modulo}',${JSON.stringify(item).replace(/"/g,'&quot;')})"><i class="bi bi-pencil"></i></button> `;
  if(meta.dup){
    s += `<button class="btn btn-sm btn-outline-secondary" onclick="duplicateItem('${modulo}',${item.id})"><i class="bi bi-files"></i></button> `;
  }
  s += `<button class="btn btn-sm btn-outline-danger" onclick="deleteItem('${modulo}',${item.id})"><i class="bi bi-trash"></i></button>`;
  return s;
}

function tableHTML(modulo, items, columns){
  const meta = MODULES_META[modulo] || {icon:"",label:modulo};
  let html = `<div class="d-flex justify-content-between align-items-center mb-3">
    <h4 class="mb-0">${meta.icon} ${meta.label} (${items.length})</h4>
    <button class="btn btn-sec" onclick="openModal('${modulo}',null)"><i class="bi bi-plus-lg"></i> Adicionar</button>
  </div>`;
  if(items.length===0){
    html += `<div class="alert alert-info">Nenhum registro encontrado.</div>`;
    return html;
  }
  html += `<div class="table-responsive"><table class="table table-hover module-card"><thead><tr>`;
  columns.forEach(c=> html += `<th>${c.label}</th>`);
  html += `<th>Ações</th></tr></thead><tbody>`;
  items.forEach(it=>{
    html += `<tr>`;
    columns.forEach(c=> html += `<td>${esc(it[c.key])}</td>`);
    html += `<td>${actionBtns(modulo, it)}</td></tr>`;
  });
  html += `</tbody></table></div>`;
  return html;
}

const COLUMNS = {
  extintores: [
    {key:"numero_extintor",label:"Nº"},{key:"classe_incendio",label:"Classe"},{key:"tipo",label:"Tipo"},
    {key:"capacidade",label:"Capac."},{key:"localizacao",label:"Local"},{key:"data_validade",label:"Validade"},{key:"status",label:"Status"}
  ],
  mangueiras: [
    {key:"numero_mangueira",label:"Nº"},{key:"tipo",label:"Tipo"},{key:"comprimento",label:"Comp."},
    {key:"diametro",label:"Diâm."},{key:"abrigo_hidrante",label:"Abrigo"},{key:"data_validade",label:"Validade"},{key:"status",label:"Status"}
  ],
  vgas: [
    {key:"numero_vga",label:"Nº"},{key:"localizacao",label:"Local"},{key:"vazao",label:"Vazão"},
    {key:"pressao",label:"Pressão"},{key:"data_ultima_inspecao",label:"Inspeção"},{key:"status",label:"Status"}
  ],
  abrigos: [
    {key:"codigo_abrigo",label:"Código"},{key:"localizacao",label:"Local"},{key:"pavimento",label:"Pav."},
    {key:"setor",label:"Setor"},{key:"tem_mangueira",label:"Mangueira"},{key:"tem_sinalizacao",label:"Sinalização"}
  ],
  outros_equipamentos: [
    {key:"tipo_equipamento",label:"Tipo"},{key:"patrimonio",label:"Patrim."},{key:"localizacao",label:"Local"},
    {key:"data_validade",label:"Validade"},{key:"status",label:"Status"}
  ],
  kits_crise: [
    {key:"item",label:"Item"},{key:"quantidade",label:"Qtd"},{key:"localizacao",label:"Local"},
    {key:"responsavel",label:"Resp."},{key:"situacao",label:"Situação"},{key:"validade",label:"Validade"}
  ],
  sdais: [
    {key:"codigo",label:"Código"},{key:"central_alarme",label:"Central"},{key:"localizacao",label:"Local"},
    {key:"data_ultimo_teste",label:"Últ. Teste"},{key:"falhas",label:"Falhas"}
  ],
  cftvs: [
    {key:"codigo",label:"Código"},{key:"tipo",label:"Tipo"},{key:"marca",label:"Marca"},
    {key:"modelo",label:"Modelo"},{key:"localizacao",label:"Local"},{key:"estado",label:"Estado"}
  ],
  lojas: [
    {key:"nome_loja",label:"Loja"},{key:"numero",label:"Nº"},{key:"segmento",label:"Segmento"},
    {key:"responsavel",label:"Resp."},{key:"data_vistoria",label:"Vistoria"},{key:"grau_risco",label:"Risco"}
  ],
  escadas: [
    {key:"codigo",label:"Código"},{key:"pavimento",label:"Pav."},{key:"quantidade_portas",label:"Portas"},
    {key:"barra_antipanico",label:"Antipânico"},{key:"sinalizacao",label:"Sinalização"},{key:"data_inspecao",label:"Inspeção"}
  ],
  tarefas: [
    {key:"nome",label:"Nome"},{key:"prioridade",label:"Prioridade"},{key:"categoria",label:"Categoria"},
    {key:"vencimento",label:"Vencimento"},{key:"responsavel",label:"Resp."},{key:"resolvido",label:"Resolvido"}
  ],
  times: [
    {key:"nome",label:"Nome"},{key:"cargo",label:"Cargo"},{key:"empresa",label:"Empresa"},
    {key:"categoria",label:"Categoria"},{key:"data_validade_certificado",label:"Certificado"}
  ],
  documentos: [
    {key:"titulo",label:"Título"},{key:"tipo",label:"Tipo"},{key:"orgao_emissor",label:"Emissor"},
    {key:"data_validade",label:"Validade"}
  ],
  ocorrencias: [
    {key:"tipo",label:"Tipo"},{key:"data",label:"Data"},{key:"hora",label:"Hora"},
    {key:"local",label:"Local"},{key:"status",label:"Status"}
  ],
  contatos: [
    {key:"nome",label:"Nome"},{key:"telefone",label:"Telefone"},{key:"email",label:"Email"},
    {key:"empresa",label:"Empresa"},{key:"funcao",label:"Função"}
  ]
};

async function renderDashboard(){
  const data = await apiGet("/api/dashboard");
  const stats = data.stats || {};
  const alertas = data.alertas || [];
  const movs = data.movimentacoes || [];
  let html = `<h4 class="mb-3">📊 Painel</h4>`;
  html += `<div class="row g-3 mb-4">`;
  const kpis = [
    {label:"Extintores", val:stats.extintores||0, icon:"🧯"},
    {label:"Mangueiras", val:stats.mangueiras||0, icon:"🚒"},
    {label:"Lojas", val:stats.lojas||0, icon:"🏬"},
    {label:"Tarefas", val:stats.tarefas||0, icon:"✅"}
  ];
  kpis.forEach(k=>{
    html += `<div class="col-md-3 col-6"><div class="card kpi-card"><div class="card-body">
      <div class="kpi-label">${k.icon} ${k.label}</div>
      <div class="kpi-num">${k.val}</div></div></div></div>`;
  });
  html += `</div>`;
  html += `<div class="row g-3"><div class="col-md-6">
    <div class="card module-card"><div class="card-body">
    <h6 class="fw-bold mb-3">⚠️ Alertas de Vencimento</h6>`;
  if(alertas.length===0){ html += `<p class="text-muted">Nenhum alerta.</p>`; }
  else {
    alertas.slice(0,10).forEach(a=>{
      html += `<div class="alert alert-danger alert-item py-2 d-flex justify-content-between align-items-center">
        <span>${esc(a.descricao)}</span>
        <button class="btn btn-sm btn-outline-danger" onclick="switchTab('${a.modulo}')">Ver</button></div>`;
    });
  }
  html += `</div></div></div>`;
  html += `<div class="col-md-6"><div class="card module-card"><div class="card-body">
    <h6 class="fw-bold mb-3">📋 Últimas Movimentações</h6>`;
  if(movs.length===0){ html += `<p class="text-muted">Sem registros.</p>`; }
  else {
    html += `<ul class="list-group list-group-flush">`;
    movs.forEach(m=>{
      html += `<li class="list-group-item px-0 d-flex justify-content-between">
        <span><span class="badge bg-secondary">${esc(m.modulo)}</span> ${esc(m.acao)} #${esc(m.item_id)}</span>
        <small class="text-muted">${esc((m.data||"").substring(0,16))}</small></li>`;
    });
    html += `</ul>`;
  }
  html += `</div></div></div></div>`;
  document.getElementById("content-area").innerHTML = html;
}

async function loadTab(tab){
  currentTab = tab;
  if(tab==="painel"){ await renderDashboard(); return; }
  const items = await apiGet(api(tab));
  const cols = COLUMNS[tab] || [];
  document.getElementById("content-area").innerHTML = tableHTML(tab, items, cols);
}

function switchTab(tab){
  document.querySelectorAll("#mainTabs .nav-link").forEach(b=>{
    b.classList.toggle("active", b.dataset.tab===tab);
  });
  loadTab(tab);
}

document.querySelectorAll("#mainTabs .nav-link").forEach(b=>{
  b.addEventListener("click", ()=> switchTab(b.dataset.tab));
});

loadTab("painel");
</script>
</body>
</html>
'''


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)
