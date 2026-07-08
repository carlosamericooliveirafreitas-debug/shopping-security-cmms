import os
from datetime import datetime
from typing import Optional, Any, Dict, List

from fastapi import FastAPI, Depends, HTTPException, Request, Query
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base, Session

# ---------------------------------------------------------------------------
# Database setup
# ---------------------------------------------------------------------------
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./seguranca.db")

# Railway often provides postgres URLs with postgres:// - normalize to postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------
class Extintor(Base):
    __tablename__ = "extintores"
    id = Column(Integer, primary_key=True, index=True)
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
    id = Column(Integer, primary_key=True, index=True)
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
    id = Column(Integer, primary_key=True, index=True)
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
    id = Column(Integer, primary_key=True, index=True)
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
    id = Column(Integer, primary_key=True, index=True)
    tipo_equipamento = Column(String, default="")
    patrimonio = Column(String, default="")
    localizacao = Column(String, default="")
    data_validade = Column(String, default="")
    situacao = Column(String, default="")
    status = Column(String, default="")
    observacoes = Column(Text, default="")


class KitCrise(Base):
    __tablename__ = "kits_crise"
    id = Column(Integer, primary_key=True, index=True)
    item = Column(String, default="")
    quantidade = Column(String, default="")
    localizacao = Column(String, default="")
    responsavel = Column(String, default="")
    situacao = Column(String, default="")
    validade = Column(String, default="")


class SDAI(Base):
    __tablename__ = "sdais"
    id = Column(Integer, primary_key=True, index=True)
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
    id = Column(Integer, primary_key=True, index=True)
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
    id = Column(Integer, primary_key=True, index=True)
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
    id = Column(Integer, primary_key=True, index=True)
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
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, default="")
    descricao = Column(Text, default="")
    prioridade = Column(String, default="")
    categoria = Column(String, default="")
    vencimento = Column(String, default="")
    responsavel = Column(String, default="")
    resolvido = Column(Boolean, default=False)
    criado_em = Column(String, default="")
    concluido_em = Column(String, default="")


class Time(Base):
    __tablename__ = "times"
    id = Column(Integer, primary_key=True, index=True)
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
    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, default="")
    tipo = Column(String, default="")
    data_emissao = Column(String, default="")
    data_validade = Column(String, default="")
    orgao_emissor = Column(String, default="")
    arquivo_url = Column(String, default="")
    observacoes = Column(Text, default="")


class Ocorrencia(Base):
    __tablename__ = "ocorrencias"
    id = Column(Integer, primary_key=True, index=True)
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
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, default="")
    telefone = Column(String, default="")
    email = Column(String, default="")
    empresa = Column(String, default="")
    funcao = Column(String, default="")
    observacoes = Column(Text, default="")


class Historico(Base):
    __tablename__ = "historicos"
    id = Column(Integer, primary_key=True, index=True)
    modulo = Column(String, default="")
    item_id = Column(Integer, default=0)
    acao = Column(String, default="")
    data = Column(String, default=lambda: datetime.now().isoformat())
    observacoes = Column(Text, default="")


# ---------------------------------------------------------------------------
# Modules mapping
# ---------------------------------------------------------------------------
MODULES: Dict[str, Any] = {
    "extintores": Extintor,
    "mangueiras": Mangueira,
    "vgas": VGA,
    "abrigos": Abrigo,
    "outros_equipamentos": OutroEquipamento,
    "kits_crise": KitCrise,
    "sdai": SDAI,
    "cftv": CFTV,
    "lojas": Loja,
    "escadas": Escada,
    "tarefas": Tarefa,
    "times": Time,
    "documentos": Documento,
    "ocorrencias": Ocorrencia,
    "contatos": Contato,
    "historicos": Historico,
}

DUPLICAVEL = {"extintores", "mangueiras", "outros_equipamentos"}


def model_to_dict(obj: Any) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for c in obj.__table__.columns:
        result[c.name] = getattr(obj, c.name)
    return result


def get_column_names(model: Any) -> List[str]:
    return [c.name for c in model.__table__.columns]


def registrar_historico(db: Session, modulo: str, item_id: int, acao: str, observacoes: str = ""):
    try:
        h = Historico(modulo=modulo, item_id=item_id, acao=acao, observacoes=observacoes)
        db.add(h)
        db.commit()
    except Exception:
        db.rollback()


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------
app = FastAPI(title="Gestão de Segurança - Shopping Center")


@app.on_event("startup")
def on_startup():
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"Erro ao criar tabelas: {e}")
        try:
            Base.metadata.drop_all(bind=engine)
            Base.metadata.create_all(bind=engine)
        except Exception as e2:
            print(f"Erro crítico ao criar tabelas: {e2}")


@app.get("/")
def root():
    return HTMLResponse(content=HTML_CONTENT)


@app.get("/api/{modulo}")
def list_items(modulo: str, status: Optional[str] = Query(None), db: Session = Depends(get_db)):
    if modulo not in MODULES:
        raise HTTPException(status_code=404, detail=f"Módulo '{modulo}' não encontrado")
    Model = MODULES[modulo]
    q = db.query(Model)
    if status and hasattr(Model, "status"):
        q = q.filter(Model.status == status)
    items = q.all()
    return [model_to_dict(i) for i in items]


