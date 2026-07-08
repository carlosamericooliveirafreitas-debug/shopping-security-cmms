import os
from datetime import datetime
from fastapi import FastAPI, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Text
from sqlalchemy.orm import sessionmaker, declarative_base
import uvicorn

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./db.sqlite")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

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


Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


HTML_PAGE = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>Gestao</title>
</head>
<body style="font-family:Arial;padding:20px;background:#f5f5f5">
    <h1>Sistema de Gestao</h1>
    <h2>Tarefas</h2>
    <div id="tarefas"></div>
    <hr>
    <h3>Nova Tarefa</h3>
    <input id="nome" placeholder="Nome"><br>
    <textarea id="desc" placeholder="Descricao"></textarea><br>
    <select id="prio">
        <option value="Alta">Alta</option>
        <option value="Media" selected>Media</option>
        <option value="Baixa">Baixa</option>
    </select><br>
    <button onclick="add()">Adicionar</button>
    <script>
    function load(){
        fetch('/api/tarefas').then(function(r){return r.json();}).then(function(d){
            var h = '';
            d.forEach(function(t){
                h += '<div style="background:white;padding:10px;margin:5px;border-radius:5px">'
                    + '<strong>' + t.nome + '</strong> (' + t.prioridade + ') '
                    + t.descricao
                    + ' <button onclick="del(' + t.id + ')">X</button></div>';
            });
            document.getElementById('tarefas').innerHTML = h;
        });
    }
    function add(){
        var b = JSON.stringify({
            nome: document.getElementById('nome').value,
            descricao: document.getElementById('desc').value,
            prioridade: document.getElementById('prio').value
        });
        fetch('/api/tarefas', {method:'POST', headers:{'Content-Type':'application/json'}, body:b})
        .then(function(){ load(); });
    }
    function del(id){
        fetch('/api/tarefas/' + id, {method:'DELETE'}).then(function(){ load(); });
    }
    load();
    </script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
def index():
    return HTML_PAGE


@app.get("/health")
def health():
    return {"status": "ok", "versao": "1.0.0", "timestamp": datetime.utcnow().isoformat()}


@app.get("/api/tarefas")
def listar(db=Depends(get_db)):
    items = db.query(Tarefa).all()
    return [
        {
            "id": t.id,
            "nome": t.nome,
            "descricao": t.descricao,
            "prioridade": t.prioridade,
            "resolvido": t.resolvido,
        }
        for t in items
    ]


@app.post("/api/tarefas")
async def criar(request: Request, db=Depends(get_db)):
    data = await request.json()
    t = Tarefa(
        nome=data.get("nome", ""),
        descricao=data.get("descricao", ""),
        prioridade=data.get("prioridade", "Media"),
    )
    db.add(t)
    db.commit()
    db.refresh(t)
    return {
        "id": t.id,
        "nome": t.nome,
        "descricao": t.descricao,
        "prioridade": t.prioridade,
        "resolvido": t.resolvido,
    }


@app.delete("/api/tarefas/{id}")
def deletar(id: int, db=Depends(get_db)):
    t = db.query(Tarefa).filter(Tarefa.id == id).first()
    if t:
        db.delete(t)
        db.commit()
    return {"ok": True}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
