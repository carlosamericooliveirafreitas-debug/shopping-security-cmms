# -*- coding: utf-8 -*-
"""
Sistema de Gestão de Segurança para Shopping Center
FastAPI + SQLite
"""
import os
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base, Session

# -----------------------------------------------------------------------------
# Configuração
# -----------------------------------------------------------------------------
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./seguranca_shopping.db")
PORT = int(os.environ.get("PORT", 8080))

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
    __tablename__ = "kit_crise"
    id = Column(Integer, primary_key=True, autoincrement=True)
    item = Column(String, default="")
    quantidade = Column(String, default="")
    localizacao = Column(String, default="")
    responsavel = Column(String, default="")
    situacao = Column(String, default="")
    validade = Column(String, default="")

class SDAI(Base):
    __tablename__ = "sdai"
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
    __tablename__ = "cftv"
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
    criado_em = Column(DateTime, default=datetime.utcnow)
    concluido_em = Column(DateTime, nullable=True)

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
    __tablename__ = "historico"
    id = Column(Integer, primary_key=True, autoincrement=True)
    modulo = Column(String, default="")
    item_id = Column(Integer, default=0)
    acao = Column(String, default="")
    data = Column(DateTime, default=datetime.utcnow)
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
    "kit_crise": KitCrise,
    "sdai": SDAI,
    "cftv": CFTV,
    "lojas": Loja,
    "escadas": Escada,
    "tarefas": Tarefa,
    "times": Time,
    "documentos": Documento,
    "ocorrencias": Ocorrencia,
    "contatos": Contato,
}

DUPLICABLE = {"extintores", "mangueiras", "outros_equipamentos"}

# Campos de data_validade por módulo para alertas
VALIDADE_FIELDS = {
    "extintores": "data_validade",
    "mangueiras": "data_validade",
    "outros_equipamentos": "data_validade",
    "kit_crise": "validade",
    "times": "data_validade_certificado",
    "documentos": "data_validade",
}

# -----------------------------------------------------------------------------
# FastAPI
# -----------------------------------------------------------------------------
app = FastAPI(title="Gestão de Segurança - Shopping Center")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def model_to_dict(obj) -> Dict[str, Any]:
    d = {c.name: getattr(obj, c.name) for c in obj.__table__.columns}
    for k, v in d.items():
        if isinstance(v, datetime):
            d[k] = v.strftime("%Y-%m-%d %H:%M:%S")
    return d

def reg_historico(db: Session, modulo: str, item_id: int, acao: str, obs: str = ""):
    h = Historico(modulo=modulo, item_id=item_id, acao=acao, observacoes=obs)
    db.add(h)
    db.commit()

# -----------------------------------------------------------------------------
# Endpoints genéricos
# -----------------------------------------------------------------------------
@app.get("/api/{modulo}")
def list_modulo(modulo: str, status: Optional[str] = Query(None), db: Session = Depends(get_db)):
    if modulo not in MODULES:
        raise HTTPException(status_code=404, detail="Módulo não encontrado")
    Model = MODULES[modulo]
    q = db.query(Model)
    if status and hasattr(Model, "status"):
        q = q.filter(Model.status == status)
    items = q.all()
    return [model_to_dict(i) for i in items]

@app.post("/api/{modulo}")
def create_modulo(modulo: str, data: Dict[str, Any], db: Session = Depends(get_db)):
    if modulo not in MODULES:
        raise HTTPException(status_code=404, detail="Módulo não encontrado")
    Model = MODULES[modulo]
    cols = {c.name for c in Model.__table__.columns}
    clean = {k: v for k, v in data.items() if k in cols}
    obj = Model(**clean)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    reg_historico(db, modulo, obj.id, "criado")
    return model_to_dict(obj)

