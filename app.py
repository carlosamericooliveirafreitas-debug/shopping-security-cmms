import os
import json
from datetime import datetime, date
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Date, DateTime, Text, ForeignKey, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
import uvicorn

# --- CONFIGURAÇÃO DO BANCO DE DADOS ---
DATABASE_URL = "sqlite:///./seguranca_shopping.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- MODELOS SQLALCHEMY ---

class Historico(Base):
    __tablename__ = "historico"
    id = Column(Integer, primary_key=True, index=True)
    modulo = Column(String)
    item_id = Column(Integer)
    acao = Column(String)
    data = Column(DateTime, default=datetime.now)
    observacoes = Column(Text)

class Extintor(Base):
    __tablename__ = "extintores"
    id = Column(Integer, primary_key=True, index=True)
    numero_extintor = Column(String)
    patrimonio = Column(String)
    classe_incendio = Column(String) # A, B, C, D, K, ABC, BC, Lítio
    tipo = Column(String) # CO2, Pó Químico, Água, Espuma
    capacidade = Column(String)
    fabricante = Column(String)
    numero_serie = Column(String)
    data_fabricacao = Column(String)
    data_teste_hidrostatico = Column(String)
    data_validade = Column(String)
    localizacao = Column(String)
    pavimento = Column(String)
    setor = Column(String)
    situacao = Column(String) # Conforme, Não Conforme, Inspecionar
    status = Column(String, default="Disponível") # Disponível, Alocado, Em Manutenção, Inativo
    observacoes = Column(Text)

class Mangueira(Base):
    __tablename__ = "mangueiras"
    id = Column(Integer, primary_key=True, index=True)
    numero_mangueira = Column(String)
    tipo = Column(String)
    comprimento = Column(String)
    diametro = Column(String)
    fabricante = Column(String)
    data_fabricacao = Column(String)
    data_ultimo_ensaio = Column(String)
    data_validade = Column(String)
    abrigo_hidrante = Column(String)
    situacao = Column(String)
    status = Column(String, default="Disponível")
    observacoes = Column(Text)

class VGA(Base):
    __tablename__ = "vgas"
    id = Column(Integer, primary_key=True, index=True)
    numero_vga = Column(String)
    localizacao = Column(String)
    pavimento = Column(String)
    vazao = Column(String)
    pressao = Column(String)
    data_ultima_inspecao = Column(String)
    situacao = Column(String)
    status = Column(String, default="Disponível")
    observacoes = Column(Text)

class Abrigo(Base):
    __tablename__ = "abrigos"
    id = Column(Integer, primary_key=True, index=True)
    codigo_abrigo = Column(String)
    localizacao = Column(String)
    pavimento = Column(String)
    setor = Column(String)
    tem_mangueira = Column(String)
    mangueira_alocada = Column(String)
    tem_chave_storz = Column(String)
    chave_storz_alocada = Column(String)
    tem_esguicho = Column(String)
    esguicho_alocada = Column(String)
    tem_tampao = Column(String)
    tampao_alocada = Column(String)
    tem_reducao = Column(String)
    reducao_alocada = Column(String)
    tem_adaptadores = Column(String)
    adaptadores_alocados = Column(String)
    tem_registro = Column(String)
    registro_status = Column(String)
    tem_sinalizacao = Column(String)
    observacoes = Column(Text)

class OutroEquipamento(Base):
    __tablename__ = "outros_equipamentos"
    id = Column(Integer, primary_key=True, index=True)
    tipo_equipamento = Column(String)
    patrimonio = Column(String)
    localizacao = Column(String)
    data_validade = Column(String)
    situacao = Column(String)
    status = Column(String, default="Disponível")
    observacoes = Column(Text)

class KitCrise(Base):
    __tablename__ = "kit_crise"
    id = Column(Integer, primary_key=True, index=True)
    item = Column(String)
    quantidade = Column(String)
    localizacao = Column(String)
    responsavel = Column(String)
    situacao = Column(String)
    validade = Column(String)

