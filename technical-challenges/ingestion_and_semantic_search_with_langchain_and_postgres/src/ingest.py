import logging

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Configure logging only if not already configured
if not logging.getLogger().handlers:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

logger = logging.getLogger(__name__)

from config import (
    PDF_PATH,
    PROVIDER,
    get_embedding_model_integration,
    get_store,
)


def ingest_pdf():
    logger.info("Starting ingestion process")
    logger.info(f"Reading PDF from: {PDF_PATH}")
    loader = PyPDFLoader(PDF_PATH)
    docs = loader.load()
    logger.info(f"Loaded {len(docs)} document(s) from PDF")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
        add_start_index=False,
    )
    logger.info(
        "Configured splitter: chunk_size=%s, chunk_overlap=%s, add_start_index=%s",
        1000,
        150,
        False,
    )

    splits = splitter.split_documents(docs)
    logger.info("Produced %d chunk(s) from PDF", len(splits))

    if not splits:
        logger.warning("No documents found after splitting; aborting ingestion")
        raise ValueError("No documents found")

    enriched = [
        Document(
            page_content=d.page_content,
            metadata={k: v for k, v in d.metadata.items() if v not in ("", None)},
        )
        for d in splits
    ]
    logger.info("Enriched metadata for %d chunk(s)", len(enriched))

    ids = [f"doc-{i}" for i in range(len(enriched))]

    logger.info("Using provider: %s", PROVIDER)
    store = get_store(get_embedding_model_integration(PROVIDER))
    logger.info("Adding %d document(s) to the store", len(enriched))
    store.add_documents(documents=enriched, ids=ids)
    logger.info("Ingestion completed successfully")


if __name__ == "__main__":
    try:
        ingest_pdf()
    except Exception:
        logger.exception("Ingestion failed")
        raise
