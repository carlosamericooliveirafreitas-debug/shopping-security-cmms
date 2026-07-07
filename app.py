# -*- coding: utf-8 -*-
"""
Gerenciador de Tarefas - FastAPI + SQLite
Servidor web para Coordenador de Segurança de Shopping
"""
import os
import uuid
from datetime import datetime
from typing import Optional, List

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base

# -----------------------------------------------------------------------------
# Configuração do banco SQLite
# -----------------------------------------------------------------------------
DATABASE_URL = "sqlite:///./tarefas.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

# -----------------------------------------------------------------------------
# Modelo Tarefa (SQLAlchemy)
# -----------------------------------------------------------------------------
class Tarefa(Base):
    __tablename__ = "tarefas"
    id = Column(String, primary_key=True)
    nome = Column(String, nullable=False)
    descricao = Column(String, default="")
    prioridade = Column(String, default="Média")
    categoria = Column(String, default="Outros")
    vencimento = Column(String, default="")
    responsavel = Column(String, default="")
    resolvido = Column(Boolean, default=False)
    criado_em = Column(String, default=lambda: datetime.now().isoformat())
    concluido_em = Column(String, nullable=True)

# -----------------------------------------------------------------------------
# Schemas Pydantic
# -----------------------------------------------------------------------------
class TarefaCreate(BaseModel):
    nome: str
    descricao: Optional[str] = ""
    prioridade: str = "Média"
    categoria: str = "Outros"
    vencimento: Optional[str] = ""
    responsavel: Optional[str] = ""
    resolvido: bool = False

class TarefaUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    prioridade: Optional[str] = None
    categoria: Optional[str] = None
    vencimento: Optional[str] = None
    responsavel: Optional[str] = None
    resolvido: Optional[bool] = None

# -----------------------------------------------------------------------------
# App FastAPI
# -----------------------------------------------------------------------------
app = FastAPI(title="Gerenciador de Tarefas")

# CORS liberado para todas origens
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicialização automática das tabelas no startup
@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)

# Dependência de sessão
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
def hoje_str() -> str:
    return datetime.now().strftime("%Y-%m-%d")

def tarefa_to_dict(t: Tarefa) -> dict:
    return {
        "id": t.id,
        "nome": t.nome,
        "descricao": t.descricao or "",
        "prioridade": t.prioridade,
        "categoria": t.categoria,
        "vencimento": t.vencimento or "",
        "responsavel": t.responsavel or "",
        "resolvido": bool(t.resolvido),
        "criado_em": t.criado_em or "",
        "concluido_em": t.concluido_em or "",
    }

def is_vencida(t: dict) -> bool:
    if t["resolvido"] or not t["vencimento"]:
        return False
    return t["vencimento"] < hoje_str()

def is_hoje(t: dict) -> bool:
    if not t["vencimento"]:
        return False
    return t["vencimento"] == hoje_str()

def is_proxima(t: dict, dias: int = 7) -> bool:
    if not t["vencimento"]:
        return False
    try:
        venc = datetime.strptime(t["vencimento"], "%Y-%m-%d")
    except Exception:
        return False
    diff = (venc - datetime.now()).days
    return 0 <= diff <= dias

# -----------------------------------------------------------------------------
# Endpoints da API
# -----------------------------------------------------------------------------
@app.get("/api/tarefas")
def listar_tarefas(
    filtro: Optional[str] = Query(None),
    busca: Optional[str] = Query(None),
):
    db = SessionLocal()
    try:
        q = db.query(Tarefa)
        if filtro == "pendentes":
            q = q.filter(Tarefa.resolvido == False)
        elif filtro == "resolvidas":
            q = q.filter(Tarefa.resolvido == True)
        if busca:
            like = f"%{busca}%"
            q = q.filter(Tarefa.nome.ilike(like))
        tarefas = q.order_by(Tarefa.criado_em.desc()).all()
        return [tarefa_to_dict(t) for t in tarefas]
    finally:
        db.close()

@app.post("/api/tarefas")
def criar_tarefa(payload: TarefaCreate):
    db = SessionLocal()
    try:
        t = Tarefa(
            id=str(uuid.uuid4()),
            nome=payload.nome,
            descricao=payload.descricao or "",
            prioridade=payload.prioridade or "Média",
            categoria=payload.categoria or "Outros",
            vencimento=payload.vencimento or "",
            responsavel=payload.responsavel or "",
            resolvido=payload.resolvido,
            criado_em=datetime.now().isoformat(),
            concluido_em=datetime.now().isoformat() if payload.resolvido else None,
        )
        db.add(t)
        db.commit()
        return tarefa_to_dict(t)
    finally:
        db.close()

@app.put("/api/tarefas/{id}")
def atualizar_tarefa(id: str, payload: TarefaUpdate):
    db = SessionLocal()
    try:
        t = db.query(Tarefa).filter(Tarefa.id == id).first()
        if not t:
            raise HTTPException(status_code=404, detail="Tarefa não encontrada")
        dados = payload.dict(exclude_unset=True)
        for k, v in dados.items():
            setattr(t, k, v)
        if "resolvido" in dados:
            t.concluido_em = datetime.now().isoformat() if t.resolvido else None
        db.commit()
        return tarefa_to_dict(t)
    finally:
        db.close()

