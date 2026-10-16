from datetime import datetime

from pydantic import BaseModel, Field
from sqlalchemy import Column, Integer, String, DateTime

from config.database import Base


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String)
    client_name = Column(String)
    subject = Column(String)
    description = Column(String)
    priority = Column(String)
    priority_justification = Column(String)
    category = Column(String)
    tone = Column(String)
    sentiment = Column(String)
    reply = Column(String)
    channel = Column(String)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class TicketResponse(BaseModel):
    categoria: str = Field(description="Categoria do chamado")
    prioridade: str = Field(description="Prioridade do chamado")
    sentimento: str = Field(description="Sentimento do chamado")
    tom: str = Field(description="Tom do chamado")
    resumo: str = Field(description="Resumo do chamado")
    justificativa_prioridade: str = Field(description="Justificativa da prioridade")
    resposta: str = Field(description="Resposta sugerida para o chamado")