class SDAI(Base):
    __tablename__ = "sdai"
    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String)
    central_alarme = Column(String)
    acionadores_manuais = Column(String)
    detectores = Column(String)
    sirenes = Column(String)
    modulos = Column(String)
    fontes = Column(String)
    baterias = Column(String)
    loop = Column(String)
    enderecamento = Column(String)
    data_ultimo_teste = Column(String)
    falhas = Column(Text)
    observacoes = Column(Text)

class CFTV(Base):
    __tablename__ = "cftv"
    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String)
    tipo = Column(String)
    marca = Column(String)
    modelo = Column(String)
    ip = Column(String)
    localizacao = Column(String)
    estado = Column(String)
    garantia = Column(String)
    data_manutencao = Column(String)
    observacoes = Column(Text)

class Loja(Base):
    __tablename__ = "lojas"
    id = Column(Integer, primary_key=True, index=True)
    nome_loja = Column(String)
    numero = Column(String)
    segmento = Column(String)
    responsavel = Column(String)
    telefone = Column(String)
    email = Column(String)
    hidrantes = Column(String)
    problemas_encontrados = Column(Text)
    data_vistoria = Column(String)
    grau_risco = Column(String)
    observacoes = Column(Text)

class EscadaEmergencia(Base):
    __tablename__ = "escadas"
    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String)
    pavimento = Column(String)
    quantidade_portas = Column(Integer)
    barra_antipanico = Column(String)
    fechadura = Column(String)
    molas = Column(String)
    sinalizacao = Column(String)
    situacao = Column(String)
    data_inspecao = Column(String)
    observacoes = Column(Text)

class Tarefa(Base):
    __tablename__ = "tarefas"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String)
    descricao = Column(Text)
    prioridade = Column(String)
    categoria = Column(String)
    vencimento = Column(String)
    responsavel = Column(String)
    resolvido = Column(Boolean, default=False)
    criado_em = Column(DateTime, default=datetime.now)
    concluido_em = Column(DateTime, nullable=True)

class Time(Base):
    __tablename__ = "times"
    id = Column(Integer, primary_key=True, index=True)
    categoria = Column(String) # interno, terceiro
    nome = Column(String)
    cargo = Column(String)
    empresa = Column(String)
    certificados = Column(String)
    data_validade_certificado = Column(String)
    telefone = Column(String)
    email = Column(String)
    escala = Column(String)
    observacoes = Column(Text)

class Documento(Base):
    __tablename__ = "documentos"
    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String)
    tipo = Column(String)
    data_emissao = Column(String)
    data_validade = Column(String)
    orgao_emissor = Column(String)
    arquivo_url = Column(String)
    observacoes = Column(Text)

class Ocorrencia(Base):
    __tablename__ = "ocorrencias"
    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(String)
    data = Column(String)
    hora = Column(String)
    local = Column(String)
    descricao = Column(Text)
    responsavel = Column(String)
    providencias = Column(Text)
    status = Column(String, default="aberto")

class Contato(Base):
    __tablename__ = "contatos"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String)
    telefone = Column(String)
    email = Column(String)
    empresa = Column(String)
    funcao = Column(String)
    observacoes = Column(Text)

Base.metadata.create_all(bind=engine)

# --- APP FASTAPI ---
app = FastAPI(title="Gestão de Segurança Shopping")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- HELPER FUNCTIONS ---
def log_movimentacao(db: Session, modulo: str, item_id: int, acao: str, obs: str = ""):
    hist = Historico(modulo=modulo, item_id=item_id, acao=acao, observacoes=obs)
    db.add(hist)
    db.commit()

# --- API ENDPOINTS (GENERIC CRUD PATTERN) ---