@app.delete("/api/tarefas/{id}")
def excluir_tarefa(id: str):
    db = SessionLocal()
    try:
        t = db.query(Tarefa).filter(Tarefa.id == id).first()
        if not t:
            raise HTTPException(status_code=404, detail="Tarefa não encontrada")
        db.delete(t)
        db.commit()
        return {"ok": True}
    finally:
        db.close()

@app.put("/api/tarefas/{id}/toggle")
def toggle_resolvido(id: str):
    db = SessionLocal()
    try:
        t = db.query(Tarefa).filter(Tarefa.id == id).first()
        if not t:
            raise HTTPException(status_code=404, detail="Tarefa não encontrada")
        t.resolvido = not t.resolvido
        t.concluido_em = datetime.now().isoformat() if t.resolvido else None
        db.commit()
        return tarefa_to_dict(t)
    finally:
        db.close()

@app.delete("/api/tarefas/limpar-resolvidas")
def limpar_resolvidas():
    db = SessionLocal()
    try:
        deletados = db.query(Tarefa).filter(Tarefa.resolvido == True).delete()
        db.commit()
        return {"ok": True, "removidas": deletados}
    finally:
        db.close()

@app.get("/api/tarefas/dashboard")
def dashboard():
    db = SessionLocal()
    try:
        tarefas = [tarefa_to_dict(t) for t in db.query(Tarefa).all()]
        total = len(tarefas)
        pendentes = sum(1 for t in tarefas if not t["resolvido"])
        resolvidas = sum(1 for t in tarefas if t["resolvido"])
        vencidas = [t for t in tarefas if is_vencida(t)]
        vencem_hoje = [t for t in tarefas if is_hoje(t) and not t["resolvido"]]
        proximas = [t for t in tarefas if is_proxima(t, 7) and not t["resolvido"]]
        taxa = round((resolvidas / total * 100), 1) if total else 0.0

        # Distribuição por prioridade
        prioridades = {"Alta": 0, "Média": 0, "Baixa": 0}
        for t in tarefas:
            if t["prioridade"] in prioridades:
                prioridades[t["prioridade"]] += 1

        # Distribuição por categoria
        categorias = {}
        for t in tarefas:
            cat = t["categoria"] or "Outros"
            categorias[cat] = categorias.get(cat, 0) + 1

        return {
            "total": total,
            "pendentes": pendentes,
            "resolvidas": resolvidas,
            "vencidas": len(vencidas),
            "vencem_hoje": len(vencem_hoje),
            "proximas_7": len(proximas),
            "taxa_conclusao": taxa,
            "lista_vencidas": vencidas,
            "lista_proximas": proximas,
            "distribuicao_prioridade": prioridades,
            "distribuicao_categoria": categorias,
        }
    finally:
        db.close()

@app.get("/api/tarefas/relatorio")
def relatorio(tipo: str = Query("completo")):
    db = SessionLocal()
    try:
        tarefas = [tarefa_to_dict(t) for t in db.query(Tarefa).all()]
        if tipo == "pendentes":
            tarefas = [t for t in tarefas if not t["resolvido"]]
        elif tipo == "resolvidas":
            tarefas = [t for t in tarefas if t["resolvido"]]
        elif tipo == "vencidas":
            tarefas = [t for t in tarefas if is_vencida(t)]
        return {
            "tipo": tipo,
            "gerado_em": datetime.now().isoformat(),
            "quantidade": len(tarefas),
            "tarefas": tarefas,
        }
    finally:
        db.close()

# -----------------------------------------------------------------------------
# Rota raiz - serve HTML
# -----------------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
def index():
    # Se existir index.html na pasta, serve ele; senão usa o HTML embutido
    if os.path.exists("index.html"):
        with open("index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(f.read())
    return HTMLResponse(HTML_EMBUTIDO)

# -----------------------------------------------------------------------------
# HTML embutido
# -----------------------------------------------------------------------------
HTML_EMBUTIDO = r'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🛡️ Gerenciador de Tarefas</title>
<style>
/* ===== Reset e base ===== */
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
  font-family: 'Segoe UI', Tahoma, sans-serif;
  background: #f0f2f5;
  color: #1f2937;
  min-height: 100vh;
}
.container { max-width: 1200px; margin: 0 auto; padding: 0 16px; }

