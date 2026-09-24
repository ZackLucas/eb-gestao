"""Ponto de entrada da aplicação FastAPI."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import models  # noqa: F401  (registra os modelos no metadata)
from app.database import criar_tabelas
from app.routers import alunos, aulas, relatorios, turmas


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Cria as tabelas automaticamente na inicialização do servidor."""
    criar_tabelas()
    yield


app = FastAPI(
    title="EB Gestão",
    description="Sistema de gestão de Escola Bíblica.",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(turmas.router, prefix="/turmas", tags=["Turmas"])
app.include_router(alunos.router, prefix="/alunos", tags=["Alunos"])
app.include_router(aulas.router, prefix="/aulas", tags=["Aulas"])
app.include_router(relatorios.router, prefix="/relatorios", tags=["Relatórios"])


@app.get("/", tags=["Health"])
def raiz() -> dict[str, str]:
    """Rota de teste para confirmar que a API está no ar."""
    return {"status": "ok", "servico": "EB Gestão"}