@app.post("/api/{modulo}")
async def create_item(modulo: str, request: Request, db: Session = Depends(get_db)):
    if modulo not in MODULES:
        raise HTTPException(status_code=404, detail=f"Módulo '{modulo}' não encontrado")
    Model = MODULES[modulo]
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="JSON inválido")
    if not isinstance(data, dict):
        raise HTTPException(status_code=400, detail="Payload deve ser um objeto")

    column_names = get_column_names(Model)
    filtered = {k: v for k, v in data.items() if k in column_names and k != "id"}
    obj = Model(**filtered)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    registrar_historico(db, modulo, obj.id, "criacao", f"Item {obj.id} criado")
    return model_to_dict(obj)


@app.put("/api/{modulo}/{item_id}")
async def update_item(modulo: str, item_id: int, request: Request, db: Session = Depends(get_db)):
    if modulo not in MODULES:
        raise HTTPException(status_code=404, detail=f"Módulo '{modulo}' não encontrado")
    Model = MODULES[modulo]
    obj = db.query(Model).filter(Model.id == item_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="JSON inválido")
    if not isinstance(data, dict):
        raise HTTPException(status_code=400, detail="Payload deve ser um objeto")

    column_names = get_column_names(Model)
    for k, v in data.items():
        if k in column_names and k != "id":
            setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    registrar_historico(db, modulo, obj.id, "atualizacao", f"Item {obj.id} atualizado")
    return model_to_dict(obj)


