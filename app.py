import os
from datetime import datetime
from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Text
from sqlalchemy.orm import sessionmaker, declarative_base
import uvicorn

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./data.db")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Tarefa(Base):
    __tablename__ = "tarefas"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, default="")
    descricao = Column(Text, default="")
    prioridade = Column(String, default="Media")
    resolvido = Column(Boolean, default=False)


class Contato(Base):
    __tablename__ = "contatos"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, default="")
    email = Column(String, default="")
    telefone = Column(String, default="")


Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class TarefaSchema(BaseModel):
    nome: str = ""
    descricao: str = ""
    prioridade: str = "Media"
    resolvido: bool = False

    class Config:
        from_attributes = True


class ContatoSchema(BaseModel):
    nome: str = ""
    email: str = ""
    telefone: str = ""

    class Config:
        from_attributes = True


HTML_CONTENT = "<!DOCTYPE html>" + "\n" + \
"<html lang='pt-br'>" + "\n" + \
"<head>" + "\n" + \
"<meta charset='UTF-8'>" + "\n" + \
"<meta name='viewport' content='width=device-width, initial-scale=1.0'>" + "\n" + \
"<title>Sistema de Gestao</title>" + "\n" + \
"<style>" + "\n" + \
"body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; color: #333; }" + "\n" + \
"h1 { color: #2c3e50; }" + "\n" + \
"h2 { color: #34495e; border-bottom: 2px solid #ccc; padding-bottom: 5px; }" + "\n" + \
".card { background: #fff; padding: 15px; margin: 10px 0; border-radius: 5px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }" + "\n" + \
"input, textarea, button { padding: 8px; margin: 4px 0; width: 100%; box-sizing: border-box; }" + "\n" + \
"button { background: #3498db; color: #fff; border: none; cursor: pointer; border-radius: 3px; }" + "\n" + \
"button:hover { background: #2980b9; }" + "\n" + \
".item { padding: 8px; border-bottom: 1px solid #eee; }" + "\n" + \
".badge { padding: 2px 6px; border-radius: 3px; font-size: 12px; color: #fff; }" + "\n" + \
".alta { background: #e74c3c; }" + "\n" + \
".media { background: #f39c12; }" + "\n" + \
".baixa { background: #27ae60; }" + "\n" + \
"</style>" + "\n" + \
"</head>" + "\n" + \
"<body>" + "\n" + \
"<h1>Sistema de Gestao</h1>" + "\n" + \
"<p>Sistema funcionando!</p>" + "\n" + \
"<div class='card'>" + "\n" + \
"<h2>Nova Tarefa</h2>" + "\n" + \
"<input id='tNome' placeholder='Nome'>" + "\n" + \
"<textarea id='tDesc' placeholder='Descricao'></textarea>" + "\n" + \
"<select id='tPrio'><option>Alta</option><option selected>Media</option><option>Baixa</option></select>" + "\n" + \
"<button onclick='addTarefa()'>Adicionar Tarefa</button>" + "\n" + \
"</div>" + "\n" + \
"<div class='card'>" + "\n" + \
"<h2>Tarefas</h2>" + "\n" + \
"<div id='listaTarefas'></div>" + "\n" + \
"</div>" + "\n" + \
"<div class='card'>" + "\n" + \
"<h2>Novo Contato</h2>" + "\n" + \
"<input id='cNome' placeholder='Nome'>" + "\n" + \
"<input id='cEmail' placeholder='Email'>" + "\n" + \
"<input id='cTel' placeholder='Telefone'>" + "\n" + \
"<button onclick='addContato()'>Adicionar Contato</button>" + "\n" + \
"</div>" + "\n" + \
"<div class='card'>" + "\n" + \
"<h2>Contatos</h2>" + "\n" + \
"<div id='listaContatos'></div>" + "\n" + \
"</div>" + "\n" + \
"<script>" + "\n" + \
"function carregarTarefas() {" + "\n" + \
"  fetch('/api/tarefas').then(function(r){ return r.json(); }).then(function(data){" + "\n" + \
"    var html = '';" + "\n" + \
"    for (var i = 0; i < data.length; i++) {" + "\n" + \
"      var t = data[i];" + "\n" + \
"      var cls = t.prioridade.toLowerCase();" + "\n" + \
"      html += '<div class=\"item\"><span class=\"badge ' + cls + '\">' + t.prioridade + '</span> <b>' + t.nome + '</b> - ' + t.descricao + ' <button onclick=\"toggleTarefa(' + t.id + ')\">' + (t.resolvido ? 'Reabrir' : 'Resolver') + '</button> <button onclick=\"delTarefa(' + t.id + ')\">X</button></div>';" + "\n" + \
"    }" + "\n" + \
"    document.getElementById('listaTarefas').innerHTML = html;" + "\n" + \
"  });" + "\n" + \
"}" + "\n" + \
"function addTarefa() {" + "\n" + \
"  var body = JSON.stringify({ nome: document.getElementById('tNome').value, descricao: document.getElementById('tDesc').value, prioridade: document.getElementById('tPrio').value, resolvido: false });" + "\n" + \
"  fetch('/api/tarefas', { method: 'POST', headers: {'Content-Type':'application/json'}, body: body }).then(function(){ document.getElementById('tNome').value=''; document.getElementById('tDesc').value=''; carregarTarefas(); });" + "\n" + \
"}" + "\n" + \
"function toggleTarefa(id) {" + "\n" + \
"  fetch('/api/tarefas/' + id + '/toggle', { method: 'POST' }).then(function(){ carregarTarefas(); });" + "\n" + \
"}" + "\n" + \
"function delTarefa(id) {" + "\n" + \
"  fetch('/api/tarefas/' + id, { method: 'DELETE' }).then(function(){ carregarTarefas(); });" + "\n" + \
"}" + "\n" + \
"function carregarContatos() {" + "\n" + \
"  fetch('/api/contatos').then(function(r){ return r.json(); }).then(function(data){" + "\n" + \
"    var html = '';" + "\n" + \
"    for (var i = 0; i < data.length; i++) {" + "\n" + \
"      var c = data[i];" + "\n" + \
"      html += '<div class=\"item\"><b>' + c.nome + '</b> - ' + c.email + ' | ' + c.telefone + ' <button onclick=\"delContato(' + c.id + ')\">X</button></div>';" + "\n" + \
"    }" + "\n" + \
"    document.getElementById('listaContatos').innerHTML = html;" + "\n" + \
"  });" + "\n" + \
"}" + "\n" + \
"function addContato() {" + "\n" + \
"  var body = JSON.stringify({ nome: document.getElementById('cNome').value, email: document.getElementById('cEmail').value, telefone: document.getElementById('cTel').value });" + "\n" + \
"  fetch('/api/contatos', { method: 'POST', headers: {'Content-Type':'application/json'}, body: body }).then(function(){ document.getElementById('cNome').value=''; document.getElementById('cEmail').value=''; document.getElementById('cTel').value=''; carregarContatos(); });" + "\n" + \
"}" + "\n" + \
"function delContato(id) {" + "\n" + \
"  fetch('/api/contatos/' + id, { method: 'DELETE' }).then(function(){ carregarContatos(); });" + "\n" + \
"}" + "\n" + \
"carregarTarefas();" + "\n" + \
"carregarContatos();" + "\n" + \
"</script>" + "\n" + \
"</body>" + "\n" + \
"</html>"


