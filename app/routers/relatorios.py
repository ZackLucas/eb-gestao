"""Endpoints de relatórios de frequência."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, func, select

from app.database import get_session
from app.models import Aluno, Aula, Presenca, Turma
from app.schemas import FrequenciaAlunoRead, FrequenciaTurmaRead

router = APIRouter()


def _total_aulas(session: Session, turma_id: int) -> int:
    """Quantidade de aulas registradas para uma turma."""
    return session.exec(
        select(func.count()).select_from(Aula).where(Aula.turma_id == turma_id)
    ).one()


def _contagens_presenca(session: Session, turma_id: int) -> dict[int, int]:
    """Presenças confirmadas por aluno (`aluno_id` -> quantidade)."""
    linhas = session.exec(
        select(Presenca.aluno_id, func.count())
        .join(Aula, Presenca.aula_id == Aula.id)
        .where(Aula.turma_id == turma_id)
        .where(Presenca.presente.is_(True))
        .group_by(Presenca.aluno_id)
    ).all()
    return {aluno_id: total for aluno_id, total in linhas}


def _montar_frequencia(
    aluno: Aluno,
    total_aulas: int,
    presencas: int,
) -> FrequenciaAlunoRead:
    percentual = round(presencas / total_aulas * 100, 2) if total_aulas else 0.0
    return FrequenciaAlunoRead(
        aluno_id=aluno.id,  # type: ignore[arg-type]
        nome_aluno=aluno.nome,
        turma_id=aluno.turma_id,
        total_aulas=total_aulas,
        presencas=presencas,
        percentual=percentual,
    )


@router.get("/frequencia/turma/{turma_id}", response_model=FrequenciaTurmaRead)
def frequencia_turma(
    turma_id: int,
    session: Session = Depends(get_session),
) -> FrequenciaTurmaRead:
    """Frequência de todos os alunos de uma turma."""
    turma = session.get(Turma, turma_id)
    if turma is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Turma não encontrada.",
        )

    total_aulas = _total_aulas(session, turma_id)
    contagens = _contagens_presenca(session, turma_id)
    alunos = session.exec(
        select(Aluno).where(Aluno.turma_id == turma_id).order_by(Aluno.nome)
    ).all()

    alunos_freq = [
        _montar_frequencia(aluno, total_aulas, contagens.get(aluno.id, 0))
        for aluno in alunos
    ]
    percentual_medio = (
        round(sum(item.percentual for item in alunos_freq) / len(alunos_freq), 2)
        if alunos_freq
        else 0.0
    )

    return FrequenciaTurmaRead(
        turma_id=turma_id,
        nome_turma=turma.nome,
        total_aulas=total_aulas,
        total_alunos=len(alunos_freq),
        percentual_medio=percentual_medio,
        alunos=alunos_freq,
    )


@router.get("/frequencia/aluno/{aluno_id}", response_model=FrequenciaAlunoRead)
def frequencia_aluno(
    aluno_id: int,
    session: Session = Depends(get_session),
) -> FrequenciaAlunoRead:
    """Frequência individual de um aluno, considerando as aulas da sua turma."""
    aluno = session.get(Aluno, aluno_id)
    if aluno is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aluno não encontrado.",
        )

    total_aulas = _total_aulas(session, aluno.turma_id)
    contagens = _contagens_presenca(session, aluno.turma_id)
    return _montar_frequencia(aluno, total_aulas, contagens.get(aluno.id, 0))
