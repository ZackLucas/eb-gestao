"""Endpoints de Alunos."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.database import get_session
from app.models import Aluno, Turma
from app.schemas import AlunoCreate, AlunoRead, AlunoUpdate

router = APIRouter()


@router.post("/", response_model=AlunoRead, status_code=status.HTTP_201_CREATED)
def criar_aluno(
    aluno: AlunoCreate,
    session: Session = Depends(get_session),
) -> Aluno:
    """Cadastra um aluno, validando se a turma informada existe."""
    if session.get(Turma, aluno.turma_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Turma não encontrada.",
        )

    db_aluno = Aluno.model_validate(aluno)
    session.add(db_aluno)
    session.commit()
    session.refresh(db_aluno)
    return db_aluno


@router.get("/", response_model=list[AlunoRead])
def listar_alunos(
    turma_id: int | None = None,
    apenas_ativos: bool = True,
    session: Session = Depends(get_session),
) -> list[Aluno]:
    """Lista alunos, com filtros opcionais por turma e por status ativo."""
    statement = select(Aluno)
    if turma_id is not None:
        statement = statement.where(Aluno.turma_id == turma_id)
    if apenas_ativos:
        statement = statement.where(Aluno.ativo.is_(True))
    return list(session.exec(statement).all())


@router.patch("/{aluno_id}", response_model=AlunoRead)
def atualizar_aluno(
    aluno_id: int,
    dados: AlunoUpdate,
    session: Session = Depends(get_session),
) -> Aluno:
    """Atualiza parcialmente um aluno (inclusive desativá-lo)."""
    aluno = session.get(Aluno, aluno_id)
    if aluno is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aluno não encontrado.",
        )

    dados_dict = dados.model_dump(exclude_unset=True)
    if "turma_id" in dados_dict and session.get(Turma, dados_dict["turma_id"]) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Turma não encontrada.",
        )

    aluno.sqlmodel_update(dados_dict)
    session.add(aluno)
    session.commit()
    session.refresh(aluno)
    return aluno
