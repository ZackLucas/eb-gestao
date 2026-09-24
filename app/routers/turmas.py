"""Endpoints de Turmas."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.database import get_session
from app.models import Turma
from app.schemas import TurmaComAlunosRead, TurmaCreate, TurmaRead, TurmaUpdate

router = APIRouter()


@router.post("/", response_model=TurmaRead, status_code=status.HTTP_201_CREATED)
def criar_turma(
    turma: TurmaCreate,
    session: Session = Depends(get_session),
) -> Turma:
    """Cria uma nova turma."""
    db_turma = Turma.model_validate(turma)
    session.add(db_turma)
    session.commit()
    session.refresh(db_turma)
    return db_turma


@router.get("/", response_model=list[TurmaRead])
def listar_turmas(
    apenas_ativas: bool = True,
    session: Session = Depends(get_session),
) -> list[Turma]:
    """Lista turmas; por padrão retorna apenas as ativas."""
    statement = select(Turma)
    if apenas_ativas:
        statement = statement.where(Turma.ativa.is_(True))
    return list(session.exec(statement).all())


@router.get("/{turma_id}", response_model=TurmaComAlunosRead)
def obter_turma(
    turma_id: int,
    session: Session = Depends(get_session),
) -> Turma:
    """Retorna uma turma e seus alunos vinculados."""
    turma = session.get(Turma, turma_id)
    if turma is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Turma não encontrada.",
        )
    # Força o carregamento do relacionamento enquanto a sessão está aberta.
    _ = turma.alunos
    return turma


@router.patch("/{turma_id}", response_model=TurmaRead)
def atualizar_turma(
    turma_id: int,
    dados: TurmaUpdate,
    session: Session = Depends(get_session),
) -> Turma:
    """Atualiza parcialmente uma turma (inclusive desativá-la)."""
    turma = session.get(Turma, turma_id)
    if turma is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Turma não encontrada.",
        )

    turma.sqlmodel_update(dados.model_dump(exclude_unset=True))
    session.add(turma)
    session.commit()
    session.refresh(turma)
    return turma
