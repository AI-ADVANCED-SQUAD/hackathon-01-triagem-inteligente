
# 🎯 Triagem Inteligente de Chamados

Automatize a triagem de chamados de suporte com IA: classificação por categoria, priorização, análise de sentimento/tom, resumo e sugestão de resposta empática — tudo persistido em banco de dados.

App em **Streamlit** + **OpenAI API (ou OpenRouter)** com saída estruturada via Pydantic + **SQLite/SQLAlchemy**.

## ✨ Funcionalidades

- **Upload em lote (CSV/XLSX):** envia uma planilha, visualiza o preview e tria N chamados de uma vez.
- **Abertura manual:** formulário com Título, Cliente, Canal, Assunto e Descrição.
- **Classificação automática via LLM:**
  - `categoria`: `ACESSO_AUTENTICACAO | INDISPONIBILIDADE | ERRO_FUNCIONAL | FINANCEIRO | CONFIGURACAO | SOLICITACAO | OUTROS`
  - `prioridade`: `BAIXA | MÉDIA | ALTA | CRÍTICA` + justificativa em 1 frase
  - `sentimento`, `tom`, `resumo`, `resposta` sugerida (profissional e empática, sem inventar solução ou prazo)
- **Persistência:** cada chamado triado é salvo na tabela `tickets` (SQLite por padrão).
- **Dashboard (`pages/dashboard.py`):** métricas, gráficos Plotly e lista filtrável de chamados.
- **Prompt versionado:** regras de triagem em `prompts/system_prompt.md`.

## 🧠 Como funciona

```
main.py
  → utils.get_user_prompt(...) + prompts/system_prompt.md
  → services.OpenAIService.get_response(messages) [beta.chat.completions.parse, response_format=TicketResponse]
  → utils.create_ticket_model(...)
  → config.Database.get_session() → models.Ticket (tabela tickets)
```

1. O texto do chamado é montado como `user_prompt`.
2. O `system_prompt` impõe categorias, prioridades e formato JSON estrito.
3. A API retorna um `TicketResponse` (Pydantic) validado.
4. O resultado é mesclado aos dados de entrada e salvo via SQLAlchemy.

## 🛠️ Stack

- **App:** Streamlit
- **IA:** SDK `openai` (funciona com OpenAI ou OpenRouter via `OPENAI_BASE_URL`)
- **Dados:** pandas, openpyxl, numpy
- **Banco/ORM:** SQLAlchemy + SQLite (`sqlite:///db.sqlite3`)
- **Validação:** Pydantic
- **Config:** python-dotenv
- **Gráficos:** Plotly (`plotly.express` no dashboard)
- **Dev:** black, isort, flake8

## 📁 Estrutura

```
.
├── main.py                  # app Streamlit principal (upload em lote + form manual)
├── pages/
│   └── dashboard.py         # 📊 Dashboard: métricas, gráficos Plotly, busca e filtro por prioridade
├── config/
│   ├── settings.py          # lê OPENAI_* do .env + DATABASE_URL
│   └── database.py          # Database(engine, SessionLocal, create_tables/get_session)
├── models/
│   └── ticket.py            # SQLAlchemy Ticket + Pydantic TicketResponse
├── services/
│   ├── openai_service.py    # wrapper do client OpenAI
│   └── ingestion_service.py # map_row(): linha da planilha -> dict padrão
├── utils/
│   ├── load_prompt.py       # lê prompts/*.md
│   ├── user_prompt.py       # monta o prompt do usuário
│   ├── create_ticket_model.py # dict PT -> model Ticket
│   └── dashboard_utils.py  # get_dashboard_data(), PRIORITY_ORDER, filtro de sentimento negativo
├── prompts/
│   └── system_prompt.md     # regras de categoria/prioridade
├── data/
│   └── chamados_suporte_100_registros_simplificado.xlsx  # exemplo com 100 linhas
├── requirements.txt
├── requirements_dev.txt
├── .env.example
└── db.sqlite3               # criado automaticamente (ignorado no git)
```

## ✅ Pré-requisitos

- Python 3.10+ (recomendado 3.11/3.12)
- Uma `OPENAI_API_KEY` válida:
  - **OpenAI:** https://platform.openai.com/api-keys
  - **OpenRouter (alternativa com modelos free):** https://openrouter.ai/keys
- Git (opcional)

## 🚀 Como rodar

### 1. Clonar / entrar na pasta

```bash
cd triagem-chamados
```

