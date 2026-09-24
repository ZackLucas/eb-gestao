"""Modelos de dados do sistema de gestão da Escola Bíblica.

As aulas podem ocorrer em qualquer dia da semana, por isso `Turma.dia_semana`
é um campo livre (ex.: "Terça-feira", "Sábado") em vez de um enum de domingo.
"""

from datetime import date

from sqlmodel import Field, Relationship, SQLModel


class Turma(SQLModel, table=True):
    """Turma da Escola Bíblica (ex.: "Jovens", "Discipulado")."""

    __tablename__ = "turmas"

    id: int | None = Field(default=None, primary_key=True)
    nome: str = Field(index=True)
    dia_semana: str
    horario: str
    ativa: bool = Field(default=True)

    alunos: list["Aluno"] = Relationship(back_populates="turma")
    aulas: list["Aula"] = Relationship(back_populates="turma")


class Aluno(SQLModel, table=True):
    """Aluno matriculado em uma turma."""

    __tablename__ = "alunos"

    id: int | None = Field(default=None, primary_key=True)
    nome: str = Field(index=True)
    telefone: str | None = None
    turma_id: int = Field(foreign_key="turmas.id", index=True)
    ativo: bool = Field(default=True)

    turma: Turma | None = Relationship(back_populates="alunos")
    presencas: list["Presenca"] = Relationship(back_populates="aluno")


class Aula(SQLModel, table=True):
    """Aula ministrada para uma turma em uma data específica."""

    __tablename__ = "aulas"

    id: int | None = Field(default=None, primary_key=True)
    turma_id: int = Field(foreign_key="turmas.id", index=True)
    data: date = Field(default_factory=date.today, index=True)
    tema: str | None = None
    visitantes_qtd: int = Field(default=0, ge=0)

    turma: Turma | None = Relationship(back_populates="aulas")
    presencas: list["Presenca"] = Relationship(back_populates="aula")


class Presenca(SQLModel, table=True):
    """Registro de presença de um aluno em uma aula."""

    __tablename__ = "presencas"

    id: int | None = Field(default=None, primary_key=True)
    aula_id: int = Field(foreign_key="aulas.id", index=True)
    aluno_id: int = Field(foreign_key="alunos.id", index=True)
    presente: bool = Field(default=False)

    aula: Aula | None = Relationship(back_populates="presencas")
    aluno: Aluno | None = Relationship(back_populates="presencas")
