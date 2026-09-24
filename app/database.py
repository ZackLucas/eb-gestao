"""Configuração da engine, criação de tabelas e sessão do banco de dados."""

from collections.abc import Generator

from sqlmodel import Session, SQLModel, create_engine

# Banco SQLite local. O arquivo `database.db` é criado no diretório de execução.
DATABASE_URL = "sqlite:///./database.db"

# `check_same_thread=False` é necessário porque o FastAPI pode executar
# requisições em threads diferentes da thread que abriu a conexão.
engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False},
)


def criar_tabelas() -> None:
    """Cria todas as tabelas registradas no metadata (operação idempotente)."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """Fornece uma sessão por requisição, garantindo o fechamento ao final."""
    with Session(engine) as session:
        yield session