@app.get("/", response_class=HTMLResponse)
def index():
    return HTML_CONTENT


@app.get("/api/tarefas")
def listar_tarefas(db=Depends(get_db)):
    itens = db.query(Tarefa).all()
    return [{"id": t.id, "nome": t.nome, "descricao": t.descricao, "prioridade": t.prioridade, "resolvido": t.resolvido} for t in itens]


@app.post("/api/tarefas")
def criar_tarefa(payload: TarefaSchema, db=Depends(get_db)):
    t = Tarefa(nome=payload.nome, descricao=payload.descricao, prioridade=payload.prioridade, resolvido=payload.resolvido)
    db.add(t)
    db.commit()
    db.refresh(t)
    return {"id": t.id, "nome": t.nome, "descricao": t.descricao, "prioridade": t.prioridade, "resolvido": t.resolvido}


@app.post("/api/tarefas/{tarefa_id}/toggle")
def toggle_tarefa(tarefa_id: int, db=Depends(get_db)):
    t = db.query(Tarefa).filter(Tarefa.id == tarefa_id).first()
    if t:
        t.resolvido = not t.resolvido
        db.commit()
        db.refresh(t)
    return {"id": t.id, "resolvido": t.resolvido}


@app.delete("/api/tarefas/{tarefa_id}")
def deletar_tarefa(tarefa_id: int, db=Depends(get_db)):
    t = db.query(Tarefa).filter(Tarefa.id == tarefa_id).first()
    if t:
        db.delete(t)
        db.commit()
    return {"ok": True}


@app.get("/api/contatos")
def listar_contatos(db=Depends(get_db)):
    itens = db.query(Contato).all()
    return [{"id": c.id, "nome": c.nome, "email": c.email, "telefone": c.telefone} for c in itens]


@app.post("/api/contatos")
def criar_contato(payload: ContatoSchema, db=Depends(get_db)):
    c = Contato(nome=payload.nome, email=payload.email, telefone=payload.telefone)
    db.add(c)
    db.commit()
    db.refresh(c)
    return {"id": c.id, "nome": c.nome, "email": c.email, "telefone": c.telefone}


@app.delete("/api/contatos/{contato_id}")
def deletar_contato(contato_id: int, db=Depends(get_db)):
    c = db.query(Contato).filter(Contato.id == contato_id).first()
    if c:
        db.delete(c)
        db.commit()
    return {"ok": True}


@app.get("/health")
def health():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
