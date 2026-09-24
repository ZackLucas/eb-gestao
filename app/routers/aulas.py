"""Endpoints de Aulas e da lista de chamada."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.database import get_session
from app.models import Aluno, Aula, Presenca, Turma
from app.schemas import (
    AulaCreate,
    AulaRead,
    ItemChamadaAlunoRead,
    ListaChamadaSubmit,
)

router = APIRouter()


@router.post("/", response_model=AulaRead, status_code=status.HTTP_201_CREATED)
def criar_aula(
    aula: AulaCreate,
    session: Session = Depends(get_session),
) -> Aula:
    """Cria/inicia uma aula para uma turma existente."""
    if session.get(Turma, aula.turma_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Turma não encontrada.",
        )

    db_aula = Aula.model_validate(aula)
    session.add(db_aula)
    session.commit()
    session.refresh(db_aula)
    return db_aula


@router.get("/{aula_id}/chamada", response_model=list[ItemChamadaAlunoRead])
def obter_chamada(
    aula_id: int,
    session: Session = Depends(get_session),
) -> list[ItemChamadaAlunoRead]:
    """Retorna a lista de chamada da aula.

    Se ainda não houver presenças salvas, devolve todos os alunos ativos da
    turma com `presente: False`. Caso contrário, devolve os dados persistidos.
    """
    aula = session.get(Aula, aula_id)
    if aula is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aula não encontrada.",
        )

    presencas = session.exec(
        select(Presenca, Aluno)
        .join(Aluno, Presenca.aluno_id == Aluno.id)
        .where(Presenca.aula_id == aula_id)
    ).all()

    if presencas:
        return [
            ItemChamadaAlunoRead(
                aluno_id=presenca.aluno_id,
                nome_aluno=aluno.nome,
                presente=presenca.presente,
            )
            for presenca, aluno in presencas
        ]

    # Nenhuma presença salva ainda: monta a lista com os alunos ativos da turma.
    alunos = session.exec(
        select(Aluno)
        .where(Aluno.turma_id == aula.turma_id)
        .where(Aluno.ativo.is_(True))
        .order_by(Aluno.nome)
    ).all()

    return [
        ItemChamadaAlunoRead(
            aluno_id=aluno.id,
            nome_aluno=aluno.nome,
            presente=False,
        )
        for aluno in alunos
        if aluno.id is not None
    ]


@router.post("/{aula_id}/chamada", response_model=list[ItemChamadaAlunoRead])
def salvar_chamada(
    aula_id: int,
    payload: ListaChamadaSubmit,
    session: Session = Depends(get_session),
) -> list[ItemChamadaAlunoRead]:
    """Salva ou atualiza em lote as presenças dos alunos da aula."""
    aula = session.get(Aula, aula_id)
    if aula is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aula não encontrada.",
        )

    aluno_ids = [item.aluno_id for item in payload.itens]

    # Valida de uma vez só quais alunos existem.
    alunos = session.exec(select(Aluno).where(Aluno.id.in_(aluno_ids))).all()
    alunos_por_id = {aluno.id: aluno for aluno in alunos}

    faltantes = [aluno_id for aluno_id in aluno_ids if aluno_id not in alunos_por_id]
    if faltantes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alunos não encontrados: {faltantes}.",
        )

    # Busca presenças já existentes para fazer upsert.
    existentes = session.exec(
        select(Presenca)
        .where(Presenca.aula_id == aula_id)
        .where(Presenca.aluno_id.in_(aluno_ids))
    ).all()
    presencas_por_aluno = {presenca.aluno_id: presenca for presenca in existentes}

    resultado: list[ItemChamadaAlunoRead] = []
    for item in payload.itens:
        presenca = presencas_por_aluno.get(item.aluno_id)
        if presenca is None:
            presenca = Presenca(
                aula_id=aula_id,
                aluno_id=item.aluno_id,
                presente=item.presente,
            )
            presencas_por_aluno[item.aluno_id] = presenca
        else:
            presenca.presente = item.presente

        session.add(presenca)
        resultado.append(
            ItemChamadaAlunoRead(
                aluno_id=item.aluno_id,
                nome_aluno=alunos_por_id[item.aluno_id].nome,
                presente=item.presente,
            )
        )

    session.commit()
    return resultado