### 2. Criar e ativar o venv

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows (PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

Opcional (formatação/lint):

```bash
pip install -r requirements_dev.txt
```

### 4. Configurar o `.env`

```bash
cp .env.example .env
```

Edite o `.env`:

| Variável           | Obrigatória | Padrão                       | Exemplo                                               |
| ------------------- | ------------ | ----------------------------- | ----------------------------------------------------- |
| `OPENAI_API_KEY`  | sim          | —                            | `sk-...` ou `sk-or-v1-...`                        |
| `OPENAI_MODEL`    | não         | `gpt-4o-mini`               | `gpt-4o-mini` / `poolside/laguna-s-2.1:free`      |
| `OPENAI_BASE_URL` | não         | `https://api.openai.com/v1` | `https://openrouter.ai/api/v1` (se usar OpenRouter) |

Exemplo com OpenAI:

```env
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
OPENAI_BASE_URL=https://api.openai.com/v1
```

Exemplo com OpenRouter:

```env
OPENAI_API_KEY=sk-or-v1-...
OPENAI_MODEL=poolside/laguna-s-2.1:free
OPENAI_BASE_URL=https://openrouter.ai/api/v1
```

### 5. Rodar o app

```bash
streamlit run main.py
```

Acesse: http://localhost:8501

O banco `db.sqlite3` e a tabela `tickets` são criados automaticamente na primeira execução (`Database().create_tables()`).

## 📝 Como usar

### Opção A — Triagem em lote

1. Na página principal, faça upload de um `.xlsx` (ou `.csv`).
2. Confira o preview da tabela.
3. Clique em **"Triar e salvar N chamados"**.
4. Aguarde o `st.success("Chamados triados e salvos com sucesso!")`.

Arquivo de exemplo para testar:

```
data/chamados_suporte_100_registros_simplificado.xlsx
```

Colunas esperadas pela função `map_row()`:

| Coluna na planilha            | Uso                                      |
| ----------------------------- | ---------------------------------------- |
| `ID do chamado`             | vira o título (`Chamado {ID}`)        |
| `Nome fictício do cliente` | `nome_do_cliente`                      |
| `Canal de atendimento`      | `canal`                                |
| `Descrição resumida`      | `descricao` (texto analisado pela IA)  |
| `Data de abertura`          | lida, mas ainda não persistida no model |
| `Status`                    | ignorada por enquanto                    |

> Nota: hoje o código usa `pd.read_excel` mesmo quando o arquivo é `.csv`. Prefira `.xlsx` para o lote.

### Opção B — Abertura manual

1. Preencha **Título, Nome do Cliente, Canal, Assunto, Descrição** no formulário `Abrir chamado`.
2. Clique em **Enviar**.
3. Veja o JSON triado no expander **"Ver detalhes do chamado"**.

### Opção C — Dashboard 📊

Acesse pela navegação multipage do Streamlit (menu lateral) em **Dashboard**.

O que a página exibe (`pages/dashboard.py` + `utils/dashboard_utils.py:get_dashboard_data`):

- **Métricas no topo:**
  - Total de Chamados
  - Prioridade Crítica (`priority == "CRÍTICA"`)
  - Sentimento Negativo (match por palavras-chave em `sentiment`: `frustr, insatis, preocup, urgent, negativ, irrit, raiva, ansios, revolt, triste`)
- **Gráficos Plotly:**
  - Barra horizontal: distribuição por prioridade (ordem `CRÍTICA > ALTA > MÉDIA > BAIXA`)
  - Pizza: distribuição por categoria
- **Lista de chamados:**
  - Busca por título (`st.text_input` com `ilike`)
  - Filtro por prioridade (`TODAS | CRÍTICA | ALTA | MÉDIA | BAIXA`)
  - Cards em 2 colunas com Prioridade, Sentimento, Categoria + expander com Cliente, Assunto, Canal, Descrição, Tom e Justificativa — ordenados por `created_at desc`.

### Exemplo de saída da IA

```json
{
  "categoria": "INDISPONIBILIDADE",
  "prioridade": "CRÍTICA",
  "sentimento": "frustração urgente",
  "tom": "reclamação direta",
  "resumo": "Sistema fora do ar impedindo emissão de notas fiscais.",
  "justificativa_prioridade": "Sistema parado com impacto operacional direto.",
  "resposta": "Olá, sentimos muito pelo transtorno. Estamos tratando seu caso com prioridade e retornaremos em breve com uma atualização."
}
```

## 🗄️ Banco de dados

- Padrão: SQLite em `db.sqlite3` (`DATABASE_URL = "sqlite:///db.sqlite3"` em `config/settings.py`).
- Tabela `tickets`: `id, title, client_name, subject, description, priority, priority_justification, category, tone, sentiment, reply, channel, created_at, updated_at`.

Inspecionar rapidamente:

```bash
sqlite3 db.sqlite3 "SELECT id, title, category, priority FROM tickets LIMIT 5;"
```

## 🧹 Qualidade de código

```bash
black .
isort .
flake8
```

Config do flake8 em `.flake8` (`ignore=E501,W503`, `exclude=.venv`).

## 🗺️ Roadmap

- [x] Dashboard com métricas, gráficos Plotly e filtros (`pages/dashboard.py`)
- [ ] Suporte real a `.csv` no upload em lote (`read_csv` vs `read_excel`)
- [ ] Paginação/progresso no processamento em lote
- [ ] Persistir `Data de abertura` e `Status` da planilha
- [ ] Testes automatizados
- [ ] Docker + `docker-compose`

## 🔧 Troubleshooting

| Problema                            | Causa provável / solução                                                                                         |
| ----------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| `OpenAIError: api key` / 401      | `.env` ausente ou `OPENAI_API_KEY` inválida. Confira `cp .env.example .env` e a chave.                       |
| Erro 404 com OpenRouter             | `OPENAI_BASE_URL` deve ser `https://openrouter.ai/api/v1` e `OPENAI_MODEL` um model ID válido do OpenRouter. |
| `FileNotFoundError` no upload CSV | Bug conhecido: `main.py` usa `pd.read_excel`. Use `.xlsx` por enquanto.                                       |
| Banco vazio / tabela não existe    | Apague `db.sqlite3` e rode `streamlit run main.py` de novo para recriar.                                        |
| Porta 8501 ocupada                  | `streamlit run main.py --server.port 8502`                                                                        |
