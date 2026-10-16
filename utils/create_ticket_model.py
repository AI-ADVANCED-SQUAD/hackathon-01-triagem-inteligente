from models.ticket import Ticket

def create_ticket_model(ticket: dict):
    return Ticket(
        title=ticket.get("titulo") or "Sem título",
        client_name=ticket.get("nome_do_cliente") or "Cliente não informado",
        subject=ticket.get("assunto") or "Suporte geral",
        description=ticket.get("descricao") or "",
        priority=ticket.get("prioridade") or "Média",
        priority_justification=ticket.get("justificativa_prioridade") or "Justificativa não informada",
        category=ticket.get("categoria") or "Categoria não informada",
        tone=ticket.get("tom") or "Tom não informado",
        sentiment=ticket.get("sentimento") or "Sentimento não informado",
        reply=ticket.get("resposta") or "Resposta não informada",
        channel=ticket.get("canal") or "Canal não informado",
    )
