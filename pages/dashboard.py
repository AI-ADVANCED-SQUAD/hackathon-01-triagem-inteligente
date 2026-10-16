import plotly.express as px
import streamlit as st

from config.database import Database
from utils.dashboard_utils import PRIORITY_ORDER, get_dashboard_data


@st.cache_resource
def get_database():
    database = Database()
    database.create_tables()
    return database


st.set_page_config(
    page_title="Dashboard - Triagem de Chamados",
    page_icon="📊",
    layout="wide",
)

st.title("📊 Dashboard")

database = get_database()
session = database.get_session()
try:
    data = get_dashboard_data(session)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total de Chamados", data["total_chamados"])
    with col2:
        st.metric("Prioridade Crítica", data["total_criticos"])
    with col3:
        st.metric("Sentimento Negativo", data["total_sentimento_negativo"])

    st.divider()
    graf1, graf2 = st.columns(2)

    with graf1:
        st.subheader("Distribuição de prioridade")
        distribuicao = data["distribuicao_prioridade"]
        if distribuicao:
            ordered_priorities = [p for p in PRIORITY_ORDER if p in distribuicao]
            ordered_priorities += [p for p in distribuicao if p not in PRIORITY_ORDER]
            counts = [distribuicao[p] for p in ordered_priorities]

            fig_bar = px.bar(
                x=counts,
                y=ordered_priorities,
                orientation="h",
                labels={"x": "Quantidade", "y": "Prioridade"},
            )
            fig_bar.update_layout(
                yaxis={
                    "categoryorder": "array",
                    "categoryarray": ordered_priorities[::-1],
                }
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("Nenhum chamado encontrado para exibir a distribuição.")

    with graf2:
        st.subheader("Distribuição por categoria")
        distribuicao_categoria = data["distribuicao_categoria"]
        if distribuicao_categoria:
            fig_pie = px.pie(
                names=list(distribuicao_categoria.keys()),
                values=list(distribuicao_categoria.values()),
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("Nenhum chamado encontrado para exibir por categoria.")

    st.subheader("Chamados")

    filter1, filter2 = st.columns(2)
    with filter1:
        search = st.text_input(
            "Pesquisar chamado por título", placeholder="Digite o título..."
        )
    with filter2:
        priority_options = ["TODAS"] + PRIORITY_ORDER
        priority = st.selectbox("Filtrar por prioridade", options=priority_options)

    chamados = get_dashboard_data(session, search=search, priority=priority)["chamados"]
    if not chamados:
        st.info("Nenhum chamado encontrado com os filtros aplicados.")
    else:
        left, right = st.columns(2)
        for i, chamado in enumerate(chamados):
            with left if i % 2 == 0 else right:
                with st.container(border=True):
                    st.write(f"**{chamado.title}**")
                    st.write(f"Prioridade: {chamado.priority}")
                    st.write(f"Sentimento: {chamado.sentiment}")
                    st.write(f"Categoria: {chamado.category}")
                    with st.expander("Ver detalhes"):
                        st.write(f"Cliente: {chamado.client_name}")
                        st.write(f"Assunto: {chamado.subject}")
                        st.write(f"Canal: {chamado.channel}")
                        st.write(f"Descrição: {chamado.description}")
                        st.write(f"Tom: {chamado.tone}")
                        st.write(f"Justificativa: {chamado.priority_justification}")
finally:
    session.close()