def create_crud_routes(model_class, prefix, schema_class):
    @app.get(f"/api/{prefix}")
    def list_items(status: Optional[str] = None, db: Session = Depends(get_db)):
        query = db.query(model_class)
        if status and hasattr(model_class, 'status'):
            query = query.filter(model_class.status == status)
        return query.all()

    @app.post(f"/api/{prefix}")
    def create_item(data: dict, db: Session = Depends(get_db)):
        item = model_class(**data)
        db.add(item)
        db.commit()
        db.refresh(item)
        log_movimentacao(db, prefix, item.id, "Criação")
        return item

    @app.put(f"/api/{prefix}/{{id}}")
    def update_item(id: int, data: dict, db: Session = Depends(get_db)):
        item = db.query(model_class).filter(model_class.id == id).first()
        if not item: raise HTTPException(404)
        
        # Check for status change logic
        old_status = getattr(item, 'status', None)
        for key, value in data.items():
            setattr(item, key, value)
        
        new_status = getattr(item, 'status', None)
        if old_status != new_status:
            log_movimentacao(db, prefix, id, f"Status alterado de {old_status} para {new_status}")
            
        db.commit()
        db.refresh(item)
        return item

    @app.delete(f"/api/{prefix}/{{id}}")
    def delete_item(id: int, db: Session = Depends(get_db)):
        item = db.query(model_class).filter(model_class.id == id).first()
        if not item: raise HTTPException(404)
        db.delete(item)
        db.commit()
        return {"status": "deleted"}

    @app.post(f"/api/{prefix}/{{id}}/duplicar")
    def duplicate_item(id: int, db: Session = Depends(get_db)):
        item = db.query(model_class).filter(model_class.id == id).first()
        if not item: raise HTTPException(404)
        
        data = {c.name: getattr(item, c.name) for c in item.__table__.columns if c.name != 'id'}
        if 'patrimonio' in data: data['patrimonio'] = ""
        
        new_item = model_class(**data)
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
        log_movimentacao(db, prefix, new_item.id, f"Duplicado do ID {id}")
        return new_item

# Registering CRUDs
create_crud_routes(Extintor, "extintores", None)
create_crud_routes(Mangueira, "mangueiras", None)
create_crud_routes(VGA, "vgas", None)
create_crud_routes(Abrigo, "abrigos", None)
create_crud_routes(OutroEquipamento, "outros_equipamentos", None)
create_crud_routes(KitCrise, "kit_crise", None)
create_crud_routes(SDAI, "sdai", None)
create_crud_routes(CFTV, "cftv", None)
create_crud_routes(Loja, "lojas", None)
create_crud_routes(EscadaEmergencia, "escadas", None)
create_crud_routes(Tarefa, "tarefas", None)
create_crud_routes(Time, "times", None)
create_crud_routes(Documento, "documentos", None)
create_crud_routes(Ocorrencia, "ocorrencias", None)
create_crud_routes(Contato, "contatos", None)

# --- SPECIAL ENDPOINTS ---

@app.get("/api/dashboard")
def get_dashboard_stats(db: Session = Depends(get_db)):
    today = date.today().isoformat()
    
    # Basic counts
    stats = {
        "total_equipamentos": db.query(Extintor).count() + db.query(Mangueira).count() + db.query(VGA).count() + db.query(OutroEquipamento).count(),
        "tarefas_pendentes": db.query(Tarefa).filter(Tarefa.resolvido == False).count(),
        "vencidos": 0,
        "alertas": [],
        "ultimos_registros": []
    }
    
    # Check expirations in various modules
    # Extintores
    ext_vencidos = db.query(Extintor).filter(Extintor.data_validade < today).all()
    for e in ext_vencidos:
        stats["alertas"].append({"msg": f"Extintor {e.numero_extintor} vencido", "modulo": "extintores", "id": e.id})
    
    # Mangueiras
    man_vencidos = db.query(Mangueira).filter(Mangueira.data_validade < today).all()
    for m in man_vencidos:
        stats["alertas"].append({"msg": f"Mangueira {m.numero_mangueira} vencida", "modulo": "mangueiras", "id": m.id})

    # Documentos
    doc_vencidos = db.query(Documento).filter(Documento.data_validade < today).all()
    for d in doc_vencidos:
        stats["alertas"].append({"msg": f"Documento {d.titulo} vencido", "modulo": "documentos", "id": d.id})

    stats["vencidos"] = len(stats["alertas"])
    
    # Last 5 history
    stats["ultimos_registros"] = db.query(Historico).order_by(Historico.data.desc()).limit(5).all()
    
    return stats

