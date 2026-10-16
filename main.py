import json
from contextlib import contextmanager

import pandas as pd
import streamlit as st

from config.database import Database
from services.ingestion_service import map_row
from services.openai_service import OpenAIService
from utils import create_ticket_model, get_user_prompt, load_prompt


@st.cache_resource
def get_openai_service():
    return OpenAIService()


@st.cache_resource
def get_prompt():
    return load_prompt("system_prompt")


@st.cache_resource
def get_database():
    database = Database()
    database.create_tables()
    return database


@contextmanager
def get_session():
    database = get_database()
    session = database.get_session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        st.error(f"Erro ao salvar o chamado: {e}")
        raise e
    finally:
        session.close()


ai = get_openai_service()
system_prompt = get_prompt()
database = get_database()

st.set_page_config(
    page_title="Triagem Inteligente de Chamados",
    page_icon="🎯",
    layout="wide",
)

st.title("🎯 Triagem Inteligente de Chamados")
st.subheader("Automatize a triagem de seus chamados")
st.space()

st.sidebar.success("Selecione uma página acima.")

uploaded_file = st.file_uploader(
    "Escolha um arquivo",
    type=["csv", "xlsx"],
    accept_multiple_files=False,
)

if uploaded_file is not None:
    with st.spinner("Processando arquivo..."):
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        st.dataframe(df)
        st.space()

        if st.button(f"Triar e salvar {len(df)} chamados"):
            for record in df.to_dict(orient="records"):
                base = map_row(record)
                user_prompt = get_user_prompt(
                    base["titulo"],
                    base["nome_do_cliente"],
                    base["assunto"],
                    base["canal"],
                    base["descricao"],
                )
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ]
                response = ai.get_response(messages)
                response = json.loads(response.model_dump_json(indent=2))
                base = base | response

                with get_session() as session:
                    ticket_model = create_ticket_model(base)
                    session.add(ticket_model)
            st.success("Chamados triados e salvos com sucesso!")

with st.form("ticket_form"):
    st.subheader("Abrir chamado")
    st.write("Preencha os dados abaixo para abrir um chamado.")
    st.space()

    col1, col2 = st.columns(2)

    with col1:
        title = st.text_input("Título")
        name = st.text_input("Nome do Cliente")
    with col2:
        channel = st.text_input("Canal")
        subject = st.text_input("Assunto")

    description = st.text_area("Descrição")
    submit = st.form_submit_button("Enviar")

if submit:
    with st.spinner("Triando chamado..."):
        ticket = {
            "titulo": title,
            "nome_do_cliente": name,
            "assunto": subject,
            "canal": channel,
            "descricao": description,
        }
        user_prompt = get_user_prompt(
            title,
            name,
            subject,
            channel,
            description,
        )
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        response = ai.get_response(messages)
        response = json.loads(response.model_dump_json(indent=2))
        ticket = ticket | response

        with get_session() as session:
            try:
                ticket_model = create_ticket_model(ticket)
                session.add(ticket_model)
                st.success("Chamado aberto com sucesso!")
                with st.expander("Ver detalhes do chamado"):
                    st.json(ticket)
            except Exception as e:
                st.error(f"Erro ao salvar o chamado: {e}")