@app.put("/api/{modulo}/{item_id}")
def update_modulo(modulo: str, item_id: int, data: Dict[str, Any], db: Session = Depends(get_db)):
    if modulo not in MODULES:
        raise HTTPException(status_code=404, detail="Módulo não encontrado")
    Model = MODULES[modulo]
    obj = db.query(Model).filter(Model.id == item_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    cols = {c.name for c in Model.__table__.columns}
    for k, v in data.items():
        if k in cols and k != "id":
            setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    reg_historico(db, modulo, obj.id, "atualizado")
    return model_to_dict(obj)

@app.delete("/api/{modulo}/{item_id}")
def delete_modulo(modulo: str, item_id: int, db: Session = Depends(get_db)):
    if modulo not in MODULES:
        raise HTTPException(status_code=404, detail="Módulo não encontrado")
    Model = MODULES[modulo]
    obj = db.query(Model).filter(Model.id == item_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    db.delete(obj)
    db.commit()
    reg_historico(db, modulo, item_id, "excluido")
    return {"ok": True}

@app.post("/api/{modulo}/{item_id}/duplicar")
def duplicate_modulo(modulo: str, item_id: int, db: Session = Depends(get_db)):
    if modulo not in DUPLICABLE:
        raise HTTPException(status_code=400, detail="Módulo não permite duplicação")
    Model = MODULES[modulo]
    obj = db.query(Model).filter(Model.id == item_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    data = model_to_dict(obj)
    data.pop("id", None)
    if "numero_extintor" in data and data["numero_extintor"]:
        data["numero_extintor"] = data["numero_extintor"] + " (cópia)"
    if "numero_mangueira" in data and data["numero_mangueira"]:
        data["numero_mangueira"] = data["numero_mangueira"] + " (cópia)"
    if "tipo_equipamento" in data and data["tipo_equipamento"]:
        data["tipo_equipamento"] = data["tipo_equipamento"] + " (cópia)"
    new = Model(**data)
    db.add(new)
    db.commit()
    db.refresh(new)
    reg_historico(db, modulo, new.id, "duplicado", f"origem={item_id}")
    return model_to_dict(new)

# -----------------------------------------------------------------------------
# Dashboard e Alertas
# -----------------------------------------------------------------------------
@app.get("/api/dashboard")
def dashboard(db: Session = Depends(get_db)):
    counts = {}
    for name, Model in MODULES.items():
        counts[name] = db.query(Model).count()

    tarefas_pendentes = db.query(Tarefa).filter(Tarefa.resolvido == False).count()

    hoje = date.today()
    limite = hoje + timedelta(days=30)
    total_vencidos = 0
    for mod, field in VALIDADE_FIELDS.items():
        Model = MODULES[mod]
        col = getattr(Model, field)
        items = db.query(Model).all()
        for it in items:
            val = getattr(it, field)
            if not val:
                continue
            try:
                d = datetime.strptime(val[:10], "%Y-%m-%d").date()
                if d <= limite:
                    total_vencidos += 1
            except Exception:
                continue

    historico = db.query(Historico).order_by(Historico.data.desc()).limit(10).all()
    hist_list = []
    for h in historico:
        hd = model_to_dict(h)
        hist_list.append(hd)

    return {
        "counts": counts,
        "tarefas_pendentes": tarefas_pendentes,
        "total_vencidos": total_vencidos,
        "total_alertas": total_vencidos,
        "historico": hist_list,
    }

@app.get("/api/alertas")
def alertas(db: Session = Depends(get_db)):
    hoje = date.today()
    limite = hoje + timedelta(days=30)
    agrupado: Dict[str, List] = {}
    for mod, field in VALIDADE_FIELDS.items():
        Model = MODULES[mod]
        items = db.query(Model).all()
        for it in items:
            val = getattr(it, field)
            if not val:
                continue
            try:
                d = datetime.strptime(val[:10], "%Y-%m-%d").date()
            except Exception:
                continue
            if d <= limite:
                d_item = model_to_dict(it)
                d_item["_campo_validade"] = field
                d_item["_data_validade"] = val
                d_item["_vencido"] = d < hoje
                agrupado.setdefault(mod, []).append(d_item)
    return agrupado

# -----------------------------------------------------------------------------
# Rota raiz - HTML
# -----------------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
def index():
    return HTML_CONTENT

# -----------------------------------------------------------------------------
# HTML / Frontend
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
  :root{ --primary:#1e3a5f; --primary-dark:#0f172a; --bg:#f0f2f5; }
  *{box-sizing:border-box;}
  body{margin:0;background:var(--bg);font-family:'Segoe UI',system-ui,sans-serif;color:#1f2937;}
  .app-header{
    background:linear-gradient(135deg,#0f172a 0%,#1e3a5f 100%);
    color:#fff;padding:22px 28px;box-shadow:0 4px 14px rgba(0,0,0,.25);
  }
  .app-header h1{margin:0;font-size:1.6rem;font-weight:700;letter-spacing:.3px;}
  .app-header p{margin:4px 0 0;opacity:.85;font-size:.9rem;}
  .nav-tabs-scroll{
    display:flex;gap:6px;overflow-x:auto;white-space:nowrap;
    background:#fff;padding:10px 14px;border-bottom:1px solid #e5e7eb;
    position:sticky;top:0;z-index:100;box-shadow:0 2px 6px rgba(0,0,0,.05);
  }
  .nav-tab{
    padding:8px 16px;border-radius:8px;cursor:pointer;font-size:.9rem;font-weight:600;
    color:#475569;background:#f1f5f9;border:none;transition:all .2s;
  }
  .nav-tab:hover{background:#e2e8f0;}
  .nav-tab.active{background:var(--primary);color:#fff;}
  .container-app{max-width:1400px;margin:0 auto;padding:24px;}
  .card{background:#fff;border-radius:12px;box-shadow:0 2px 10px rgba(0,0,0,.06);border:none;margin-bottom:20px;}
  .card-header{background:var(--primary);color:#fff;border-radius:12px 12px 0 0 !important;font-weight:600;}
  .kpi-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:18px;margin-bottom:24px;}
  .kpi{background:#fff;border-radius:12px;padding:22px;box-shadow:0 2px 10px rgba(0,0,0,.06);text-align:center;}
  .kpi .label{font-size:.85rem;color:#64748b;text-transform:uppercase;letter-spacing:.5px;}
  .kpi .value{font-size:2.2rem;font-weight:700;margin-top:6px;color:var(--primary);}
  .kpi.danger .value{color:#dc2626;}
  .kpi.warning .value{color:#d97706;}
  .kpi.info .value{color:#2563eb;}
  table{width:100%;border-collapse:collapse;}
  thead th{background:var(--primary);color:#fff;padding:12px;text-align:left;font-size:.82rem;text-transform:uppercase;letter-spacing:.4px;}
  thead th:first-child{border-radius:8px 0 0 0;}
  thead th:last-child{border-radius:0 8px 0 0;}
  tbody td{padding:11px 12px;border-bottom:1px solid #eef2f7;font-size:.88rem;}
  tbody tr:hover{background:#f8fafc;}
  .badge{padding:5px 10px;border-radius:20px;font-size:.75rem;font-weight:600;}
  .badge-ok{background:#dcfce7;color:#166534;}
  .badge-warn{background:#fef3c7;color:#92400e;}
  .badge-danger{background:#fee2e2;color:#991b1b;}
  .badge-info{background:#dbeafe;color:#1e40af;}
  .badge-muted{background:#f1f5f9;color:#475569;}
  .modal-overlay{position:fixed;inset:0;background:rgba(15,23,42,.55);display:none;align-items:flex-start;justify-content:center;z-index:1000;padding:30px 15px;overflow-y:auto;}
  .modal-overlay.show{display:flex;animation:fadeIn .2s;}
  .modal-box{background:#fff;border-radius:14px;max-width:780px;width:100%;padding:26px;box-shadow:0 20px 50px rgba(0,0,0,.3);animation:slideUp .25s;}
  @keyframes fadeIn{from{opacity:0}to{opacity:1}}
  @keyframes slideUp{from{transform:translateY(20px);opacity:0}to{transform:translateY(0);opacity:1}}
  .form-label{font-weight:600;font-size:.85rem;color:#334155;margin-bottom:4px;}
  .form-select,.form-control{border-radius:8px;border:1px solid #cbd5e1;padding:8px 10px;font-size:.9rem;}
  .form-select:focus,.form-control:focus{border-color:var(--primary);box-shadow:0 0 0 .2rem rgba(30,58,95,.15);}
  .btn-primary{background:var(--primary);border-color:var(--primary);}
  .btn-primary:hover{background:#15293f;border-color:#15293f;}
  .btn-icon{padding:5px 9px;border-radius:6px;font-size:.8rem;margin-right:4px;}
  .alert-item{background:#fff;border-left:4px solid #dc2626;border-radius:8px;padding:12px 16px;margin-bottom:10px;box-shadow:0 1px 4px rgba(0,0,0,.05);display:flex;justify-content:space-between;align-items:center;}
  .alert-item.warn{border-left-color:#d97706;}
  .section-title{font-size:1.1rem;font-weight:700;color:var(--primary);margin:24px 0 12px;}
  .empty-state{text-align:center;padding:40px;color:#94a3b8;}
  .table-wrap{overflow-x:auto;border-radius:12px;}
  @media(max-width:768px){
    .app-header h1{font-size:1.2rem;}
    .kpi .value{font-size:1.6rem;}
  }
</style>
</head>
<body>

<div class="app-header">
  <h1>🛡️ Gestão de Segurança - Shopping Center</h1>
  <p>Sistema integrado de gestão de segurança e combate a incêndio</p>
</div>

<div class="nav-tabs-scroll" id="navTabs">
  <button class="nav-tab active" onclick="switchTab('dashboard')">PAINEL</button>
  <button class="nav-tab" onclick="switchTab('extintores')">Extintores</button>
  <button class="nav-tab" onclick="switchTab('mangueiras')">Mangueiras</button>
  <button class="nav-tab" onclick="switchTab('vgas')">VGAs</button>
  <button class="nav-tab" onclick="switchTab('abrigos')">Abrigos</button>
  <button class="nav-tab" onclick="switchTab('outros_equipamentos')">Outros Equip.</button>
  <button class="nav-tab" onclick="switchTab('kit_crise')">Kit Crise</button>
  <button class="nav-tab" onclick="switchTab('sdai')">SDAI</button>
  <button class="nav-tab" onclick="switchTab('cftv')">CFTV</button>
  <button class="nav-tab" onclick="switchTab('lojas')">Lojas</button>
  <button class="nav-tab" onclick="switchTab('escadas')">Escadas</button>
  <button class="nav-tab" onclick="switchTab('tarefas')">Tarefas</button>
  <button class="nav-tab" onclick="switchTab('times')">Times</button>
  <button class="nav-tab" onclick="switchTab('documentos')">Documentos</button>
  <button class="nav-tab" onclick="switchTab('ocorrencias')">Ocorrências</button>
  <button class="nav-tab" onclick="switchTab('contatos')">Contatos</button>
</div>

<div class="container-app" id="appContent"></div>

<div class="modal-overlay" id="modalOverlay">
  <div class="modal-box" id="modalBox"></div>
</div>

<script>
const MODULE_META = {
  dashboard:{label:'Painel',icon:'📊'},
  extintores:{label:'Extintores',icon:'🧯'},
  mangueiras:{label:'Mangueiras',icon:'🚒'},
  vgas:{label:'VGAs',icon:'💧'},
  abrigos:{label:'Abrigos',icon:'🚪'},
  outros_equipamentos:{label:'Outros Equipamentos',icon:'🧰'},
  kit_crise:{label:'Kit Crise',icon:'🎒'},
  sdai:{label:'SDAI',icon:'🚨'},
  cftv:{label:'CFTV',icon:'📹'},
  lojas:{label:'Lojas',icon:'🏬'},
  escadas:{label:'Escadas',icon:'🪜'},
  tarefas:{label:'Tarefas',icon:'✅'},
  times:{label:'Times',icon:'👥'},
  documentos:{label:'Documentos',icon:'📄'},
  ocorrencias:{label:'Ocorrências',icon:'⚠️'},
  contatos:{label:'Contatos',icon:'📇'}
};

const DUPLICABLE = ['extintores','mangueiras','outros_equipamentos'];
let currentTab = 'dashboard';
let cacheData = {};

function esc(v){
  if(v===null||v===undefined) return '';
  return String(v).replace(/[&<>"']/g, c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}

function badgeForStatus(status){
  if(!status) return '<span class="badge badge-muted">-</span>';
  const s = status.toLowerCase();
  if(['conforme','disponível','disponivel','ativo','ok','resolvido'].includes(s)) return '<span class="badge badge-ok">'+esc(status)+'</span>';
  if(['não conforme','nao conforme','em manutenção','em manutencao','em andamento','repor','inspecionar','manutenção','manutencao'].includes(s)) return '<span class="badge badge-warn">'+esc(status)+'</span>';
  if(['inativo','vencido','aberto','não conformidade'].includes(s)) return '<span class="badge badge-danger">'+esc(status)+'</span>';
  return '<span class="badge badge-info">'+esc(status)+'</span>';
}

async function apiGet(url){
  const r = await fetch(url);
  if(!r.ok) throw new Error('Erro '+r.status);
  return r.json();
}
async function apiPost(url,body){
  const r = await fetch(url,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body||{})});
  if(!r.ok) throw new Error('Erro '+r.status);
  return r.json();
}
async function apiPut(url,body){
  const r = await fetch(url,{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify(body||{})});
  if(!r.ok) throw new Error('Erro '+r.status);
  return r.json();
}
async function apiDelete(url){
  const r = await fetch(url,{method:'DELETE'});
  if(!r.ok) throw new Error('Erro '+r.status);
  return r.json();
}

function switchTab(tab){
  currentTab = tab;
  document.querySelectorAll('.nav-tab').forEach(b=>b.classList.remove('active'));
  const btns = document.querySelectorAll('.nav-tab');
  const idx = Object.keys(MODULE_META).indexOf(tab);
  if(idx>=0 && btns[idx]) btns[idx].classList.add('active');
  renderTab();
}

async function renderTab(){
  const app = document.getElementById('appContent');
  if(currentTab==='dashboard'){ await renderDashboard(); return; }
  const meta = MODULE_META[currentTab];
  try{
    const data = await apiGet('/api/'+currentTab);
    cacheData[currentTab] = data;
    app.innerHTML = renderModuleTable(currentTab, data);
  }catch(e){
    app.innerHTML = '<div class="card p-4 text-danger">Erro ao carregar: '+esc(e.message)+'</div>';
  }
}

function renderModuleTable(tab, items){
  const meta = MODULE_META[tab];
  const dup = DUPLICABLE.includes(tab);
  let html = '<div class="card"><div class="card-header d-flex justify-content-between align-items-center">'+
    '<span>'+meta.icon+' '+meta.label+' ('+items.length+')</span>'+
    '<button class="btn btn-light btn-sm" onclick="openForm(\''+tab+'\',null)"><i class="bi bi-plus-lg"></i> Adicionar</button></div>'+
    '<div class="card-body p-0"><div class="table-wrap"><table><thead><tr>';
  const cols = getColumns(tab);
  cols.forEach(c=> html += '<th>'+esc(c.label)+'</th>');
  html += '<th>Ações</th></tr></thead><tbody>';
  if(items.length===0){
    html += '<tr><td colspan="'+(cols.length+1)+'" class="empty-state">Nenhum registro encontrado.</td></tr>';
  }
  items.forEach(it=>{
    html += '<tr>';
    cols.forEach(c=>{
      let val = it[c.field];
      if(c.field==='status' || c.field==='situacao' || c.field==='estado' || c.field==='grau_risco'){
        html += '<td>'+badgeForStatus(val)+'</td>';
      } else if(c.field==='resolvido'){
        html += '<td>'+(val?'<span class="badge badge-ok">Sim</span>':'<span class="badge badge-muted">Não</span>')+'</td>';
      } else {
        html += '<td>'+esc(val)+'</td>';
      }
    });
    html += '<td>';
    if(dup) html += '<button class="btn btn-sm btn-outline-secondary btn-icon" onclick="duplicateItem(\''+tab+'\','+it.id+')" title="Duplicar"><i class="bi bi-files"></i></button>';
    html += '<button class="btn btn-sm btn-outline-primary btn-icon" onclick="editItem(\''+tab+'\','+it.id+')" title="Editar"><i class="bi bi-pencil"></i></button>';
    html += '<button class="btn btn-sm btn-outline-danger btn-icon" onclick="deleteItem(\''+tab+'\','+it.id+')" title="Excluir"><i class="bi bi-trash"></i></button>';
    html += '</td></tr>';
  });
  html += '</tbody></table></div></div></div>';
  return html;
}

function getColumns(tab){
  const map = {
    extintores:[{field:'numero_extintor',label:'Nº'},{field:'patrimonio',label:'Patrimônio'},{field:'classe_incendio',label:'Classe'},{field:'tipo',label:'Tipo'},{field:'capacidade',label:'Capacidade'},{field:'localizacao',label:'Localização'},{field:'pavimento',label:'Pav.'},{field:'data_validade',label:'Validade'},{field:'status',label:'Status'}],
    mangueiras:[{field:'numero_mangueira',label:'Nº'},{field:'tipo',label:'Tipo'},{field:'comprimento',label:'Compr.'},{field:'diametro',label:'Diâm.'},{field:'abrigo_hidrante',label:'Abrigo'},{field:'data_validade',label:'Validade'},{field:'status',label:'Status'}],
    vgas:[{field:'numero_vga',label:'Nº'},{field:'localizacao',label:'Localização'},{field:'pavimento',label:'Pav.'},{field:'vazao',label:'Vazão'},{field:'pressao',label:'Pressão'},{field:'data_ultima_inspecao',label:'Últ. Inspeção'},{field:'status',label:'Status'}],
    abrigos:[{field:'codigo_abrigo',label:'Código'},{field:'localizacao',label:'Localização'},{field:'pavimento',label:'Pav.'},{field:'tem_mangueira',label:'Mangueira'},{field:'tem_esguicho',label:'Esguicho'},{field:'tem_sinalizacao',label:'Sinalização'},{field:'situacao',label:'Situação'}],
    outros_equipamentos:[{field:'tipo_equipamento',label:'Tipo'},{field:'patrimonio',label:'Patrimônio'},{field:'localizacao',label:'Localização'},{field:'data_validade',label:'Validade'},{field:'status',label:'Status'}],
    kit_crise:[{field:'item',label:'Item'},{field:'quantidade',label:'Qtd'},{field:'localizacao',label:'Localização'},{field:'responsavel',label:'Responsável'},{field:'situacao',label:'Situação'},{field:'validade',label:'Validade'}],
    sdai:[{field:'codigo',label:'Código'},{field:'central_alarme',label:'Central'},{field:'detectores',label:'Detectores'},{field:'sirenes',label:'Sirenes'},{field:'data_ultimo_teste',label:'Últ. Teste'},{field:'falhas',label:'Falhas'}],
    cftv:[{field:'codigo',label:'Código'},{field:'tipo',label:'Tipo'},{field:'marca',label:'Marca'},{field:'modelo',label:'Modelo'},{field:'localizacao',label:'Localização'},{field:'estado',label:'Estado'}],
    lojas:[{field:'nome_loja',label:'Loja'},{field:'numero',label:'Nº'},{field:'segmento',label:'Segmento'},{field:'responsavel',label:'Responsável'},{field:'data_vistoria',label:'Vistoria'},{field:'grau_risco',label:'Risco'}],
    escadas:[{field:'codigo',label:'Código'},{field:'pavimento',label:'Pav.'},{field:'quantidade_portas',label:'Portas'},{field:'barra_antipanico',label:'Barra Antipânico'},{field:'sinalizacao',label:'Sinalização'},{field:'data_inspecao',label:'Inspeção'}],
    tarefas:[{field:'nome',label:'Nome'},{field:'prioridade',label:'Prioridade'},{field:'categoria',label:'Categoria'},{field:'vencimento',label:'Vencimento'},{field:'responsavel',label:'Responsável'},{field:'resolvido',label:'Resolvido'}],
    times:[{field:'categoria',label:'Categoria'},{field:'nome',label:'Nome'},{field:'cargo',label:'Cargo'},{field:'empresa',label:'Empresa'},{field:'data_validade_certificado',label:'Validade Cert.'},{field:'telefone',label:'Telefone'}],
    documentos:[{field:'titulo',label:'Título'},{field:'tipo',label:'Tipo'},{field:'data_emissao',label:'Emissão'},{field:'data_validade',label:'Validade'},{field:'orgao_emissor',label:'Órgão'}],
    ocorrencias:[{field:'tipo',label:'Tipo'},{field:'data',label:'Data'},{field:'hora',label:'Hora'},{field:'local',label:'Local'},{field:'responsavel',label:'Responsável'},{field:'status',label:'Status'}],
    contatos:[{field:'nome',label:'Nome'},{field:'telefone',label:'Telefone'},{field:'email',label:'E-mail'},{field:'empresa',label:'Empresa'},{field:'funcao',label:'Função'}]
  };
  return map[tab]||[];
}

async function renderDashboard(){
  const app = document.getElementById('appContent');
  try{
    const dash = await apiGet('/api/dashboard');
    const alertas = await apiGet('/api/alertas');
    let totalGeral = 0;
    Object.values(dash.counts).forEach(c=> totalGeral += c);

    let html = '<div class="kpi-grid">';
    html += kpiCard('Total Geral', totalGeral, '');
    html += kpiCard('Itens Vencidos', dash.total_vencidos, 'danger');
    html += kpiCard('Tarefas Pendentes', dash.tarefas_pendentes, 'warning');
    html += kpiCard('Total Alertas', dash.total_alertas, 'info');
    html += '</div>';

    html += '<div class="card"><div class="card-header">⚠️ Alertas Críticos</div><div class="card-body">';
    let hasAlert = false;
    Object.keys(alertas).forEach(mod=>{
      alertas[mod].forEach(it=>{
        hasAlert = true;
        const venc = it._vencido;
        const label = MODULE_META[mod]?MODULE_META[mod].label:mod;
        const nome = it.numero_extintor||it.numero_mangueira||it.numero_vga||it.codigo_abrigo||it.tipo_equipamento||it.item||it.codigo||it.titulo||it.nome||('#'+it.id);
        html += '<div class="alert-item '+(venc?'':'warn')+'"><div><strong>'+esc(label)+'</strong> — '+esc(nome)+' <span class="badge '+(venc?'badge-danger':'badge-warn')+'">'+(venc?'Vencido':'Vence em breve')+'</span><br><small class="text-muted">Validade: '+esc(it._data_validade)+'</small></div>'+
          '<button class="btn btn-sm btn-primary" onclick="switchTab(\''+mod+'\')">Ver</button></div>';
      });
    });
    if(!hasAlert) html += '<div class="empty-state">Nenhum alerta crítico. 🎉</div>';
    html += '</div></div>';

    html += '<div class="card"><div class="card-header">🕐 Últimas Movimentações</div><div class="card-body p-0"><div class="table-wrap"><table><thead><tr><th>Módulo</th><th>Item ID</th><th>Ação</th><th>Data</th><th>Observações</th></tr></thead><tbody>';
    if(dash.historico.length===0){
      html += '<tr><td colspan="5" class="empty-state">Sem movimentações.</td></tr>';
    }
    dash.historico.forEach(h=>{
      html += '<tr><td>'+esc(h.modulo)+'</td><td>'+esc(h.item_id)+'</td><td>'+esc(h.acao)+'</td><td>'+esc(h.data)+'</td><td>'+esc(h.observacoes)+'</td></tr>';
    });
    html += '</tbody></table></div></div></div>';
    app.innerHTML = html;
  }catch(e){
    app.innerHTML = '<div class="card p-4 text-danger">Erro ao carregar dashboard: '+esc(e.message)+'</div>';
  }
}

function kpiCard(label,value,cls){
  return '<div class="kpi '+cls+'"><div class="label">'+label+'</div><div class="value">'+esc(value)+'</div></div>';
}

function openForm(tab,id){
  let item = {};
  if(id){
    const data = cacheData[tab]||[];
    item = data.find(i=>i.id===id) || {};
  }
  const meta = MODULE_META[tab];
  const box = document.getElementById('modalBox');
  let html = '<div class="d-flex justify-content-between align-items-center mb-3">'+
    '<h4 class="m-0" style="color:var(--primary)">'+meta.icon+' '+(id?'Editar':'Adicionar')+' '+meta.label+'</h4>'+
    '<button class="btn-close" onclick="closeModal()"></button></div>';
  html += '<form id="itemForm">';
  html += generateFormHTML(tab, item);
  html += '<div class="d-flex justify-content-end gap-2 mt-3">';
  html += '<button type="button" class="btn btn-secondary" onclick="closeModal()">Cancelar</button>';
  html += '<button type="button" class="btn btn-primary" onclick="saveItem(\''+tab+'\','+(id||'null')+')"><i class="bi bi-check-lg"></i> Salvar</button>';
  html += '</div></form>';
  box.innerHTML = html;
  document.getElementById('modalOverlay').classList.add('show');
}

function closeModal(){
  document.getElementById('modalOverlay').classList.remove('show');
}

function editItem(tab,id){ openForm(tab,id); }

function field(label, inner){
  return '<div class="mb-2"><label class="form-label">'+label+'</label>'+inner+'</div>';
}
function inp(name,val,type='text'){ return '<input type="'+type+'" class="form-control" id="f_'+name+'" name="'+name+'" value="'+esc(val||'')+'">'; }
function sel(name,val,opts){
  let h = '<select class="form-select" id="f_'+name+'" name="'+name+'">';
  h += '<option value="">-- Selecione --</option>';
  opts.forEach(o=>{ const ov = typeof o==='object'?o.value:o; const ol = typeof o==='object'?o.label:o; h += '<option value="'+esc(ov)+'" '+(val==ov?'selected':'')+'>'+esc(ol)+'</option>'; });
  h += '</select>'; return h;
}
function ta(name,val){ return '<textarea class="form-control" id="f_'+name+'" name="'+name+'" rows="3">'+esc(val||'')+'</textarea>'; }
function chk(name,val){ return '<div class="form-check"><input class="form-check-input" type="checkbox" id="f_'+name+'" name="'+name+'" '+(val?'checked':'')+'><label class="form-check-label" for="f_'+name+'">Sim</label></div>'; }

function generateFormHTML(tab, item){
  let h = '<div class="row">';
  const col = (inner, size=6)=> '<div class="col-md-'+size+'">'+inner+'</div>';

  if(tab==='extintores'){
    h += col(field('Número Extintor', inp('numero_extintor',item.numero_extintor)));
    h += col(field('Patrimônio', inp('patrimonio',item.patrimonio)));
    h += col(field('Classe Incêndio', sel('classe_incendio',item.classe_incendio,['A','B','C','D','K','ABC','BC','Lítio'])));
    h += col(field('Tipo', sel('tipo',item.tipo,['CO2','Pó Químico','Água','Espuma'])));
    h += col(field('Capacidade', inp('capacidade',item.capacidade)));
    h += col(field('Fabricante', inp('fabricante',item.fabricante)));
    h += col(field('Número de Série', inp('numero_serie',item.numero_serie)));
    h += col(field('Data Fabricação', inp('data_fabricacao',item.data_fabricacao,'date')));
    h += col(field('Data Teste Hidrostático', inp('data_teste_hidrostatico',item.data_teste_hidrostatico,'date')));
    h += col(field('Data Validade', inp('data_validade',item.data_validade,'date')));
    h += col(field('Localização', inp('localizacao',item.localizacao)));
    h += col(field('Pavimento', inp('pavimento',item.pavimento)));
    h += col(field('Setor', inp('setor',item.setor)));
    h += col(field('Situação', sel('situacao',item.situacao,['Conforme','Não Conforme','Inspecionar'])));
    h += col(field('Status', sel('status',item.status,['Disponível','Alocado','Em Manutenção','Inativo'])));
    h += '<div class="col-12">'+field('Observações', ta('observacoes',item.observacoes))+'</div>';
  }
  else if(tab==='mangueiras'){
    h += col(field('Número Mangueira', inp('numero_mangueira',item.numero_mangueira)));
    h += col(field('Tipo', sel('tipo',item.tipo,['1 polegada','1.5 pol','2 pol'])));
    h += col(field('Comprimento', inp('comprimento',item.comprimento)));
    h += col(field('Diâmetro', inp('diametro',item.diametro)));
    h += col(field('Fabricante', inp('fabricante',item.fabricante)));
    h += col(field('Data Fabricação', inp('data_fabricacao',item.data_fabricacao,'date')));
    h += col(field('Data Último Ensaio', inp('data_ultimo_ensaio',item.data_ultimo_ensaio,'date')));
    h += col(field('Data Validade', inp('data_validade',item.data_validade,'date')));
    h += col(field('Abrigo Hidrante', inp('abrigo_hidrante',item.abrigo_hidrante)));
    h += col(field('Situação', sel('situacao',item.situacao,['Conforme','Não Conforme','Inspecionar'])));
    h += col(field('Status', sel('status',item.status,['Disponível','Alocado','Em Manutenção','Inativo'])));
    h += '<div class="col-12">'+field('Observações', ta('observacoes',item.observacoes))+'</div>';
  }
  else if(tab==='vgas'){
    h += col(field('Número VGA', inp('numero_vga',item.numero_vga)));
    h += col(field('Localização', inp('localizacao',item.localizacao)));
    h += col(field('Pavimento', inp('pavimento',item.pavimento)));
    h += col(field('Vazão', inp('vazao',item.vazao)));
    h += col(field('Pressão', inp('pressao',item.pressao)));
    h += col(field('Data Última Inspeção', inp('data_ultima_inspecao',item.data_ultima_inspecao,'date')));
    h += col(field('Situação', sel('situacao',item.situacao,['Conforme','Não Conforme','Inspecionar'])));
    h += col(field('Status', sel('status',item.status,['Disponível','Alocado','Em Manutenção','Inativo'])));
    h += '<div class="col-12">'+field('Observações', ta('observacoes',item.observacoes))+'</div>';
  }
  else if(tab==='abrigos'){
    h += col(field('Código Abrigo', inp('codigo_abrigo',item.codigo_abrigo)));
    h += col(field('Localização', inp('localizacao',item.localizacao)));
    h += col(field('Pavimento', inp('pavimento',item.pavimento)));
    h += col(field('Setor', inp('setor',item.setor)));
    h += col(field('Tem Mangueira?', sel('tem_mangueira',item.tem_mangueira,['sim','não'])));
    h += col(field('Mangueira Alocada', inp('mangueira_alocada',item.mangueira_alocada)));
    h += col(field('Tem Chave Storz?', sel('tem_chave_storz',item.tem_chave_storz,['sim','não'])));
    h += col(field('Chave Storz Alocada', inp('chave_storz_alocada',item.chave_storz_alocada)));
    h += col(field('Tem Esguicho?', sel('tem_esguicho',item.tem_esguicho,['sim','não'])));
    h += col(field('Esguicho Alocada', inp('esguicho_alocada',item.esguicho_alocada)));
    h += col(field('Tampão?', sel('tem_tampao',item.tem_tampao,['sim','não'])));
    h += col(field('Tampão Alocada', inp('tampao_alocada',item.tampao_alocada)));
    h += col(field('Tem Redução?', sel('tem_reducao',item.tem_reducao,['sim','não'])));
    h += col(field('Redução Alocada', inp('reducao_alocada',item.reducao_alocada)));
    h += col(field('Tem Adaptadores?', sel('tem_adaptadores',item.tem_adaptadores,['sim','não'])));
    h += col(field('Adaptadores Alocados', inp('adaptadores_alocados',item.adaptadores_alocados)));
    h += col(field('Tem Registro?', sel('tem_registro',item.tem_registro,['sim','não'])));
    h += col(field('Registro Status', inp('registro_status',item.registro_status)));
    h += col(field('Sinalização', sel('tem_sinalizacao',item.tem_sinalizacao,['Conforme','Não Conforme','Inexistente'])));
    h += '<div class="col-12">'+field('Observações', ta('observacoes',item.observacoes))+'</div>';
  }
  else if(tab==='outros_equipamentos'){
    h += col(field('Tipo Equipamento', inp('tipo_equipamento',item.tipo_equipamento)));
    h += col(field('Patrimônio', inp('patrimonio',item.patrimonio)));
    h += col(field('Localização', inp('localizacao',item.localizacao)));
    h += col(field('Data Validade', inp('data_validade',item.data_validade,'date')));
    h += col(field('Situação', sel('situacao',item.situacao,['Conforme','Não Conforme','Inspecionar'])));
    h += col(field('Status', sel('status',item.status,['Disponível','Alocado','Em Manutenção','Inativo'])));
    h += '<div class="col-12">'+field('Observações', ta('observacoes',item.observacoes))+'</div>';
  }
  else if(tab==='kit_crise'){
    h += col(field('Item', inp('item',item.item)));
    h += col(field('Quantidade', inp('quantidade',item.quantidade)));
    h += col(field('Localização', inp('localizacao',item.localizacao)));
    h += col(field('Responsável', inp('responsavel',item.responsavel)));
    h += col(field('Situação', sel('situacao',item.situacao,['OK','Repor','Vencido'])));
    h += col(field('Validade', inp('validade',item.validade,'date')));
  }
  else if(tab==='sdai'){
    h += col(field('Código', inp('codigo',item.codigo)));
    h += col(field('Central de Alarme', inp('central_alarme',item.central_alarme)));
    h += col(field('Acionadores Manuais', inp('acionadores_manuais',item.acionadores_manuais)));
    h += col(field('Detectores', inp('detectores',item.detectores)));
    h += col(field('Sirenes', inp('sirenes',item.sirenes)));
    h += col(field('Módulos', inp('modulos',item.modulos)));
    h += col(field('Fontes', inp('fontes',item.fontes)));
    h += col(field('Baterias', inp('baterias',item.baterias)));
    h += col(field('Loop', inp('loop',item.loop)));
    h += col(field('Endereçamento', inp('enderecamento',item.enderecamento)));
    h += col(field('Data Último Teste', inp('data_ultimo_teste',item.data_ultimo_teste,'date')));
    h += '<div class="col-12">'+field('Falhas', ta('falhas',item.falhas))+'</div>';
    h += '<div class="col-12">'+field('Observações', ta('observacoes',item.observacoes))+'</div>';
  }
  else if(tab==='cftv'){
    h += col(field('Código', inp('codigo',item.codigo)));
    h += col(field('Tipo', sel('tipo',item.tipo,['Câmera','DVR','Monitor'])));
    h += col(field('Marca', inp('marca',item.marca)));
    h += col(field('Modelo', inp('modelo',item.modelo)));
    h += col(field('IP', inp('ip',item.ip)));
    h += col(field('Localização', inp('localizacao',item.localizacao)));
    h += col(field('Estado', sel('estado',item.estado,['Ativo','Inativo','Manutenção'])));
    h += col(field('Garantia', inp('garantia',item.garantia)));
    h += col(field('Data Manutenção', inp('data_manutencao',item.data_manutencao,'date')));
    h += '<div class="col-12">'+field('Observações', ta('observacoes',item.observacoes))+'</div>';
  }
  else if(tab==='lojas'){
    h += col(field('Nome da Loja', inp('nome_loja',item.nome_loja)));
    h += col(field('Número', inp('numero',item.numero)));
    h += col(field('Segmento', inp('segmento',item.segmento)));
    h += col(field('Responsável', inp('responsavel',item.responsavel)));
    h += col(field('Telefone', inp('telefone',item.telefone)));
    h += col(field('E-mail', inp('email',item.email)));
    h += col(field('Hidrantes', inp('hidrantes',item.hidrantes)));
    h += col(field('Data Vistoria', inp('data_vistoria',item.data_vistoria,'date')));
    h += col(field('Grau de Risco', sel('grau_risco',item.grau_risco,['Risco 01','Risco 02','Risco 03','Risco 04'])));
    h += '<div class="col-12">'+field('Problemas Encontrados', ta('problemas_encontrados',item.problemas_encontrados))+'</div>';
    h += '<div class="col-12">'+field('Observações', ta('observacoes',item.observacoes))+'</div>';
  }
  else if(tab==='escadas'){
    h += col(field('Código', inp('codigo',item.codigo)));
    h += col(field('Pavimento', inp('pavimento',item.pavimento)));
    h += col(field('Quantidade de Portas', inp('quantidade_portas',item.quantidade_portas,'number')));
    h += col(field('Barra Antipânico', sel('barra_antipanico',item.barra_antipanico,['Conforme','Não Conforme'])));
    h += col(field('Fechadura', sel('fechadura',item.fechadura,['Conforme','Não Conforme'])));
    h += col(field('Molas', sel('molas',item.molas,['Conforme','Não Conforme'])));
    h += col(field('Sinalização', sel('sinalizacao',item.sinalizacao,['Conforme','Não Conforme','Inexistente'])));
    h += col(field('Situação', inp('situacao',item.situacao)));
    h += col(field('Data Inspeção', inp('data_inspecao',item.data_inspecao,'date')));
    h += '<div class="col-12">'+field('Observações', ta('observacoes',item.observacoes))+'</div>';
  }
  else if(tab==='tarefas'){
    h += col(field('Nome', inp('nome',item.nome)));
    h += col(field('Prioridade', sel('prioridade',item.prioridade,['Baixa','Média','Alta'])));
    h += col(field('Categoria', sel('categoria',item.categoria,['Trabalho','Pessoal','Estudo','Saúde','Finanças','Outros'])));
    h += col(field('Vencimento', inp('vencimento',item.vencimento,'date')));
    h += col(field('Responsável', inp('responsavel',item.responsavel)));
    h += col(field('Resolvido', chk('resolvido',item.resolvido)));
    h += '<div class="col-12">'+field('Descrição', ta('descricao',item.descricao))+'</div>';
    if(item.criado_em) h += '<div class="col-12">'+field('Criado em', inp('criado_em',item.criado_em,'text'))+'</div>';
  }
  else if(tab==='times'){
    h += col(field('Categoria', sel('categoria',item.categoria,['Interno','Terceiro'])));
    h += col(field('Nome', inp('nome',item.nome)));
    h += col(field('Cargo', inp('cargo',item.cargo)));
    h += col(field('Empresa', inp('empresa',item.empresa)));
    h += col(field('Certificados', inp('certificados',item.certificados)));
    h += col(field('Validade Certificado', inp('data_validade_certificado',item.data_validade_certificado,'date')));
    h += col(field('Telefone', inp('telefone',item.telefone)));
    h += col(field('E-mail', inp('email',item.email)));
    h += col(field('Escala', inp('escala',item.escala)));
    h += '<div class="col-12">'+field('Observações', ta('observacoes',item.observacoes))+'</div>';
  }
  else if(tab==='documentos'){
    h += col(field('Título', inp('titulo',item.titulo)));
    h += col(field('Tipo', sel('tipo',item.tipo,['Alvará','LVCB','AVCB','Certificado Brigada','Laudo Técnico','Seguro','Contrato','Outros'])));
    h += col(field('Data Emissão', inp('data_emissao',item.data_emissao,'date')));
    h += col(field('Data Validade', inp('data_validade',item.data_validade,'date')));
    h += col(field('Órgão Emissor', inp('orgao_emissor',item.orgao_emissor)));
    h += col(field('Arquivo URL', inp('arquivo_url',item.arquivo_url)));
    h += '<div class="col-12">'+field('Observações', ta('observacoes',item.observacoes))+'</div>';
  }
  else if(tab==='ocorrencias'){
    h += col(field('Tipo', sel('tipo',item.tipo,['Incêndio','Princípio Incêndio','Vazamento','Alarme Falso','Emergência Médica','Outros'])));
    h += col(field('Data', inp('data',item.data,'date')));
    h += col(field('Hora', inp('hora',item.hora,'time')));
    h += col(field('Local', inp('local',item.local)));
    h += col(field('Responsável', inp('responsavel',item.responsavel)));
    h += col(field('Status', sel('status',item.status,['Aberto','Em Andamento','Resolvido'])));
    h += '<div class="col-12">'+field('Descrição', ta('descricao',item.descricao))+'</div>';
    h += '<div class="col-12">'+field('Providências', ta('providencias',item.providencias))+'</div>';
  }
  else if(tab==='contatos'){
    h += col(field('Nome', inp('nome',item.nome)));
    h += col(field('Telefone', inp('telefone',item.telefone)));
    h += col(field('E-mail', inp('email',item.email)));
    h += col(field('Empresa', inp('empresa',item.empresa)));
    h += col(field('Função', inp('funcao',item.funcao)));
    h += '<div class="col-12">'+field('Observações', ta('observacoes',item.observacoes))+'</div>';
  }
  else {
    h += '<div class="col-12">Formulário não implementado.</div>';
  }

  h += '</div>';
  return h;
}

function collectFormData(tab){
  const form = document.getElementById('itemForm');
  const data = {};
  form.querySelectorAll('[id^="f_"]').forEach(el=>{
    const name = el.id.substring(2);
    if(el.type==='checkbox'){
      data[name] = el.checked;
    } else {
      data[name] = el.value;
    }
  });
  return data;
}

async function saveItem(tab,id){
  const data = collectFormData(tab);
  try{
    if(id){
      await apiPut('/api/'+tab+'/'+id, data);
    } else {
      await apiPost('/api/'+tab, data);
    }
    closeModal();
    await renderTab();
  }catch(e){
    alert('Erro ao salvar: '+e.message);
  }
}

async function deleteItem(tab,id){
  if(!confirm('Confirma a exclusão deste registro?')) return;
  try{
    await apiDelete('/api/'+tab+'/'+id);
    await renderTab();
  }catch(e){
    alert('Erro ao excluir: '+e.message);
  }
}

async function duplicateItem(tab,id){
  try{
    await apiPost('/api/'+tab+'/'+id+'/duplicar',{});
    await renderTab();
  }catch(e){
    alert('Erro ao duplicar: '+e.message);
  }
}

document.getElementById('modalOverlay').addEventListener('click',function(e){
  if(e.target===this) closeModal();
});

window.addEventListener('DOMContentLoaded',()=>{
  switchTab('dashboard');
});
</script>
</body>
</html>'''

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)
