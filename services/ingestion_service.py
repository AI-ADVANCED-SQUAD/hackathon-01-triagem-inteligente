import pandas as pd

def map_row(row: dict) -> dict:
    desc = str(row.get("Descrição resumida") or "").strip()
    return {
      "titulo": f"Chamado {row.get('ID do chamado')}" if pd.notna(row.get("ID do chamado")) else desc[:60] or "Sem título",
      "nome_do_cliente": row.get("Nome fictício do cliente") or "Não informado",
      "assunto": "Suporte geral",  # default fixo, IA classifica via categoria depois
      "canal": row.get("Canal de atendimento") or "Não informado",
      "descricao": desc,
      "created_at": row.get("Data de abertura"),  # opcional, precisa add coluna no model se quiser usar
    }
