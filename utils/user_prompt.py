from textwrap import dedent

def get_user_prompt(
    title: str,
    client_name: str,
    subject: str,
    channel: str,
    description: str
) -> str:
    return dedent(f"""
        Por favor, faça a triagem do chamado abaixo, considerando
        os dados já preenchidos do cliente e retornando APENAS o JSON:

        Título: {title}
        Cliente: {client_name}
        Assunto: {subject}
        Canal: {channel}
        Descrição: {description}
    """)