/* ===== Header ===== */
.header {
  background: linear-gradient(135deg, #1e3a5f 0%, #2563eb 100%);
  color: #fff;
  padding: 28px 0 0;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}
.header h1 { font-size: 28px; font-weight: 700; }
.header .sub { font-size: 15px; opacity: 0.9; margin-top: 4px; }
.tabs {
  display: flex;
  gap: 6px;
  margin-top: 20px;
  flex-wrap: wrap;
}
.tab {
  background: rgba(255,255,255,0.15);
  color: #fff;
  border: none;
  padding: 10px 22px;
  border-radius: 10px 10px 0 0;
  cursor: pointer;
  font-size: 15px;
  font-weight: 600;
  transition: all 0.2s;
}
.tab:hover { background: rgba(255,255,255,0.28); }
.tab.active { background: #fff; color: #2563eb; }

/* ===== Cards ===== */
.card {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  padding: 18px;
  margin-bottom: 20px;
}
.card h2 {
  font-size: 18px;
  margin-bottom: 14px;
  color: #1e3a5f;
  border-bottom: 2px solid #e5e7eb;
  padding-bottom: 8px;
}

/* ===== Contadores ===== */
.contadores { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 20px; }
.contador {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  border-left: 5px solid #ccc;
  text-align: center;
  transition: transform 0.2s;
}
.contador:hover { transform: translateY(-3px); }
.contador .num { font-size: 34px; font-weight: 800; color: #1e3a5f; }
.contador .lbl { font-size: 14px; color: #6b7280; margin-top: 4px; }
.contador.pend { border-left-color: #f59e0b; }
.contador.resol { border-left-color: #16a34a; }
.contador.total { border-left-color: #2563eb; }

/* ===== Formulário ===== */
.form-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; }
.form-grid .full { grid-column: 1 / -1; }
.form-grid .col2 { grid-column: span 2; }
label { display: block; font-size: 13px; font-weight: 600; color: #374151; margin-bottom: 4px; }
input, select, textarea {
  width: 100%;
  padding: 9px 11px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  font-family: inherit;
  transition: border-color 0.2s, box-shadow 0.2s;
}
input:focus, select:focus, textarea:focus {
  outline: none;
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37,99,235,0.15);
}
textarea { resize: vertical; min-height: 60px; }
.botoes { display: flex; gap: 10px; margin-top: 16px; flex-wrap: wrap; }
.btn {
  padding: 10px 18px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}
.btn:hover { transform: translateY(-1px); box-shadow: 0 3px 8px rgba(0,0,0,0.15); }
.btn-primary { background: #2563eb; color: #fff; }
.btn-secondary { background: #6b7280; color: #fff; }
.btn-danger { background: #dc2626; color: #fff; }
.btn-light { background: #dbeafe; color: #1e40af; }
.btn-pink { background: #fce7f3; color: #be185d; }

/* ===== Busca e filtros ===== */
.filtros { display: flex; gap: 10px; margin-bottom: 16px; flex-wrap: wrap; align-items: center; }
.filtros input[type=text] { max-width: 320px; }
.filtro-btn {
  padding: 8px 16px;
  border: 1px solid #d1d5db;
  background: #fff;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.2s;
}
.filtro-btn:hover { background: #f3f4f6; }
.filtro-btn.active { background: #2563eb; color: #fff; border-color: #2563eb; }

/* ===== Tabela ===== */
.tabela-wrap { overflow-x: auto; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
table { width: 100%; border-collapse: collapse; background: #fff; min-width: 900px; }
thead th {
  background: #1e3a5f;
  color: #fff;
  text-transform: uppercase;
  font-size: 12px;
  letter-spacing: 0.5px;
  padding: 12px 10px;
  text-align: left;
}
tbody td { padding: 11px 10px; border-bottom: 1px solid #e5e7eb; font-size: 14px; vertical-align: top; }
tbody tr:hover { background: #f9fafb; }
tbody tr.resolvido { opacity: 0.55; }
tbody tr.resolvido td { text-decoration: line-through; }
tbody tr.vencida { background: #fef2f2; }
tbody tr.vencida:hover { background: #fee2e2; }

/* ===== Badges ===== */
.badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
  white-space: nowrap;
}
.badge-alta { background: #fee2e2; color: #b91c1c; }
.badge-media { background: #fef9c3; color: #a16207; }
.badge-baixa { background: #dcfce7; color: #15803d; }
.badge-pendente { background: #fef3c7; color: #b45309; }
.badge-resolvido { background: #dcfce7; color: #15803d; }
.badge-vencida { background: #fee2e2; color: #b91c1c; }

/* ===== Ações ===== */
.acoes { display: flex; gap: 6px; }
.acoes button {
  padding: 6px 9px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: transform 0.15s;
}
.acoes button:hover { transform: scale(1.1); }
.btn-edit { background: #dbeafe; }
.btn-del { background: #fce7f3; }

/* ===== Dashboard KPIs ===== */
.kpis { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-bottom: 20px; }
.kpi {
  background: #fff;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  border-left: 5px solid #ccc;
}
.kpi .num { font-size: 28px; font-weight: 800; color: #1e3a5f; }
.kpi .lbl { font-size: 13px; color: #6b7280; margin-top: 2px; }
.kpi.blue { border-left-color: #2563eb; }
.kpi.yellow { border-left-color: #f59e0b; }
.kpi.green { border-left-color: #16a34a; }
.kpi.red { border-left-color: #dc2626; }
.kpi.orange { border-left-color: #ea580c; }
.kpi.purple { border-left-color: #7c3aed; }

/* ===== Barras de distribuição ===== */
.barra-item { margin-bottom: 12px; }
.barra-item .topo { display: flex; justify-content: space-between; font-size: 14px; margin-bottom: 4px; }
.barra-track { background: #e5e7eb; border-radius: 999px; height: 12px; overflow: hidden; }
.barra-fill { height: 100%; border-radius: 999px; transition: width 0.5s; }
.fill-alta { background: #dc2626; }
.fill-media { background: #f59e0b; }
.fill-baixa { background: #16a34a; }
.fill-cat { background: #2563eb; }

/* ===== Seções dashboard ===== */
.dash-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px; }
.lista-item {
  padding: 10px 12px;
  background: #f9fafb;
  border-radius: 8px;
  margin-bottom: 8px;
  font-size: 14px;
  border-left: 3px solid #2563eb;
}
.lista-item .nome { font-weight: 600; color: #1e3a5f; }
.lista-item .meta { font-size: 12px; color: #6b7280; margin-top: 2px; }

/* ===== Relatório ===== */
.relatorio-topo { display: flex; gap: 10px; align-items: center; margin-bottom: 16px; flex-wrap: wrap; }
.relatorio-topo select { max-width: 220px; }
.relatorio-info { font-size: 13px; color: #6b7280; margin-bottom: 12px; }

/* ===== Modal ===== */
.overlay {
  position: fixed; inset: 0;
  background: rgba(0,0,0,0.55);
  display: none;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 16px;
}
.overlay.show { display: flex; animation: fade 0.25s ease; }
@keyframes fade { from { opacity: 0; } to { opacity: 1; } }
.modal {
  background: #fff;
  border-radius: 14px;
  padding: 24px;
  max-width: 480px;
  width: 100%;
  box-shadow: 0 10px 40px rgba(0,0,0,0.3);
  animation: pop 0.25s ease;
}
@keyframes pop { from { transform: scale(0.92); opacity: 0; } to { transform: scale(1); opacity: 1; } }
.modal h3 { font-size: 20px; margin-bottom: 12px; }
.modal h3.alerta { color: #dc2626; }
.modal p, .modal li { font-size: 14px; color: #374151; margin-bottom: 6px; line-height: 1.5; }
.modal ul { margin: 10px 0 16px 18px; }
.modal-botoes { display: flex; gap: 10px; justify-content: flex-end; margin-top: 16px; }

/* ===== Seções/abas ===== */
.secao { display: none; padding: 24px 0; }
.secao.active { display: block; animation: fade 0.3s ease; }

/* ===== Responsivo ===== */
@media (max-width: 900px) {
  .kpis { grid-template-columns: repeat(2, 1fr); }
  .dash-grid { grid-template-columns: 1fr; }
}
@media (max-width: 700px) {
  .contadores { grid-template-columns: 1fr; }
  .form-grid { grid-template-columns: 1fr; }
  .form-grid .col2 { grid-column: span 1; }
  .header h1 { font-size: 22px; }
  .tab { padding: 8px 14px; font-size: 13px; }
}

/* ===== Print ===== */
@media print {
  .header, .tabs, .filtros, .form-grid, .botoes, .relatorio-topo, .acoes { display: none !important; }
  body { background: #fff; }
  .card { box-shadow: none; border: 1px solid #ddd; }
  .secao { display: block !important; }
}
</style>
</head>
<body>

<!-- ===== Header ===== -->
<header class="header">
  <div class="container">
    <h1>🛡️ Gerenciador de Tarefas</h1>
    <div class="sub">Coordenador de Segurança de Shopping</div>
    <nav class="tabs">
      <button class="tab active" onclick="mudarAba('tarefas', this)">📋 Tarefas</button>
      <button class="tab" onclick="mudarAba('dashboard', this)">📊 Dashboard</button>
      <button class="tab" onclick="mudarAba('relatorio', this)">📄 Relatório</button>
    </nav>
  </div>
</header>

<!-- ===== Aba Tarefas ===== -->
<section id="aba-tarefas" class="secao active">
  <div class="container">

    <!-- Contadores -->
    <div class="contadores">
      <div class="contador pend">
        <div class="num" id="cnt-pend">0</div>
        <div class="lbl">⏳ Pendentes</div>
      </div>
      <div class="contador resol">
        <div class="num" id="cnt-resol">0</div>
        <div class="lbl">✅ Resolvidas</div>
      </div>
      <div class="contador total">
        <div class="num" id="cnt-total">0</div>
        <div class="lbl">📋 Total</div>
      </div>
    </div>

    <!-- Formulário -->
    <div class="card">
      <h2 id="form-titulo">➕ Nova Tarefa</h2>
      <div class="form-grid">
        <div class="full">
          <label>Nome *</label>
          <textarea id="f-nome" placeholder="Digite o nome da tarefa..."></textarea>
        </div>
        <div class="full">
          <label>Descrição</label>
          <textarea id="f-desc" placeholder="Descrição detalhada (opcional)"></textarea>
        </div>
        <div>
          <label>Prioridade</label>
          <select id="f-prio">
            <option value="Baixa">🟢 Baixa</option>
            <option value="Média" selected>🟡 Média</option>
            <option value="Alta">🔴 Alta</option>
          </select>
        </div>
        <div>
          <label>Categoria</label>
          <select id="f-cat">
            <option value="Trabalho">Trabalho</option>
            <option value="Pessoal">Pessoal</option>
            <option value="Estudo">Estudo</option>
            <option value="Saúde">Saúde</option>
            <option value="Finanças">Finanças</option>
            <option value="Outros" selected>Outros</option>
          </select>
        </div>
        <div>
          <label>Data Vencimento</label>
          <input type="date" id="f-venc">
        </div>
        <div class="col2">
          <label>Responsável</label>
          <input type="text" id="f-resp" placeholder="Nome do responsável">
        </div>
      </div>
      <div class="botoes">
        <button class="btn btn-primary" onclick="salvarTarefa()">💾 Salvar</button>
        <button class="btn btn-secondary" onclick="cancelarEdicao()">↺ Cancelar</button>
        <button class="btn btn-danger" onclick="limparResolvidas()">🗑️ Limpar Resolvidas</button>
      </div>
    </div>

    <!-- Busca e filtros -->
    <div class="filtros">
      <input type="text" id="busca" placeholder="🔍 Buscar por nome..." oninput="carregarTarefas()">
      <button class="filtro-btn active" data-filtro="todas" onclick="setFiltro('todas', this)">Todas</button>
      <button class="filtro-btn" data-filtro="pendentes" onclick="setFiltro('pendentes', this)">⏳ Pendentes</button>
      <button class="filtro-btn" data-filtro="resolvidas" onclick="setFiltro('resolvidas', this)">✅ Resolvidas</button>
    </div>

    <!-- Tabela -->
    <div class="tabela-wrap">
      <table>
        <thead>
          <tr>
            <th style="width:40px">✓</th>
            <th>Nome</th>
            <th>Descrição</th>
            <th>Prioridade</th>
            <th>Categoria</th>
            <th>Vencimento</th>
            <th>Responsável</th>
            <th>Status</th>
            <th>Ações</th>
          </tr>
        </thead>
        <tbody id="corpo-tabela"></tbody>
      </table>
    </div>

  </div>
</section>

<!-- ===== Aba Dashboard ===== -->
<section id="aba-dashboard" class="secao">
  <div class="container">
    <div class="kpis" id="kpis"></div>

    <div class="dash-grid">
      <div class="card">
        <h2>🔴 Tarefas Vencidas</h2>
        <div id="dash-vencidas"></div>
      </div>
      <div class="card">
        <h2>📅 Próximos Vencimentos</h2>
        <div id="dash-proximas"></div>
      </div>
    </div>

    <div class="dash-grid">
      <div class="card">
        <h2>⚡ Distribuição por Prioridade</h2>
        <div id="dist-prioridade"></div>
      </div>
      <div class="card">
        <h2>🏷 Distribuição por Categoria</h2>
        <div id="dist-categoria"></div>
      </div>
    </div>
  </div>
</section>

<!-- ===== Aba Relatório ===== -->
<section id="aba-relatorio" class="secao">
  <div class="container">
    <div class="card">
      <h2>📄 Relatório de Tarefas</h2>
      <div class="relatorio-topo">
        <label>Tipo:</label>
        <select id="rel-tipo">
          <option value="completo">Completo</option>
          <option value="pendentes">Pendentes</option>
          <option value="resolvidas">Resolvidas</option>
          <option value="vencidas">Vencidas</option>
        </select>
        <button class="btn btn-primary" onclick="visualizarRelatorio()">👁️ Gerar Relatório</button>
        <button class="btn btn-light" onclick="window.print()">🖨 Imprimir</button>
      </div>
      <div class="relatorio-info" id="rel-info"></div>
      <div class="tabela-wrap">
        <table id="rel-tabela">
          <thead>
            <tr>
              <th>Nome</th><th>Prioridade</th><th>Categoria</th>
              <th>Vencimento</th><th>Responsável</th><th>Status</th>
            </tr>
          </thead>
          <tbody id="rel-corpo"></tbody>
        </table>
      </div>
    </div>
  </div>
</section>

<!-- ===== Modal de alerta ===== -->
<div class="overlay" id="overlay-alerta">
  <div class="modal">
    <h3 class="alerta">⚠️ Atenção!</h3>
    <p>Existem tarefas vencidas ou vencendo hoje:</p>
    <ul id="alerta-lista"></ul>
    <div class="modal-botoes">
      <button class="btn btn-primary" onclick="fecharModal('overlay-alerta')">Entendi</button>
    </div>
  </div>
</div>

<!-- ===== Modal de confirmação ===== -->
<div class="overlay" id="overlay-confirma">
  <div class="modal">
    <h3 id="confirma-titulo">Confirmação</h3>
    <p id="confirma-texto"></p>
    <div class="modal-botoes">
      <button class="btn btn-secondary" onclick="fecharModal('overlay-confirma')">Cancelar</button>
      <button class="btn btn-danger" id="confirma-ok">Confirmar</button>
    </div>
  </div>
</div>

<script>
/* ===== Estado global ===== */
let filtroAtual = 'todas';
let editandoId = null;

/* ===== Utilitários ===== */
function escapeHtml(s) {
  if (s === null || s === undefined) return '';
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function hojeStr() {
  const d = new Date();
  const a = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const dia = String(d.getDate()).padStart(2, '0');
  return `${a}-${m}-${dia}`;
}

function isVencida(t) {
  if (t.resolvido || !t.vencimento) return false;
  return t.vencimento < hojeStr();
}

function isHoje(t) {
  if (!t.vencimento) return false;
  return t.vencimento === hojeStr();
}

function formatarData(d) {
  if (!d) return '—';
  const parts = d.split('-');
  if (parts.length !== 3) return d;
  return `${parts[2]}/${parts[1]}/${parts[0]}`;
}

/* ===== Navegação por abas ===== */
function mudarAba(nome, btn) {
  document.querySelectorAll('.secao').forEach(s => s.classList.remove('active'));
  document.getElementById('aba-' + nome).classList.add('active');
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  btn.classList.add('active');
  if (nome === 'dashboard') renderDashboard();
}

/* ===== Modais ===== */
function abrirModal(id) { document.getElementById(id).classList.add('show'); }
function fecharModal(id) { document.getElementById(id).classList.remove('show'); }

function abrirConfirma(titulo, texto, callback) {
  document.getElementById('confirma-titulo').textContent = titulo;
  document.getElementById('confirma-texto').textContent = texto;
  const ok = document.getElementById('confirma-ok');
  // clonar para remover listeners antigos
  const novo = ok.cloneNode(true);
  ok.parentNode.replaceChild(novo, ok);
  novo.addEventListener('click', () => {
    fecharModal('overlay-confirma');
    callback();
  });
  abrirModal('overlay-confirma');
}

/* ===== Filtros ===== */
function setFiltro(f, btn) {
  filtroAtual = f;
  document.querySelectorAll('.filtro-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  carregarTarefas();
}

/* ===== Carregar tarefas ===== */
async function carregarTarefas() {
  try {
    const busca = document.getElementById('busca').value.trim();
    let url = '/api/tarefas?';
    if (filtroAtual !== 'todas') url += `filtro=${filtroAtual}&`;
    if (busca) url += `busca=${encodeURIComponent(busca)}&`;
    const resp = await fetch(url);
    const tarefas = await resp.json();
    renderTabela(tarefas);
    atualizarContadores(tarefas);
  } catch (e) {
    console.error('Erro ao carregar tarefas:', e);
  }
}

function atualizarContadores(tarefas) {
  // Para contadores precisos, buscar sempre totais sem filtro
  fetch('/api/tarefas')
    .then(r => r.json())
    .then(todas => {
      const pend = todas.filter(t => !t.resolvido).length;
      const resol = todas.filter(t => t.resolvido).length;
      document.getElementById('cnt-pend').textContent = pend;
      document.getElementById('cnt-resol').textContent = resol;
      document.getElementById('cnt-total').textContent = todas.length;
    });
}

function renderTabela(tarefas) {
  const tbody = document.getElementById('corpo-tabela');
  if (!tarefas.length) {
    tbody.innerHTML = '<tr><td colspan="9" style="text-align:center;color:#9ca3af;padding:24px">Nenhuma tarefa encontrada.</td></tr>';
    return;
  }
  tbody.innerHTML = tarefas.map(t => {
    const venc = isVencida(t);
    const hoje = isHoje(t) && !t.resolvido;
    const classes = [];
    if (t.resolvido) classes.push('resolvido');
    if (venc) classes.push('vencida');

    // Badge prioridade
    let bp = '';
    if (t.prioridade === 'Alta') bp = '<span class="badge badge-alta">🔴 Alta</span>';
    else if (t.prioridade === 'Média') bp = '<span class="badge badge-media">🟡 Média</span>';
    else bp = '<span class="badge badge-baixa">🟢 Baixa</span>';

    // Badge status
    let bs = '';
    if (t.resolvido) bs = '<span class="badge badge-resolvido">✅ Resolvido</span>';
    else if (venc) bs = '<span class="badge badge-vencida">🔴 Vencida</span>';
    else bs = '<span class="badge badge-pendente">⏳ Pendente</span>';

    return `<tr class="${classes.join(' ')}">
      <td><input type="checkbox" ${t.resolvido ? 'checked' : ''} onchange="toggleResolvido('${t.id}')"></td>
      <td><strong>${escapeHtml(t.nome)}</strong></td>
      <td>${escapeHtml(t.descricao)}</td>
      <td>${bp}</td>
      <td>${escapeHtml(t.categoria)}</td>
      <td>${formatarData(t.vencimento)}</td>
      <td>${escapeHtml(t.responsavel)}</td>
      <td>${bs}</td>
      <td><div class="acoes">
        <button class="btn-edit" onclick="editarTarefa('${t.id}')" title="Editar">✏️</button>
        <button class="btn-del" onclick="excluirTarefa('${t.id}')" title="Excluir">🗑️</button>
      </div></td>
    </tr>`;
  }).join('');
}

/* ===== Salvar / Editar ===== */
async function salvarTarefa() {
  const nome = document.getElementById('f-nome').value.trim();
  if (!nome) { alert('Informe o nome da tarefa.'); return; }
  const dados = {
    nome: nome,
    descricao: document.getElementById('f-desc').value.trim(),
    prioridade: document.getElementById('f-prio').value,
    categoria: document.getElementById('f-cat').value,
    vencimento: document.getElementById('f-venc').value,
    responsavel: document.getElementById('f-resp').value.trim(),
    resolvido: false
  };
  try {
    if (editandoId) {
      await fetch(`/api/tarefas/${editandoId}`, {
        method: 'PUT',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(dados)
      });
      editandoId = null;
      document.getElementById('form-titulo').textContent = '➕ Nova Tarefa';
    } else {
      await fetch('/api/tarefas', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(dados)
      });
    }
    limparForm();
    carregarTarefas();
  } catch (e) {
    console.error('Erro ao salvar:', e);
    alert('Erro ao salvar tarefa.');
  }
}

function limparForm() {
  document.getElementById('f-nome').value = '';
  document.getElementById('f-desc').value = '';
  document.getElementById('f-prio').value = 'Média';
  document.getElementById('f-cat').value = 'Outros';
  document.getElementById('f-venc').value = '';
  document.getElementById('f-resp').value = '';
}

function cancelarEdicao() {
  editandoId = null;
  document.getElementById('form-titulo').textContent = '➕ Nova Tarefa';
  limparForm();
}

async function editarTarefa(id) {
  try {
    const resp = await fetch('/api/tarefas');
    const tarefas = await resp.json();
    const t = tarefas.find(x => x.id === id);
    if (!t) return;
    editandoId = id;
    document.getElementById('form-titulo').textContent = '✏️ Editar Tarefa';
    document.getElementById('f-nome').value = t.nome;
    document.getElementById('f-desc').value = t.descricao || '';
    document.getElementById('f-prio').value = t.prioridade;
    document.getElementById('f-cat').value = t.categoria;
    document.getElementById('f-venc').value = t.vencimento || '';
    document.getElementById('f-resp').value = t.responsavel || '';
    window.scrollTo({ top: 0, behavior: 'smooth' });
  } catch (e) {
    console.error('Erro ao editar:', e);
  }
}

/* ===== Toggle resolvido ===== */
async function toggleResolvido(id) {
  try {
    await fetch(`/api/tarefas/${id}/toggle`, { method: 'PUT' });
    carregarTarefas();
  } catch (e) {
    console.error('Erro ao alternar:', e);
  }
}

/* ===== Excluir ===== */
function excluirTarefa(id) {
  abrirConfirma('Excluir Tarefa', 'Deseja realmente excluir esta tarefa? Esta ação não pode ser desfeita.', async () => {
    try {
      await fetch(`/api/tarefas/${id}`, { method: 'DELETE' });
      carregarTarefas();
    } catch (e) {
      console.error('Erro ao excluir:', e);
    }
  });
}

/* ===== Limpar resolvidas ===== */
function limparResolvidas() {
  abrirConfirma('Limpar Resolvidas', 'Deseja remover todas as tarefas resolvidas? Esta ação não pode ser desfeita.', async () => {
    try {
      await fetch('/api/tarefas/limpar-resolvidas', { method: 'DELETE' });
      carregarTarefas();
    } catch (e) {
      console.error('Erro ao limpar:', e);
    }
  });
}

/* ===== Dashboard ===== */
async function renderDashboard() {
  try {
    const resp = await fetch('/api/tarefas/dashboard');
    const d = await resp.json();

    // KPIs
    const kpis = [
      { lbl: 'Total', num: d.total, cls: 'blue' },
      { lbl: 'Pendentes', num: d.pendentes, cls: 'yellow' },
      { lbl: 'Resolvidas', num: d.resolvidas, cls: 'green' },
      { lbl: 'Vencidas', num: d.vencidas, cls: 'red' },
      { lbl: 'Vencem Hoje', num: d.vencem_hoje, cls: 'orange' },
      { lbl: 'Próx. 7 dias', num: d.proximas_7, cls: 'yellow' },
      { lbl: 'Taxa Conclusão', num: d.taxa_conclusao + '%', cls: 'purple' }
    ];
    document.getElementById('kpis').innerHTML = kpis.map(k =>
      `<div class="kpi ${k.cls}"><div class="num">${k.num}</div><div class="lbl">${k.lbl}</div></div>`
    ).join('');

    // Vencidas
    const venc = d.lista_vencidas || [];
    document.getElementById('dash-vencidas').innerHTML = venc.length
      ? '<div class="tabela-wrap"><table><thead><tr><th>Nome</th><th>Vencimento</th><th>Responsável</th></tr></thead><tbody>' +
        venc.map(t => `<tr><td>${escapeHtml(t.nome)}</td><td>${formatarData(t.vencimento)}</td><td>${escapeHtml(t.responsavel)}</td></tr>`).join('') +
        '</tbody></table></div>'
      : '<p style="color:#16a34a">✅ Nenhuma tarefa vencida.</p>';

    // Próximas
    const prox = d.lista_proximas || [];
    document.getElementById('dash-proximas').innerHTML = prox.length
      ? prox.map(t => `<div class="lista-item"><div class="nome">${escapeHtml(t.nome)}</div><div class="meta">📅 ${formatarData(t.vencimento)} • 👤 ${escapeHtml(t.responsavel || '—')}</div></div>`).join('')
      : '<p style="color:#6b7280">Nenhum vencimento nos próximos 7 dias.</p>';

    // Distribuição prioridade
    const dp = d.distribuicao_prioridade || {};
    const totalP = (dp['Alta']||0) + (dp['Média']||0) + (dp['Baixa']||0);
    document.getElementById('dist-prioridade').innerHTML = [
      { lbl: '🔴 Alta', val: dp['Alta']||0, cls: 'fill-alta' },
      { lbl: '🟡 Média', val: dp['Média']||0, cls: 'fill-media' },
      { lbl: '🟢 Baixa', val: dp['Baixa']||0, cls: 'fill-baixa' }
    ].map(i => {
      const pct = totalP ? Math.round(i.val / totalP * 100) : 0;
      return `<div class="barra-item"><div class="topo"><span>${i.lbl}</span><span>${i.val} (${pct}%)</span></div><div class="barra-track"><div class="barra-fill ${i.cls}" style="width:${pct}%"></div></div></div>`;
    }).join('');

    // Distribuição categoria
    const dc = d.distribuicao_categoria || {};
    const totalC = Object.values(dc).reduce((a,b) => a+b, 0);
    const catHtml = Object.keys(dc).map(cat => {
      const val = dc[cat];
      const pct = totalC ? Math.round(val / totalC * 100) : 0;
      return `<div class="barra-item"><div class="topo"><span>🏷 ${escapeHtml(cat)}</span><span>${val} (${pct}%)</span></div><div class="barra-track"><div class="barra-fill fill-cat" style="width:${pct}%"></div></div></div>`;
    }).join('');
    document.getElementById('dist-categoria').innerHTML = catHtml || '<p style="color:#6b7280">Sem dados.</p>';

  } catch (e) {
    console.error('Erro no dashboard:', e);
  }
}

/* ===== Relatório ===== */
async function visualizarRelatorio() {
  try {
    const tipo = document.getElementById('rel-tipo').value;
    const resp = await fetch(`/api/tarefas/relatorio?tipo=${tipo}`);
    const r = await resp.json();
    document.getElementById('rel-info').innerHTML =
      `Relatório <strong>${escapeHtml(r.tipo)}</strong> • ${r.quantidade} tarefa(s) • Gerado em ${new Date(r.gerado_em).toLocaleString('pt-BR')}`;
    const corpo = document.getElementById('rel-corpo');
    if (!r.tarefas.length) {
      corpo.innerHTML = '<tr><td colspan="6" style="text-align:center;color:#9ca3af;padding:20px">Nenhuma tarefa neste relatório.</td></tr>';
      return;
    }
    corpo.innerHTML = r.tarefas.map(t => {
      let bs = '';
      if (t.resolvido) bs = '<span class="badge badge-resolvido">✅ Resolvido</span>';
      else if (isVencida(t)) bs = '<span class="badge badge-vencida">🔴 Vencida</span>';
      else bs = '<span class="badge badge-pendente">⏳ Pendente</span>';
      return `<tr><td>${escapeHtml(t.nome)}</td><td>${escapeHtml(t.prioridade)}</td><td>${escapeHtml(t.categoria)}</td><td>${formatarData(t.vencimento)}</td><td>${escapeHtml(t.responsavel)}</td><td>${bs}</td></tr>`;
    }).join('');
  } catch (e) {
    console.error('Erro no relatório:', e);
  }
}

/* ===== Alerta de vencidas ao carregar ===== */
async function verificarAlertas() {
  try {
    const resp = await fetch('/api/tarefas');
    const tarefas = await resp.json();
    const alertas = tarefas.filter(t => (isVencida(t) || isHoje(t)) && !t.resolvido);
    if (alertas.length) {
      const lista = document.getElementById('alerta-lista');
      lista.innerHTML = alertas.map(t =>
        `<li><strong>${escapeHtml(t.nome)}</strong> — vencimento ${formatarData(t.vencimento)}${isVencida(t) ? ' (vencida)' : ' (hoje)'}</li>`
      ).join('');
      abrirModal('overlay-alerta');
    }
  } catch (e) {
    console.error('Erro ao verificar alertas:', e);
  }
}

/* ===== Inicialização ===== */
window.addEventListener('DOMContentLoaded', () => {
  carregarTarefas();
  verificarAlertas();
});
</script>
</body>
</html>
'''

# -----------------------------------------------------------------------------
# Execução
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