@app.put("/api/abrigos/{id}/alocar")
def alocar_equipamento_abrigo(id: int, data: dict, db: Session = Depends(get_db)):
    abrigo = db.query(Abrigo).filter(Abrigo.id == id).first()
    if not abrigo: raise HTTPException(404)
    
    # Logic: if mangueira_alocada is provided, find that mangueira and set status to Alocado
    if "mangueira_alocada" in data and data["mangueira_alocada"]:
        m = db.query(Mangueira).filter(Mangueira.numero_mangueira == data["mangueira_alocada"]).first()
        if m: m.status = "Alocado"
    
    for k, v in data.items():
        setattr(abrigo, k, v)
    
    db.commit()
    return abrigo

# --- FRONTEND HTML ---

HTML_CONTENT = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gestão de Segurança - Shopping Center</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body { background-color: #f0f2f5; font-family: 'Inter', sans-serif; }
        .header-gradient { background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 100%); }
        .tab-active { border-bottom: 4px solid #3b82f6; color: #3b82f6; font-weight: bold; }
        .card { background: white; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
        .scroll-x { overflow-x: auto; white-space: nowrap; }
        .status-badge { padding: 2px 8px; border-radius: 12px; font-size: 0.75rem; font-weight: 600; }
        .status-disponivel { background: #dcfce7; color: #166534; }
        .status-alocado { background: #dbeafe; color: #1e40af; }
        .status-manutencao { background: #fef3c7; color: #92400e; }
        .status-inativo { background: #f3f4f6; color: #374151; }
    </style>
</head>
<body>

<div id="app">
    <!-- Header -->
    <header class="header-gradient text-white p-6 shadow-lg">
        <div class="container mx-auto flex flex-col md:flex-row justify-between items-center">
            <div>
                <h1 class="text-2xl font-bold">🛡️ Gestão de Segurança - Shopping Center</h1>
                <p class="text-blue-200 text-sm">Sistema Integrado de Segurança Patrimonial</p>
            </div>
            <div class="mt-4 md:mt-0">
                <span id="clock" class="text-lg font-mono"></span>
            </div>
        </div>
    </header>

    <!-- Navigation Tabs -->
    <nav class="bg-white border-b sticky top-0 z-40">
        <div class="container mx-auto scroll-x px-4">
            <div class="flex space-x-6 py-3">
                <button onclick="setTab('dashboard')" class="nav-link" id="tab-dashboard">📊 PAINEL</button>
                <div class="h-6 w-px bg-gray-300"></div>
                <button onclick="setTab('extintores')" class="nav-link" id="tab-extintores">🧯 Extintores</button>
                <button onclick="setTab('mangueiras')" class="nav-link" id="tab-mangueiras">🔥 Mangueiras</button>
                <button onclick="setTab('vgas')" class="nav-link" id="tab-vgas">💧 VGAs</button>
                <button onclick="setTab('abrigos')" class="nav-link" id="tab-abrigos">🚪 Abrigos</button>
                <button onclick="setTab('outros_equipamentos')" class="nav-link" id="tab-outros_equipamentos">🔧 Outros</button>
                <button onclick="setTab('kit_crise')" class="nav-link" id="tab-kit_crise">🆘 Kit Crise</button>
                <button onclick="setTab('sdai')" class="nav-link" id="tab-sdai">🚨 SDAI</button>
                <button onclick="setTab('cftv')" class="nav-link" id="tab-cftv">📹 CFTV</button>
                <div class="h-6 w-px bg-gray-300"></div>
                <button onclick="setTab('lojas')" class="nav-link" id="tab-lojas">🏪 Lojas</button>
                <button onclick="setTab('escadas')" class="nav-link" id="tab-escadas">🪜 Escadas</button>
                <button onclick="setTab('tarefas')" class="nav-link" id="tab-tarefas">📋 Tarefas</button>
                <button onclick="setTab('times')" class="nav-link" id="tab-times">👥 Times</button>
                <button onclick="setTab('documentos')" class="nav-link" id="tab-documentos">📄 Documentos</button>
                <button onclick="setTab('ocorrencias')" class="nav-link" id="tab-ocorrencias">📝 Ocorrências</button>
                <button onclick="setTab('contatos')" class="nav-link" id="tab-contatos">📞 Contatos</button>
            </div>
        </div>
    </nav>

    <!-- Main Content -->
    <main class="container mx-auto p-6">
        <div id="view-container"></div>
    </main>

    <!-- Modal Generic -->
    <div id="modal" class="fixed inset-0 bg-black bg-opacity-50 hidden flex items-center justify-center z-50">
        <div class="bg-white rounded-xl p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div class="flex justify-between items-center mb-4">
                <h3 id="modal-title" class="text-xl font-bold"></h3>
                <button onclick="closeModal()" class="text-gray-500 hover:text-black"><i class="fa fa-times"></i></button>
            </div>
            <div id="modal-body"></div>
        </div>
    </div>
</div>

<script>
    let currentTab = 'dashboard';
    let apiData = {};

    async function fetchData(endpoint) {
        const res = await fetch(`/api/${endpoint}`);
        return await res.json();
    }

    function setTab(tab) {
        currentTab = tab;
        document.querySelectorAll('.nav-link').forEach(el => el.classList.remove('tab-active'));
        const activeTab = document.getElementById(`tab-${tab}`);
        if(activeTab) activeTab.classList.add('tab-active');
        renderView();
    }

    async function renderView() {
        const container = document.getElementById('view-container');
        container.innerHTML = '<div class="text-center py-10"><i class="fa fa-spinner fa-spin text-4xl text-blue-600"></i></div>';

        if (currentTab === 'dashboard') {
            const stats = await fetchData('dashboard');
            container.innerHTML = `
                <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                    <div class="card p-6 border-l-4 border-blue-500">
                        <p class="text-gray-500 text-sm uppercase font-bold">Total Equipamentos</p>
                        <h2 class="text-3xl font-bold">${stats.total_equipamentos}</h2>
                    </div>
                    <div class="card p-6 border-l-4 border-red-500">
                        <p class="text-gray-500 text-sm uppercase font-bold">Vencidos</p>
                        <h2 class="text-3xl font-bold text-red-600">${stats.vencidos}</h2>
                    </div>
                    <div class="card p-6 border-l-4 border-yellow-500">
                        <p class="text-gray-500 text-sm uppercase font-bold">Tarefas Pendentes</p>
                        <h2 class="text-3xl font-bold">${stats.tarefas_pendentes}</h2>
                    </div>
                    <div class="card p-6 border-l-4 border-green-500">
                        <p class="text-gray-500 text-sm uppercase font-bold">Status Sistema</p>
                        <h2 class="text-3xl font-bold text-green-600">OK</h2>
                    </div>
                </div>

                <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    <div class="card p-6">
                        <h3 class="text-lg font-bold mb-4"><i class="fa fa-bell text-red-500 mr-2"></i> Alertas Críticos</h3>
                        <div class="space-y-3">
                            ${stats.alertas.length ? stats.alertas.map(a => `
                                <div onclick="setTab('${a.modulo}')" class="p-3 bg-red-50 border border-red-100 rounded-lg flex justify-between items-center cursor-pointer hover:bg-red-100">
                                    <span class="text-red-800 font-medium">${a.msg}</span>
                                    <i class="fa fa-chevron-right text-red-400"></i>
                                </div>
                            `).join('') : '<p class="text-gray-400">Nenhum alerta no momento.</p>'}
                        </div>
                    </div>
                    <div class="card p-6">
                        <h3 class="text-lg font-bold mb-4"><i class="fa fa-history text-blue-500 mr-2"></i> Últimas Movimentações</h3>
                        <div class="overflow-x-auto">
                            <table class="w-full text-sm">
                                <thead><tr class="text-left border-b"><th>Data</th><th>Módulo</th><th>Ação</th></tr></thead>
                                <tbody>
                                    ${stats.ultimos_registros.map(r => `
                                        <tr class="border-b">
                                            <td class="py-2">${new Date(r.data).toLocaleString()}</td>
                                            <td>${r.modulo}</td>
                                            <td>${r.acao}</td>
                                        </tr>
                                    `).join('')}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            `;
        } else {
            // Generic Module View
            const items = await fetchData(currentTab);
            const columns = getColumnsForTab(currentTab);
            
            container.innerHTML = `
                <div class="flex justify-between items-center mb-6">
                    <h2 class="text-2xl font-bold capitalize">${currentTab.replace('_', ' ')} (${items.length})</h2>
                    <div class="space-x-2">
                        <button onclick="openForm()" class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"><i class="fa fa-plus mr-2"></i> Adicionar</button>
                    </div>
                </div>
                
                <div class="card overflow-hidden">
                    <div class="overflow-x-auto">
                        <table class="w-full text-left">
                            <thead class="bg-slate-800 text-white">
                                <tr>
                                    ${columns.map(c => `<th class="px-4 py-3">${c.label}</th>`).join('')}
                                    <th class="px-4 py-3">Ações</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${items.map(item => `
                                    <tr class="border-b hover:bg-gray-50">
                                        ${columns.map(c => `<td class="px-4 py-3">${formatCell(item[c.key], c.key)}</td>`).join('')}
                                        <td class="px-4 py-3 space-x-2">
                                            <button onclick="editItem(${item.id})" class="text-blue-600"><i class="fa fa-edit"></i></button>
                                            <button onclick="duplicateItem(${item.id})" class="text-green-600"><i class="fa fa-copy"></i></button>
                                            <button onclick="deleteItem(${item.id})" class="text-red-600"><i class="fa fa-trash"></i></button>
                                        </td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                </div>
            `;
        }
    }

    function formatCell(val, key) {
        if (key === 'status') {
            const cls = val === 'Disponível' ? 'status-disponivel' : val === 'Alocado' ? 'status-alocado' : val === 'Em Manutenção' ? 'status-manutencao' : 'status-inativo';
            return `<span class="status-badge ${cls}">${val}</span>`;
        }
        if (key === 'prioridade') {
            const colors = { 'Alta': 'text-red-600', 'Média': 'text-yellow-600', 'Baixa': 'text-green-600' };
            return `<span class="font-bold ${colors[val] || ''}">${val}</span>`;
        }
        return val || '-';
    }

    function getColumnsForTab(tab) {
        const cols = {
            extintores: [{key:'numero_extintor', label:'Nº'}, {key:'tipo', label:'Tipo'}, {key:'capacidade', label:'Cap.'}, {key:'data_validade', label:'Validade'}, {key:'localizacao', label:'Local'}, {key:'status', label:'Status'}],
            mangueiras: [{key:'numero_mangueira', label:'Nº'}, {key:'tipo', label:'Tipo'}, {key:'comprimento', label:'Comp.'}, {key:'data_validade', label:'Validade'}, {key:'status', label:'Status'}],
            vgas: [{key:'numero_vga', label:'Nº'}, {key:'localizacao', label:'Local'}, {key:'pressao', label:'Pressão'}, {key:'situacao', label:'Situação'}],
            abrigos: [{key:'codigo_abrigo', label:'Código'}, {key:'localizacao', label:'Local'}, {key:'mangueira_alocada', label:'Mangueira'}],
            outros_equipamentos: [{key:'tipo_equipamento', label:'Tipo'}, {key:'patrimonio', label:'Patrimônio'}, {key:'data_validade', label:'Validade'}, {key:'status', label:'Status'}],
            tarefas: [{key:'nome', label:'Tarefa'}, {key:'prioridade', label:'Prioridade'}, {key:'responsavel', label:'Resp.'}, {key:'vencimento', label:'Vencimento'}],
            times: [{key:'nome', label:'Nome'}, {key:'cargo', label:'Cargo'}, {key:'empresa', label:'Empresa'}, {key:'data_validade_certificado', label:'Cert. Validade'}],
            documentos: [{key:'titulo', label:'Título'}, {key:'tipo', label:'Tipo'}, {key:'data_validade', label:'Validade'}],
            ocorrencias: [{key:'tipo', label:'Tipo'}, {key:'data', label:'Data'}, {key:'local', label:'Local'}, {key:'status', label:'Status'}]
        };
        return cols[tab] || [{key:'id', label:'ID'}];
    }

    async function deleteItem(id) {
        if(confirm('Deseja realmente excluir?')) {
            await fetch(`/api/${currentTab}/${id}`, { method: 'DELETE' });
            renderView();
        }
    }

    async function duplicateItem(id) {
        await fetch(`/api/${currentTab}/${id}/duplicar`, { method: 'POST' });
        renderView();
    }

    function openForm(item = null) {
        const modal = document.getElementById('modal');
        const title = document.getElementById('modal-title');
        const body = document.getElementById('modal-body');
        
        title.innerText = item ? 'Editar Registro' : 'Novo Registro';
        
        // Dynamic Form Generation based on columns (simplified for demo)
        const fields = getFieldsForTab(currentTab);
        body.innerHTML = `
            <form id="item-form" class="grid grid-cols-1 md:grid-cols-2 gap-4">
                ${fields.map(f => `
                    <div>
                        <label class="block text-sm font-bold mb-1">${f.label}</label>
                        ${f.type === 'select' ? `
                            <select name="${f.key}" class="w-full border p-2 rounded">
                                ${f.options.map(o => `<option value="${o}" ${item && item[f.key] == o ? 'selected' : ''}>${o}</option>`).join('')}
                            </select>
                        ` : `
                            <input type="${f.type || 'text'}" name="${f.key}" value="${item ? item[f.key] || '' : ''}" class="w-full border p-2 rounded">
                        `}
                    </div>
                `).join('')}
                <div class="md:col-span-2 mt-4">
                    <button type="submit" class="w-full bg-blue-600 text-white py-3 rounded-lg font-bold">SALVAR</button>
                </div>
            </form>
        `;

        document.getElementById('item-form').onsubmit = async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const data = Object.fromEntries(formData.entries());
            
            const url = item ? `/api/${currentTab}/${item.id}` : `/api/${currentTab}`;
            const method = item ? 'PUT' : 'POST';

            await fetch(url, {
                method: method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            closeModal();
            renderView();
        };

        modal.classList.remove('hidden');
    }

    async function editItem(id) {
        const items = await fetchData(currentTab);
        const item = items.find(i => i.id === id);
        openForm(item);
    }

    function closeModal() {
        document.getElementById('modal').classList.add('hidden');
    }

    function getFieldsForTab(tab) {
        // Simplified field definitions
        const commonStatus = ['Disponível', 'Alocado', 'Em Manutenção', 'Inativo'];
        if (tab === 'extintores') return [
            {key:'numero_extintor', label:'Número Extintor'}, {key:'patrimonio', label:'Patrimônio'},
            {key:'classe_incendio', label:'Classe', type:'select', options:['A','B','C','ABC','BC','K','D','Lítio']},
            {key:'tipo', label:'Tipo', type:'select', options:['CO2','Pó Químico','Água','Espuma']},
            {key:'capacidade', label:'Capacidade'}, {key:'data_validade', label:'Validade', type:'date'},
            {key:'localizacao', label:'Localização'}, {key:'status', label:'Status', type:'select', options:commonStatus}
        ];
        if (tab === 'tarefas') return [
            {key:'nome', label:'Título'}, {key:'descricao', label:'Descrição'},
            {key:'prioridade', label:'Prioridade', type:'select', options:['Baixa','Média','Alta']},
            {key:'vencimento', label:'Vencimento', type:'date'}, {key:'responsavel', label:'Responsável'}
        ];
        // Fallback for other tabs
        return getColumnsForTab(tab).map(c => ({key: c.key, label: c.label}));
    }

    function updateClock() {
        const now = new Date();
        document.getElementById('clock').innerText = now.toLocaleTimeString();
    }

    setInterval(updateClock, 1000);
    updateClock();
    setTab('dashboard');

    // Initial Alert Check
    window.onload = async () => {
        const stats = await fetchData('dashboard');
        if (stats.vencidos > 0) {
            alert(`Atenção: Existem ${stats.vencidos} itens com validade vencida no sistema!`);
        }
    };
</script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def serve_index():
    if os.path.exists("index.html"):
        return FileResponse("index.html")
    return HTML_CONTENT

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
