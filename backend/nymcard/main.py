# nymcard_project/nymcard/main.py

import os
import sys
import asyncio
import logging
import argparse

from dotenv import load_dotenv

from .core.confluence_loader import ConfluenceLoader
from .core.doc_processor import process_confluence_page
from .core.doc_registry import load_registry, save_registry, compute_content_hash
from .core.vectorstore_manager import VectorStoreManager

from .core.advanced_rag_pipeline import CustomConversationalRAGPipeline
from .API import app 

load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

CONFLUENCE_URL = os.getenv("CONFLUENCE_URL")
CONFLUENCE_USERNAME = os.getenv("CONFLUENCE_USERNAME")
CONFLUENCE_API_TOKEN = os.getenv("CONFLUENCE_API_TOKEN")
CONFLUENCE_SPACE_KEY = os.getenv("CONFLUENCE_SPACE_KEY", "TD")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


async def fetch_and_ingest_pages(space_key: str, vectorstore_manager: VectorStoreManager):
    """
    1) Fetch pages from Confluence (async).
    2) Process them (clean, chunk).
    3) Embed them if new or changed (using doc_registry).
    4) Collect the raw text for fallback retrieval (URL/phone/keyword).
    Returns:
      updated_count: int - number of new or updated pages embedded.
      all_docs_text: list[str] - all "cleaned_text" from each page for the HybridRetriever.
    """
    registry = load_registry()
    loader = ConfluenceLoader(
        url=CONFLUENCE_URL,
        username=CONFLUENCE_USERNAME,
        api_token=CONFLUENCE_API_TOKEN
    )

    logger.info(f"[INGEST] Fetching pages from space '{space_key}'...")
    pages = await loader.fetch_all_pages_in_space(space_key)
    if not pages:
        logger.warning("[INGEST] No pages found. Check space key or permissions.")
        return 0, []

    tasks = []
    all_docs_text = []

    for page in pages:
        processed = process_confluence_page(page)
        all_docs_text.append(processed["cleaned_text"])
        tasks.append(_maybe_embed_page(processed, registry, vectorstore_manager))

    results = await asyncio.gather(*tasks, return_exceptions=True)
    updated_count = sum(r for r in results if isinstance(r, int))

    if updated_count > 0:
        save_registry(registry)
        logger.info(f"[INGEST] {updated_count} pages embedded/updated.")
    else:
        logger.info("[INGEST] No new or updated pages found.")

    return updated_count, all_docs_text


async def _maybe_embed_page(processed_page: dict, registry: dict, vs_manager: VectorStoreManager) -> int:
    """
    Checks if page is new or updated. If so, embed in vector store.
    Returns 1 if embedded, else 0.
    """
    try:
        page_id = processed_page["page_id"]
        cleaned_text = processed_page["cleaned_text"]
        current_hash = compute_content_hash(cleaned_text)

        if page_id not in registry:
            logger.info(f"[INGEST] New page_id={page_id}, embedding.")
            await embed_page(vs_manager, processed_page)
            registry[page_id] = current_hash
            return 1
        else:
            old_hash = registry[page_id]
            if current_hash != old_hash:
                logger.info(f"[INGEST] Updated page_id={page_id}, re-embedding.")
                await embed_page(vs_manager, processed_page)
                registry[page_id] = current_hash
                return 1
            else:
                logger.debug(f"[INGEST] No change for page_id={page_id}. Skipped.")
                return 0
    except Exception as e:
        logger.error(f"[INGEST] Error embedding page: {e}", exc_info=True)
        return 0


async def embed_page(vs_manager: VectorStoreManager, processed_page: dict):
    """
    Actually adds the chunked text to the vector store.
    """
    page_id = processed_page["page_id"]
    chunks = processed_page["chunks"]
    title = processed_page["title"]

    metas = [{"page_id": page_id, "title": title} for _ in chunks]
    logger.debug(f"[EMBED_PAGE] Embedding {len(chunks)} chunks for page_id={page_id}")
    await vs_manager.add_texts(chunks, metas)


async def interactive_query_loop(all_docs_text=None):
    """
    1) Create the VectorStoreManager.
    2) Create the CustomConversationalRAGPipeline with all_docs_text for HybridRetriever.
    3) Enter an interactive user loop.
    """
    vs_manager = VectorStoreManager()
    pipeline = CustomConversationalRAGPipeline(
        vectorstore_manager=vs_manager,
        openai_api_key=OPENAI_API_KEY,
        all_docs_text=all_docs_text or []
    )

    print("\n=== Confluence Knowledge Assistant (Hybrid + Conversational) ===")
    print("Type 'exit' to quit.\n")

    while True:
        user_input = input("Ask a question: ").strip()
        if user_input.lower() == "exit":
            print("Goodbye!")
            break
        if not user_input:
            continue

        answer = await pipeline.query(user_input)
        print(f"\nAnswer: {answer}\n")


async def run_ingestion_only():
    """
    Just ingest docs and exit.
    """
    vs_manager = VectorStoreManager()
    updated_count, _ = await fetch_and_ingest_pages(CONFLUENCE_SPACE_KEY, vs_manager)
    logger.info(f"[MAIN] Ingestion complete. {updated_count} new/updated pages.")


async def run_query_only():
    """
    If user runs only 'query' mode, we won't have doc_text for fallback logic
    unless we store it somewhere. We'll pass an empty list here,
    meaning phone/URL fallback won't function. But embedding-based queries
    still work if you've ingested previously.
    """
    await interactive_query_loop(all_docs_text=None)


async def run_all():
    """
    1) Ingest docs from Confluence (and gather doc_text for fallback).
    2) Start interactive Q&A loop with HybridRetriever + memory.
    """
    vs_manager = VectorStoreManager()
    updated_count, all_docs_text = await fetch_and_ingest_pages(CONFLUENCE_SPACE_KEY, vs_manager)
    logger.info(f"[MAIN] Ingestion done, {updated_count} new/updated pages.")

    # Now run queries. We pass 'all_docs_text' so fallback logic for URLs, phones, etc. works.
    await interactive_query_loop(all_docs_text)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Confluence Knowledge Assistant using HybridRetriever + Conversational Memory + Flask API"
    )
    parser.add_argument(
        "--mode", default="all", choices=["all", "ingest", "query", "api"],
        help="Which mode to run: 'ingest' only, 'query' only, 'all' (both), or 'api' to run the Flask API."
    )
    return parser.parse_args()


def main():
    args = parse_args()
    if args.mode == "ingest":
        asyncio.run(run_ingestion_only())
    elif args.mode == "query":
        asyncio.run(run_query_only())
    elif args.mode == "api":
        # Run the Flask API
        app.run(host='0.0.0.0', port=5000)
    else:
        asyncio.run(run_all())


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("[MAIN] User interrupted.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"[MAIN] Error: {e}", exc_info=True)
        sys.exit(1)
