import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
def index():
    return "<h1>Funcionou!</h1><p>Sistema de Gestao de Seguranca</p>"

@app.get("/health")
def health():
    return {"status": "ok", "versao": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