@app.delete("/api/{modulo}/{item_id}")
def delete_item(modulo: str, item_id: int, db: Session = Depends(get_db)):
    if modulo not in MODULES:
        raise HTTPException(status_code=404, detail=f"Módulo '{modulo}' não encontrado")
    Model = MODULES[modulo]
    obj = db.query(Model).filter(Model.id == item_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    db.delete(obj)
    db.commit()
    registrar_historico(db, modulo, item_id, "exclusao", f"Item {item_id} excluído")
    return {"ok": True, "id": item_id}


@app.post("/api/{modulo}/{item_id}/duplicar")
async def duplicate_item(modulo: str, item_id: int, db: Session = Depends(get_db)):
    if modulo not in MODULES:
        raise HTTPException(status_code=404, detail=f"Módulo '{modulo}' não encontrado")
    if modulo not in DUPLICAVEL:
        raise HTTPException(status_code=400, detail=f"Duplicação não permitida para '{modulo}'")
    Model = MODULES[modulo]
    obj = db.query(Model).filter(Model.id == item_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Item não encontrado")

    column_names = get_column_names(Model)
    new_data = {k: getattr(obj, k) for k in column_names if k != "id"}
    new_obj = Model(**new_data)
    db.add(new_obj)
    db.commit()
    db.refresh(new_obj)
    registrar_historico(db, modulo, new_obj.id, "duplicacao", f"Duplicado a partir do item {item_id}")
    return model_to_dict(new_obj)


@app.get("/api/dashboard")
def dashboard(db: Session = Depends(get_db)):
    stats: Dict[str, Any] = {}
    for nome, Model in MODULES.items():
        try:
            stats[nome] = db.query(Model).count()
        except Exception:
            stats[nome] = 0
    return stats


@app.get("/api/alertas")
def alertas(db: Session = Depends(get_db)):
    hoje = datetime.now().date()
    alertas_list: List[Dict[str, Any]] = []

    # Extintores vencidos
    try:
        for e in db.query(Extintor).all():
            val = (e.data_validade or "").strip()
            if val:
                try:
                    dv = datetime.strptime(val[:10], "%Y-%m-%d").date()
                    dias = (dv - hoje).days
                    if dias < 0:
                        alertas_list.append({"tipo": "Extintor vencido", "modulo": "extintores",
                                             "id": e.id, "descricao": f"Extintor {e.numero_extintor} vencido em {val}",
                                             "dias": dias})
                    elif dias <= 30:
                        alertas_list.append({"tipo": "Extintor a vencer", "modulo": "extintores",
                                             "id": e.id, "descricao": f"Extintor {e.numero_extintor} vence em {val}",
                                             "dias": dias})
                except Exception:
                    pass
    except Exception:
        pass

    # Mangueiras vencidas
    try:
        for m in db.query(Mangueira).all():
            val = (m.data_validade or "").strip()
            if val:
                try:
                    dv = datetime.strptime(val[:10], "%Y-%m-%d").date()
                    dias = (dv - hoje).days
                    if dias < 0:
                        alertas_list.append({"tipo": "Mangueira vencida", "modulo": "mangueiras",
                                             "id": m.id, "descricao": f"Mangueira {m.numero_mangueira} vencida em {val}",
                                             "dias": dias})
                    elif dias <= 30:
                        alertas_list.append({"tipo": "Mangueira a vencer", "modulo": "mangueiras",
                                             "id": m.id, "descricao": f"Mangueira {m.numero_mangueira} vence em {val}",
                                             "dias": dias})
                except Exception:
                    pass
    except Exception:
        pass

    # Outros equipamentos vencidos
    try:
        for o in db.query(OutroEquipamento).all():
            val = (o.data_validade or "").strip()
            if val:
                try:
                    dv = datetime.strptime(val[:10], "%Y-%m-%d").date()
                    dias = (dv - hoje).days
                    if dias < 0:
                        alertas_list.append({"tipo": "Equipamento vencido", "modulo": "outros_equipamentos",
                                             "id": o.id, "descricao": f"{o.tipo_equipamento} vencido em {val}",
                                             "dias": dias})
                    elif dias <= 30:
                        alertas_list.append({"tipo": "Equipamento a vencer", "modulo": "outros_equipamentos",
                                             "id": o.id, "descricao": f"{o.tipo_equipamento} vence em {val}",
                                             "dias": dias})
                except Exception:
                    pass
    except Exception:
        pass

    # Tarefas pendentes
    try:
        for t in db.query(Tarefa).all():
            if not t.resolvido and (t.vencimento or "").strip():
                try:
                    dv = datetime.strptime(t.vencimento[:10], "%Y-%m-%d").date()
                    dias = (dv - hoje).days
                    if dias < 0:
                        alertas_list.append({"tipo": "Tarefa atrasada", "modulo": "tarefas",
                                             "id": t.id, "descricao": f"Tarefa '{t.nome}' atrasada",
                                             "dias": dias})
                except Exception:
                    pass
    except Exception:
        pass

    return alertas_list


# ---------------------------------------------------------------------------
# HTML Frontend
# ---------------------------------------------------------------------------
HTML_CONTENT = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Gestão de Segurança - Shopping Center</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
<link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css" rel="stylesheet">
<style>
  body { background:#f4f6f9; }
  .header-gradient {
    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 50%, #0f2027 100%);
    color:#fff; padding:18px 24px; box-shadow:0 4px 12px rgba(0,0,0,.25);
  }
  .header-gradient h1 { margin:0; font-size:1.6rem; font-weight:700; }
  .nav-tabs .nav-link { color:#1e3c72; font-weight:600; }
  .nav-tabs .nav-link.active { background:#1e3c72; color:#fff; }
  .card-item { transition:.15s; }
  .card-item:hover { box-shadow:0 4px 14px rgba(0,0,0,.12); transform:translateY(-2px); }
  .badge-vencido { background:#dc3545; }
  .badge-ok { background:#198754; }
  .badge-alerta { background:#fd7e14; }
  .stat-card { border-left:5px solid #1e3c72; }
  .alert-card { border-left:5px solid #dc3545; }
</style>
</head>
<body>
<div class="header-gradient">
  <h1>🛡️ Gestão de Segurança - Shopping Center</h1>
</div>

<div class="container-fluid py-3">
  <ul class="nav nav-tabs flex-wrap mb-3" id="mainTabs">
    <li class="nav-item"><button class="nav-link active" data-modulo="painel">PAINEL</button></li>
    <li class="nav-item"><button class="nav-link" data-modulo="extintores">Extintores</button></li>
    <li class="nav-item"><button class="nav-link" data-modulo="mangueiras">Mangueiras</button></li>
    <li class="nav-item"><button class="nav-link" data-modulo="vgas">VGAs</button></li>
    <li class="nav-item"><button class="nav-link" data-modulo="abrigos">Abrigos</button></li>
    <li class="nav-item"><button class="nav-link" data-modulo="outros_equipamentos">Outros Equip.</button></li>
    <li class="nav-item"><button class="nav-link" data-modulo="kits_crise">Kit Crise</button></li>
    <li class="nav-item"><button class="nav-link" data-modulo="sdai">SDAI</button></li>
    <li class="nav-item"><button class="nav-link" data-modulo="cftv">CFTV</button></li>
    <li class="nav-item"><button class="nav-link" data-modulo="lojas">Lojas</button></li>
    <li class="nav-item"><button class="nav-link" data-modulo="escadas">Escadas</button></li>
    <li class="nav-item"><button class="nav-link" data-modulo="tarefas">Tarefas</button></li>
    <li class="nav-item"><button class="nav-link" data-modulo="times">Times</button></li>
    <li class="nav-item"><button class="nav-link" data-modulo="documentos">Documentos</button></li>
    <li class="nav-item"><button class="nav-link" data-modulo="ocorrencias">Ocorrências</button></li>
    <li class="nav-item"><button class="nav-link" data-modulo="contatos">Contatos</button></li>
  </ul>

  <div id="contentArea"></div>
</div>

<!-- Modal -->
<div class="modal fade" id="formModal" tabindex="-1">
  <div class="modal-dialog modal-lg modal-dialog-scrollable">
    <div class="modal-content">
      <div class="modal-header bg-primary text-white">
        <h5 class="modal-title" id="formModalTitle">Formulário</h5>
        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
      </div>
      <div class="modal-body" id="formModalBody"></div>
      <div class="modal-footer">
        <button class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
        <button class="btn btn-primary" id="btnSaveItem"><i class="bi bi-save"></i> Salvar</button>
      </div>
    </div>
  </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
<script>
let currentModulo = 'painel';
let editingId = null;
let formModal = null;

document.addEventListener('DOMContentLoaded', () => {
  formModal = new bootstrap.Modal(document.getElementById('formModal'));
  document.querySelectorAll('#mainTabs .nav-link').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('#mainTabs .nav-link').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      currentModulo = btn.dataset.modulo;
      loadModulo(currentModulo);
    });
  });
  document.getElementById('btnSaveItem').addEventListener('click', saveItem);
  loadModulo('painel');
});

async function apiGet(url){
  const r = await fetch(url);
  if(!r.ok) throw new Error('Erro '+r.status);
  return r.json();
}
async function apiSend(url, method, body){
  const r = await fetch(url, {method, headers:{'Content-Type':'application/json'}, body: JSON.stringify(body)});
  if(!r.ok) throw new Error('Erro '+r.status);
  return r.json();
}

async function loadModulo(modulo){
  const content = document.getElementById('contentArea');
  if(modulo === 'painel'){ await loadPainel(content); return; }
  content.innerHTML = `<div class="d-flex justify-content-between align-items-center mb-3">
    <h4 class="text-primary"><i class="bi bi-list-ul"></i> ${tituloModulo(modulo)}</h4>
    <button class="btn btn-primary" onclick="openForm('${modulo}')"><i class="bi bi-plus-lg"></i> Novo</button>
  </div><div id="itemsList"><div class="text-center py-4 text-muted">Carregando...</div></div>`;
  try{
    const items = await apiGet('/api/'+modulo);
    renderItems(modulo, items);
  }catch(e){
    document.getElementById('itemsList').innerHTML = '<div class="alert alert-danger">Erro ao carregar: '+e.message+'</div>';
  }
}

function tituloModulo(m){
  const titulos = {
    extintores:'Extintores', mangueiras:'Mangueiras', vgas:'VGAs', abrigos:'Abrigos',
    outros_equipamentos:'Outros Equipamentos', kits_crise:'Kit Crise', sdai:'SDAI',
    cftv:'CFTV', lojas:'Lojas', escadas:'Escadas', tarefas:'Tarefas', times:'Times',
    documentos:'Documentos', ocorrencias:'Ocorrências', contatos:'Contatos'
  };
  return titulos[m] || m;
}

function renderItems(modulo, items){
  const el = document.getElementById('itemsList');
  if(!items || items.length === 0){
    el.innerHTML = '<div class="alert alert-info">Nenhum item cadastrado.</div>';
    return;
  }
  let html = '<div class="row g-3">';
  items.forEach(item => {
    const titulo = itemCardTitulo(modulo, item);
    const sub = itemCardSubtitulo(modulo, item);
    const statusBadge = item.status ? `<span class="badge ${statusClass(item.status)} float-end">${item.status}</span>` : '';
    const dupBtn = (modulo==='extintores'||modulo==='mangueiras'||modulo==='outros_equipamentos')
      ? `<button class="btn btn-sm btn-outline-secondary" onclick="duplicateItem('${modulo}',${item.id})"><i class="bi bi-files"></i></button>` : '';
    html += `<div class="col-md-6 col-lg-4">
      <div class="card card-item h-100">
        <div class="card-body">
          <h6 class="card-title">${titulo}${statusBadge}</h6>
          <p class="card-text small text-muted mb-2">${sub}</p>
          <div class="btn-group btn-group-sm">
            <button class="btn btn-sm btn-outline-primary" onclick="editItem('${modulo}',${item.id})"><i class="bi bi-pencil"></i></button>
            ${dupBtn}
            <button class="btn btn-sm btn-outline-danger" onclick="deleteItem('${modulo}',${item.id})"><i class="bi bi-trash"></i></button>
          </div>
        </div>
      </div>
    </div>`;
  });
  html += '</div>';
  el.innerHTML = html;
}

function statusClass(s){
  s = (s||'').toLowerCase();
  if(s.includes('vencid') || s.includes('atrasad') || s.includes('falha') || s.includes('critic')) return 'badge-vencido';
  if(s.includes('alerta') || s.includes('pend') || s.includes('aten')) return 'badge-alerta';
  return 'badge-ok';
}

function itemCardTitulo(modulo, item){
  const map = {
    extintores: item.numero_extintor || item.patrimonio || 'Extintor #'+item.id,
    mangueiras: item.numero_mangueira || 'Mangueira #'+item.id,
    vgas: item.numero_vga || 'VGA #'+item.id,
    abrigos: item.codigo_abrigo || 'Abrigo #'+item.id,
    outros_equipamentos: item.tipo_equipamento || item.patrimonio || 'Equip #'+item.id,
    kits_crise: item.item || 'Kit #'+item.id,
    sdai: item.codigo || 'SDAI #'+item.id,
    cftv: item.codigo || item.modelo || 'CFTV #'+item.id,
    lojas: item.nome_loja || 'Loja #'+item.id,
    escadas: item.codigo || 'Escada #'+item.id,
    tarefas: item.nome || 'Tarefa #'+item.id,
    times: item.nome || 'Membro #'+item.id,
    documentos: item.titulo || 'Doc #'+item.id,
    ocorrencias: item.tipo || 'Ocorrência #'+item.id,
    contatos: item.nome || 'Contato #'+item.id
  };
  return map[modulo] || '#'+item.id;
}

function itemCardSubtitulo(modulo, item){
  const map = {
    extintores: `${item.classe_incendio||''} ${item.capacidade||''} - ${item.localizacao||''} ${item.data_validade?'| Val: '+item.data_validade:''}`,
    mangueiras: `${item.tipo||''} ${item.diametro||''} - ${item.abrigo_hidrante||''} ${item.data_validade?'| Val: '+item.data_validade:''}`,
    vgas: `${item.localizacao||''} - ${item.pavimento||''} | Vazão: ${item.vazao||''}`,
    abrigos: `${item.localizacao||''} - ${item.pavimento||''} | ${item.setor||''}`,
    outros_equipamentos: `${item.localizacao||''} ${item.data_validade?'| Val: '+item.data_validade:''}`,
    kits_crise: `Qtd: ${item.quantidade||''} - ${item.localizacao||''} ${item.validade?'| Val: '+item.validade:''}`,
    sdai: `Central: ${item.central_alarme||''} | Teste: ${item.data_ultimo_teste||''}`,
    cftv: `${item.tipo||''} ${item.marca||''} - ${item.localizacao||''}`,
    lojas: `${item.numero||''} - ${item.segmento||''} | Risco: ${item.grau_risco||''}`,
    escadas: `${item.pavimento||''} | Portas: ${item.quantidade_portas||0} | ${item.situacao||''}`,
    tarefas: `${item.prioridade||''} - ${item.responsavel||''} | Venc: ${item.vencimento||''} ${item.resolvido?'<span class=\'badge badge-ok\'>Resolvido</span>':''}`,
    times: `${item.cargo||''} - ${item.empresa||''} | Val: ${item.data_validade_certificado||''}`,
    documentos: `${item.tipo||''} | Val: ${item.data_validade||''}`,
    ocorrencias: `${item.data||''} ${item.hora||''} - ${item.local||''} | ${item.status||''}`,
    contatos: `${item.funcao||''} - ${item.empresa||''} | ${item.telefone||''}`
  };
  return map[modulo] || '';
}

async function loadPainel(content){
  content.innerHTML = '<div class="mb-4"><h4 class="text-primary"><i class="bi bi-speedometer2"></i> Painel</h4></div><div class="row g-3 mb-4" id="statsRow"><div class="text-muted">Carregando estatísticas...</div></div><div class="row g-3"><div class="col-md-6"><div class="card"><div class="card-header bg-danger text-white"><i class="bi bi-exclamation-triangle"></i> Alertas</div><div class="card-body" id="alertasBody">Carregando...</div></div></div><div class="col-md-6"><div class="card"><div class="card-header bg-primary text-white"><i class="bi bi-clock-history"></i> Histórico Recente</div><div class="card-body" id="histBody">Carregando...</div></div></div></div>';
  try{
    const stats = await apiGet('/api/dashboard');
    let html = '';
    for(const [k,v] of Object.entries(stats)){
      if(k==='historicos') continue;
      html += `<div class="col-md-3 col-sm-6"><div class="card stat-card"><div class="card-body"><div class="text-muted small">${tituloModulo(k)}</div><div class="fs-4 fw-bold text-primary">${v}</div></div></div></div>`;
    }
    document.getElementById('statsRow').innerHTML = html || '<div class="text-muted">Sem dados</div>';
  }catch(e){ document.getElementById('statsRow').innerHTML = '<div class="alert alert-danger">Erro: '+e.message+'</div>'; }
  try{
    const alertas = await apiGet('/api/alertas');
    let ah = '';
    if(alertas.length===0){ ah = '<div class="text-success"><i class="bi bi-check-circle"></i> Nenhum alerta ativo.</div>'; }
    else{
      ah = '<ul class="list-unstyled">';
      alertas.forEach(a => {
        const cls = a.dias < 0 ? 'text-danger' : 'text-warning';
        ah += `<li class="mb-2 p-2 border-start border-3 ${a.dias<0?'border-danger':'border-warning'}"><strong>${a.tipo}</strong><br><small class="${cls}">${a.descricao}</small></li>`;
      });
      ah += '</ul>';
    }
    document.getElementById('alertasBody').innerHTML = ah;
  }catch(e){ document.getElementById('alertasBody').innerHTML = '<div class="alert alert-danger">Erro</div>'; }
  try{
    const hist = await apiGet('/api/historicos');
    let hh = '<ul class="list-unstyled small">';
    (hist.slice(-10).reverse()).forEach(h => {
      hh += `<li class="mb-1"><span class="badge bg-secondary">${h.acao}</span> ${h.modulo} #${h.item_id} <small class="text-muted">${(h.data||'').substring(0,16)}</small></li>`;
    });
    hh += '</ul>';
    document.getElementById('histBody').innerHTML = hh;
  }catch(e){ document.getElementById('histBody').innerHTML = '<div class="text-muted">Sem histórico</div>'; }
}

function openForm(modulo, item=null){
  editingId = item ? item.id : null;
  document.getElementById('formModalTitle').innerText = (item?'Editar ':'Novo ') + tituloModulo(modulo);
  document.getElementById('formModalBody').innerHTML = generateFormHTML(modulo, item);
  formModal.show();
}

async function editItem(modulo, id){
  try{
    const items = await apiGet('/api/'+modulo);
    const item = items.find(i => i.id === id);
    if(item) openForm(modulo, item);
  }catch(e){ alert('Erro: '+e.message); }
}

async function deleteItem(modulo, id){
  if(!confirm('Confirma exclusão?')) return;
  try{
    await apiSend('/api/'+modulo+'/'+id, 'DELETE');
    loadModulo(modulo);
  }catch(e){ alert('Erro: '+e.message); }
}

async function duplicateItem(modulo, id){
  try{
    await apiSend('/api/'+modulo+'/'+id+'/duplicar', 'POST');
    loadModulo(modulo);
  }catch(e){ alert('Erro: '+e.message); }
}

function field(label, name, value='', type='text'){
  return `<div class="col-md-6 mb-2"><label class="form-label small">${label}</label><input type="${type}" class="form-control form-control-sm" id="f_${name}" value="${escapeHtml(value)}"></div>`;
}
function textareaField(label, name, value=''){
  return `<div class="col-12 mb-2"><label class="form-label small">${label}</label><textarea class="form-control form-control-sm" id="f_${name}" rows="2">${escapeHtml(value)}</textarea></div>`;
}
function selectField(label, name, options, value=''){
  let opts = '<option value=""></option>';
  options.forEach(o => { opts += `<option value="${o}" ${o===value?'selected':''}>${o}</option>`; });
  return `<div class="col-md-6 mb-2"><label class="form-label small">${label}</label><select class="form-select form-select-sm" id="f_${name}">${opts}</select></div>`;
}
function escapeHtml(s){ return (s==null?'':String(s)).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;'); }

function generateFormHTML(modulo, item){
  const v = (k) => item ? (item[k]==null?'':item[k]) : '';
  let html = '<div class="row">';
  if(modulo==='extintores'){
    html += field('Número','numero_extintor',v('numero_extintor'));
    html += field('Patrimônio','patrimonio',v('patrimonio'));
    html += selectField('Classe','classe_incendio',['A','B','C','ABC','BC','D','K'],v('classe_incendio'));
    html += selectField('Tipo','tipo',['Pó ABC','CO2','Água','Espuma','Pó BC','Outro'],v('tipo'));
    html += field('Capacidade','capacidade',v('capacidade'));
    html += field('Fabricante','fabricante',v('fabricante'));
    html += field('Nº Série','numero_serie',v('numero_serie'));
    html += field('Data Fabricação','data_fabricacao',v('data_fabricacao'),'date');
    html += field('Teste Hidrostático','data_teste_hidrostatico',v('data_teste_hidrostatico'),'date');
    html += field('Validade','data_validade',v('data_validade'),'date');
    html += field('Localização','localizacao',v('localizacao'));
    html += field('Pavimento','pavimento',v('pavimento'));
    html += field('Setor','setor',v('setor'));
    html += selectField('Situação','situacao',['Bom','Regular','Ruim','Manutenção'],v('situacao'));
    html += selectField('Status','status',['Ativo','Vencido','Em Manutenção','Inativo'],v('status'));
    html += textareaField('Observações','observacoes',v('observacoes'));
  } else if(modulo==='mangueiras'){
    html += field('Número','numero_mangueira',v('numero_mangueira'));
    html += selectField('Tipo','tipo',['Tipo 1','Tipo 2','Tipo 3'],v('tipo'));
    html += field('Comprimento','comprimento',v('comprimento'));
    html += field('Diâmetro','diametro',v('diametro'));
    html += field('Fabricante','fabricante',v('fabricante'));
    html += field('Data Fabricação','data_fabricacao',v('data_fabricacao'),'date');
    html += field('Último Ensaio','data_ultimo_ensaio',v('data_ultimo_ensaio'),'date');
    html += field('Validade','data_validade',v('data_validade'),'date');
    html += field('Abrigo/Hidrante','abrigo_hidrante',v('abrigo_hidrante'));
    html += selectField('Situação','situacao',['Bom','Regular','Ruim','Manutenção'],v('situacao'));
    html += selectField('Status','status',['Ativo','Vencido','Em Manutenção','Inativo'],v('status'));
    html += textareaField('Observações','observacoes',v('observacoes'));
  } else if(modulo==='vgas'){
    html += field('Número VGA','numero_vga',v('numero_vga'));
    html += field('Localização','localizacao',v('localizacao'));
    html += field('Pavimento','pavimento',v('pavimento'));
    html += field('Vazão','vazao',v('vazao'));
    html += field('Pressão','pressao',v('pressao'));
    html += field('Última Inspeção','data_ultima_inspecao',v('data_ultima_inspecao'),'date');
    html += selectField('Situação','situacao',['Bom','Regular','Ruim','Manutenção'],v('situacao'));
    html += selectField('Status','status',['Ativo','Inativo','Em Manutenção'],v('status'));
    html += textareaField('Observações','observacoes',v('observacoes'));
  } else if(modulo==='abrigos'){
    html += field('Código Abrigo','codigo_abrigo',v('codigo_abrigo'));
    html += field('Localização','localizacao',v('localizacao'));
    html += field('Pavimento','pavimento',v('pavimento'));
    html += field('Setor','setor',v('setor'));
    html += selectField('Tem Mangueira','tem_mangueira',['Sim','Não'],v('tem_mangueira'));
    html += field('Mangueira Alocada','mangueira_alocada',v('mangueira_alocada'));
    html += selectField('Tem Chave Storz','tem_chave_storz',['Sim','Não'],v('tem_chave_storz'));
    html += field('Chave Storz Alocada','chave_storz_alocada',v('chave_storz_alocada'));
    html += selectField('Tem Esguicho','tem_esguicho',['Sim','Não'],v('tem_esguicho'));
    html += field('Esguicho Alocada','esguicho_alocada',v('esguicho_alocada'));
    html += selectField('Tem Tampão','tem_tampao',['Sim','Não'],v('tem_tampao'));
    html += field('Tampão Alocada','tampao_alocada',v('tampao_alocada'));
    html += selectField('Tem Redução','tem_reducao',['Sim','Não'],v('tem_reducao'));
    html += field('Redução Alocada','reducao_alocada',v('reducao_alocada'));
    html += selectField('Tem Adaptadores','tem_adaptadores',['Sim','Não'],v('tem_adaptadores'));
    html += field('Adaptadores Alocados','adaptadores_alocados',v('adaptadores_alocados'));
    html += selectField('Tem Registro','tem_registro',['Sim','Não'],v('tem_registro'));
    html += field('Registro Status','registro_status',v('registro_status'));
    html += selectField('Tem Sinalização','tem_sinalizacao',['Sim','Não'],v('tem_sinalizacao'));
    html += textareaField('Observações','observacoes',v('observacoes'));
  } else if(modulo==='outros_equipamentos'){
    html += field('Tipo Equipamento','tipo_equipamento',v('tipo_equipamento'));
    html += field('Patrimônio','patrimonio',v('patrimonio'));
    html += field('Localização','localizacao',v('localizacao'));
    html += field('Validade','data_validade',v('data_validade'),'date');
    html += selectField('Situação','situacao',['Bom','Regular','Ruim','Manutenção'],v('situacao'));
    html += selectField('Status','status',['Ativo','Vencido','Em Manutenção','Inativo'],v('status'));
    html += textareaField('Observações','observacoes',v('observacoes'));
  } else if(modulo==='kits_crise'){
    html += field('Item','item',v('item'));
    html += field('Quantidade','quantidade',v('quantidade'),'number')
    html += field('Localização','localizacao',v('localizacao'));
    html += field('Responsável','responsavel',v('responsavel'));
    html += selectField('Situação','situacao',['Bom','Regular','Repor','Vencido'],v('situacao'));
    html += field('Validade','validade',v('validade'),'date');
  } else if(modulo==='sdai'){
    html += field('Código','codigo',v('codigo'));
    html += field('Central de Alarme','central_alarme',v('central_alarme'));
    html += field('Acionadores Manuais','acionadores_manuais',v('acionadores_manuais'));
    html += field('Detectores','detectores',v('detectores'));
    html += field('Sirenes','sirenes',v('sirenes'));
    html += field('Módulos','modulos',v('modulos'));
    html += field('Fontes','fontes',v('fontes'));
    html += field('Baterias','baterias',v('baterias'));
    html += field('Loop','loop',v('loop'));
    html += field('Endereçamento','enderecamento',v('enderecamento'));
    html += field('Último Teste','data_ultimo_teste',v('data_ultimo_teste'),'date');
    html += textareaField('Falhas','falhas',v('falhas'));
    html += textareaField('Observações','observacoes',v('observacoes'));
  } else if(modulo==='cftv'){
    html += field('Código','codigo',v('codigo'));
    html += selectField('Tipo','tipo',['Câmera','DVR','NVR','Encoder','Outro'],v('tipo'));
    html += field('Marca','marca',v('marca'));
    html += field('Modelo','modelo',v('modelo'));
    html += field('IP','ip',v('ip'));
    html += field('Localização','localizacao',v('localizacao'));
    html += selectField('Estado','estado',['Ativo','Inativo','Com Falha','Manutenção'],v('estado'));
    html += field('Garantia','garantia',v('garantia'),'date');
    html += field('Data Manutenção','data_manutencao',v('data_manutencao'),'date');
    html += textareaField('Observações','observacoes',v('observacoes'));
  } else if(modulo==='lojas'){
    html += field('Nome da Loja','nome_loja',v('nome_loja'));
    html += field('Número','numero',v('numero'));
    html += field('Segmento','segmento',v('segmento'));
    html += field('Responsável','responsavel',v('responsavel'));
    html += field('Telefone','telefone',v('telefone'));
    html += field('Email','email',v('email'),'email')
    html += field('Hidrantes','hidrantes',v('hidrantes'));
    html += textareaField('Problemas Encontrados','problemas_encontrados',v('problemas_encontrados'));
    html += field('Data Vistoria','data_vistoria',v('data_vistoria'),'date');
    html += selectField('Grau de Risco','grau_risco',['Baixo','Médio','Alto','Crítico'],v('grau_risco'));
    html += textareaField('Observações','observacoes',v('observacoes'));
  } else if(modulo==='escadas'){
    html += field('Código','codigo',v('codigo'));
    html += field('Pavimento','pavimento',v('pavimento'));
    html += field('Qtd Portas','quantidade_portas',v('quantidade_portas'),'number')
    html += selectField('Barra Antipânico','barra_antipanico',['Sim','Não'],v('barra_antipanico'));
    html += selectField('Fechadura','fechadura',['Boa','Regular','Ruim','Sem'],v('fechadura'));
    html += selectField('Molas','molas',['Boa','Regular','Ruim','Sem'],v('molas'));
    html += selectField('Sinalização','sinalizacao',['Boa','Regular','Ausente'],v('sinalizacao'));
    html += selectField('Situação','situacao',['Bom','Regular','Ruim','Manutenção'],v('situacao'));
    html += field('Data Inspeção','data_inspecao',v('data_inspecao'),'date');
    html += textareaField('Observações','observacoes',v('observacoes'));
  } else if(modulo==='tarefas'){
    html += field('Nome','nome',v('nome'));
    html += textareaField('Descrição','descricao',v('descricao'));
    html += selectField('Prioridade','prioridade',['Baixa','Média','Alta','Crítica'],v('prioridade'));
    html += field('Categoria','categoria',v('categoria'));
    html += field('Vencimento','vencimento',v('vencimento'),'date');
    html += field('Responsável','responsavel',v('responsavel'));
    html += `<div class="col-md-6 mb-2"><label class="form-label small">Resolvido</label><select class="form-select form-select-sm" id="f_resolvido"><option value="false" ${!v('resolvido')?'selected':''}>Não</option><option value="true" ${v('resolvido')?'selected':''}>Sim</option></select></div>`;
  } else if(modulo==='times'){
    html += field('Categoria','categoria',v('categoria'));
    html += field('Nome','nome',v('nome'));
    html += field('Cargo','cargo',v('cargo'));
    html += field('Empresa','empresa',v('empresa'));
    html += field('Certificados','certificados',v('certificados'));
    html += field('Validade Certificado','data_validade_certificado',v('data_validade_certificado'),'date');
    html += field('Telefone','telefone',v('telefone'));
    html += field('Email','email',v('email'),'email')
    html += field('Escala','escala',v('escala'));
    html += textareaField('Observações','observacoes',v('observacoes'));
  } else if(modulo==='documentos'){
    html += field('Título','titulo',v('titulo'));
    html += selectField('Tipo','tipo',['Certificado','Laudo','Licença','Manual','Procedimento','Outro'],v('tipo'));
    html += field('Data Emissão','data_emissao',v('data_emissao'),'date');
    html += field('Data Validade','data_validade',v('data_validade'),'date');
    html += field('Órgão Emissor','orgao_emissor',v('orgao_emissor'));
    html += field('Arquivo URL','arquivo_url',v('arquivo_url'));
    html += textareaField('Observações','observacoes',v('observacoes'));
  } else if(modulo==='ocorrencias'){
    html += field('Tipo','tipo',v('tipo'));
    html += field('Data','data',v('data'),'date');
    html += field('Hora','hora',v('hora'),'time')
    html += field('Local','local',v('local'));
    html += textareaField('Descrição','descricao',v('descricao'));
    html += field('Responsável','responsavel',v('responsavel'));
    html += textareaField('Providências','providencias',v('providencias'));
    html += selectField('Status','status',['Aberta','Em Andamento','Concluída','Arquivada'],v('status'));
  } else if(modulo==='contatos'){
    html += field('Nome','nome',v('nome'));
    html += field('Telefone','telefone',v('telefone'));
    html += field('Email','email',v('email'),'email')
    html += field('Empresa','empresa',v('empresa'));
    html += field('Função','funcao',v('funcao'));
    html += textareaField('Observações','observacoes',v('observacoes'));
  } else {
    html += '<div class="alert alert-warning">Formulário não disponível para este módulo.</div>';
  }
  html += '</div>';
  return html;
}

async function saveItem(){
  const modulo = currentModulo === 'painel' ? null : currentModulo;
  if(!modulo){ alert('Selecione um módulo.'); return; }
  const body = {};
  document.querySelectorAll('[id^="f_"]').forEach(el => {
    const key = el.id.substring(2);
    let val = el.value;
    if(el.tagName === 'SELECT' && (val === 'true' || val === 'false')) val = val === 'true';
    if(el.type === 'number') val = val === '' ? 0 : Number(val);
    body[key] = val;
  });
  try{
    if(editingId){
      await apiSend('/api/'+modulo+'/'+editingId, 'PUT', body);
    } else {
      await apiSend('/api/'+modulo, 'POST', body);
    }
    formModal.hide();
    loadModulo(modulo);
  }catch(e){ alert('Erro ao salvar: '+e.message); }
}
</script>
</body>
</html>"""


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
