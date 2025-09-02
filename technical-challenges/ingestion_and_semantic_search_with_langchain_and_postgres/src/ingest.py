from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import (
    PDF_PATH,
    PROVIDER,
    get_embedding_model_integration,
    get_store,
)


def ingest_pdf():
    loader = PyPDFLoader(PDF_PATH)
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
        add_start_index=False,
    )

    splits = splitter.split_documents(docs)

    if not splits:
        raise ValueError("No documents found")

    enriched = [
        Document(
            page_content=d.page_content,
            metadata={k: v for k, v in d.metadata.items() if v not in ("", None)},
        )
        for d in splits
    ]

    ids = [f"doc-{i}" for i in range(len(enriched))]

    store = get_store(get_embedding_model_integration(PROVIDER))
    store.add_documents(documents=enriched, ids=ids)


if __name__ == "__main__":
    ingest_pdf()
