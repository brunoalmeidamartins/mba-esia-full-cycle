# Ingestão e Busca Semântica com LangChain e Postgres (PGVector)

Este desafio implementa um fluxo simples de:
- Ingestão de um PDF em chunks;
- Geração de embeddings (OpenAI ou Google, escolhidos automaticamente);
- Armazenamento no Postgres com PGVector;
- Busca semântica e chat com o conteúdo indexado.

O projeto foi estruturado para ser executado a partir da pasta:
technical-challenges/ingestion_and_semantic_search_with_langchain_and_postgres


## Sumário
- Requisitos
- Configuração de ambiente (.env)
- Como a escolha de provider funciona (OpenAI x Google)
- Banco de dados (Postgres + PGVector)
- Instalação
- Comandos principais (Makefile)
- Execução
- Troubleshooting


## Requisitos
- Python 3.12+
- Postgres com extensão PGVector instalada
- Chave de API de um dos provedores de embeddings:
  - OpenAI, ou
  - Google Generative AI (Gemini)


## Configuração de ambiente (.env)
Crie um arquivo .env nesta pasta com as variáveis necessárias. Há validações em src/config.py que garantem que:
- PDF_PATH exista e aponte para um arquivo;
- DATABASE_URL e PG_VECTOR_COLLECTION_NAME estejam preenchidos;
- Ou OpenAI (OPENAI_API_KEY e OPENAI_EMBEDDING_MODEL) ou Google (GOOGLE_API_KEY e GOOGLE_EMBEDDING_MODEL) estejam configurados.

Exemplo de .env (usando OpenAI):

PDF_PATH=/caminho/para/arquivo.pdf
DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/meubanco
PG_VECTOR_COLLECTION_NAME=meu_indice
OPENAI_API_KEY=sk-xxxx
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

Exemplo de .env (usando Google):

PDF_PATH=/caminho/para/arquivo.pdf
DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/meubanco
PG_VECTOR_COLLECTION_NAME=meu_indice
GOOGLE_API_KEY=AIza-xxxx
GOOGLE_EMBEDDING_MODEL=text-embedding-004

Observações:
- Não é necessário definir variáveis dos dois provedores. Se ambos estiverem definidos, o projeto prioriza OpenAI.
- As variáveis de chat usam modelos padrão definidos em src/config.py (OPENAI_MODEL e GOOGLE_MODEL) e podem ser ajustadas ali, se necessário.


## Como a escolha de provider funciona
Em src/config.py, o provider é definido automaticamente em PROVIDER:
- Se OPENAI_API_KEY e OPENAI_EMBEDDING_MODEL estiverem válidos, PROVIDER="openai";
- Caso contrário, se GOOGLE_API_KEY e GOOGLE_EMBEDDING_MODEL estiverem válidos, PROVIDER="google";
- Se nenhum for válido, a aplicação encerra com erro explicativo.

As factories get_embedding_model_integration e get_chat retornam as integrações corretas para o provider ativo.


## Banco de dados (Postgres + PGVector)
- É necessário ter o Postgres com a extensão PGVector instalada.
- A URL usada (DATABASE_URL) segue o formato SQLAlchemy/psycopg (ex.: postgresql+psycopg://user:password@host:5432/db).
- O nome da coleção vetorial é definido por PG_VECTOR_COLLECTION_NAME.
- O armazenamento é feito via langchain-postgres (PGVector) com use_jsonb=true.

Dica: para instalar PGVector em um Postgres local, algo como:
CREATE EXTENSION IF NOT EXISTS vector;


## Instalação
Recomendado usar um virtualenv/venv.

- Crie e ative o ambiente virtual
python -m venv .venv
source .venv/bin/activate

- Instale dependências (sugestão usando pip e extras típicos do ecossistema LangChain)
pip install -U pip
pip install langchain langchain-openai langchain-google-genai langchain-postgres langchain-community langchain-text-splitters python-dotenv psycopg[binary] pypdf isort black

Obs.: Se preferir, liste as dependências em requirements.txt. O repositório já possui pyproject.toml com as regras de formatação.


## Comandos principais (Makefile)
- Format (isort + black, leitura de regras pelo pyproject.toml)
make format

- Ingestão (carrega o PDF, gera embeddings e indexa no Postgres)
make ingest

- Chat (faz perguntas com base no conteúdo indexado)
make run


## Execução
1) Suba a infraestrutura com Docker (Postgres + PGVector)
- Na raiz deste desafio, execute:

docker-compose up -d

- Para parar/remover os serviços posteriormente:

docker-compose down

2) Configure o .env conforme sua escolha de provider e banco.
3) (Opcional) Formate o código
make format
4) Faça a ingestão do seu PDF
make ingest
- O ingest tem logs estruturados (INFO) com timestamp; falhas geram stack trace.
5) Rode o chat
make run
- Digite sua pergunta no terminal; use exit para encerrar.


## Troubleshooting
- Erro de variáveis ausentes: src/config.py valida tudo no start e informa exatamente o que falta.
- PDF_PATH inválido: o caminho deve existir e apontar para um arquivo (não diretório).
- Conexão Postgres: verifique DATABASE_URL, credenciais e se a extensão PGVector está instalada.
- Sem resultados na busca: certifique-se de ter rodado a ingestão após configurar corretamente o provider e o banco.
- Provider: se ambos (OpenAI e Google) estiverem configurados, OpenAI será usado. Para forçar Google, remova as variáveis de OpenAI.


## Licença
MIT. Veja o campo license no pyproject.toml.
