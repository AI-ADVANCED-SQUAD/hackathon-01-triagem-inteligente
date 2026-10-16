from sqlalchemy import func, or_

from models.ticket import Ticket

NEGATIVE_KEYWORDS = [
    "frustr",
    "insatis",
    "preocup",
    "urgent",
    "negativ",
    "irrit",
    "raiva",
    "ansios",
    "revolt",
    "triste",
]

PRIORITY_ORDER = ["CRÍTICA", "ALTA", "MÉDIA", "BAIXA"]


def _negative_sentiment_filter():
    return or_(*[Ticket.sentiment.ilike(f"%{kw}%") for kw in NEGATIVE_KEYWORDS])


def _base_filtered_query(session, search: str = "", priority: str = "TODAS"):
    query = session.query(Ticket)
    if search:
        query = query.filter(Ticket.title.ilike(f"%{search}%"))
    if priority and priority != "TODAS":
        query = query.filter(Ticket.priority == priority)
    return query


def get_dashboard_data(session, search: str = "", priority: str = "TODAS") -> dict:
    search = (search or "").strip()

    total_chamados = session.query(func.count(Ticket.id)).scalar() or 0

    total_criticos = (
        session.query(func.count(Ticket.id))
        .filter(Ticket.priority == "CRÍTICA")
        .scalar()
        or 0
    )

    total_sentimento_negativo = (
        session.query(func.count(Ticket.id))
        .filter(_negative_sentiment_filter())
        .scalar()
        or 0
    )

    distribuicao_rows = (
        session.query(Ticket.priority, func.count(Ticket.id))
        .group_by(Ticket.priority)
        .all()
    )
    distribuicao_prioridade = {row[0]: row[1] for row in distribuicao_rows}

    categoria_rows = (
        session.query(Ticket.category, func.count(Ticket.id))
        .group_by(Ticket.category)
        .all()
    )
    distribuicao_categoria = {row[0]: row[1] for row in categoria_rows if row[0]}

    prioridades_disponiveis = [
        row[0]
        for row in session.query(Ticket.priority)
        .distinct()
        .order_by(Ticket.priority)
        .all()
        if row[0]
    ]

    chamados = (
        _base_filtered_query(session, search=search, priority=priority)
        .order_by(Ticket.created_at.desc())
        .all()
    )

    return {
        "total_chamados": total_chamados,
        "total_criticos": total_criticos,
        "total_sentimento_negativo": total_sentimento_negativo,
        "distribuicao_prioridade": distribuicao_prioridade,
        "distribuicao_categoria": distribuicao_categoria,
        "prioridades_disponiveis": prioridades_disponiveis,
        "chamados": chamados,
    }
