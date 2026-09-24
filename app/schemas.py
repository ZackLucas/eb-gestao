"""Schemas de entrada e saída da API.

Separados dos modelos de tabela (`app.models`) para não acoplar o contrato
da API ao esquema do banco de dados.
"""

from datetime import date

from sqlmodel import Field, SQLModel


# ---------------------------------------------------------------------------
# Turma
# ---------------------------------------------------------------------------
class TurmaCreate(SQLModel):
    nome: str
    dia_semana: str
    horario: str


class TurmaRead(SQLModel):
    id: int
    nome: str
    dia_semana: str
    horario: str
    ativa: bool


class TurmaUpdate(SQLModel):
    nome: str | None = None
    dia_semana: str | None = None
    horario: str | None = None
    ativa: bool | None = None


# ---------------------------------------------------------------------------
# Aluno
# ---------------------------------------------------------------------------
class AlunoCreate(SQLModel):
    nome: str
    telefone: str | None = None
    turma_id: int


class AlunoRead(SQLModel):
    id: int
    nome: str
    telefone: str | None = None
    turma_id: int
    ativo: bool


class AlunoUpdate(SQLModel):
    nome: str | None = None
    telefone: str | None = None
    turma_id: int | None = None
    ativo: bool | None = None


# ---------------------------------------------------------------------------
# Turma com alunos (depende de AlunoRead, por isso vem depois)
# ---------------------------------------------------------------------------
class TurmaComAlunosRead(TurmaRead):
    alunos: list[AlunoRead] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Aula
# ---------------------------------------------------------------------------
class AulaCreate(SQLModel):
    turma_id: int
    data: date = Field(default_factory=date.today)
    tema: str | None = None
    visitantes_qtd: int = 0


class AulaRead(SQLModel):
    id: int
    turma_id: int
    data: date
    tema: str | None = None
    visitantes_qtd: int


# ---------------------------------------------------------------------------
# Chamada / Presença
# ---------------------------------------------------------------------------
class ItemChamadaInput(SQLModel):
    aluno_id: int
    presente: bool


class ListaChamadaSubmit(SQLModel):
    itens: list[ItemChamadaInput]


class ItemChamadaAlunoRead(SQLModel):
    aluno_id: int
    nome_aluno: str
    presente: bool


# ---------------------------------------------------------------------------
# Relatórios
# ---------------------------------------------------------------------------
class FrequenciaAlunoRead(SQLModel):
    aluno_id: int
    nome_aluno: str
    turma_id: int
    total_aulas: int
    presencas: int
    percentual: float


class FrequenciaTurmaRead(SQLModel):
    turma_id: int
    nome_turma: str
    total_aulas: int
    total_alunos: int
    percentual_medio: float
    alunos: list[FrequenciaAlunoRead]
