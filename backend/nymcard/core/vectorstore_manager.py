import os
import logging
import asyncio
from typing import List, Dict, Tuple
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain.schema import Document
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
VECTORSTORE_DIRECTORY = os.getenv("VECTORSTORE_DIRECTORY", "./chroma_db")


class VectorStoreManager:
    def __init__(self):
        """
        Initialize embeddings and vectorstore (Chroma).
        """
        logger.info("[INIT_VECTORSTORE] Initializing VectorStore with Chroma + OpenAI embeddings.")
        self.embedding_fn = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

        self.vstore = Chroma(
            collection_name="confluence_docs",
            embedding_function=self.embedding_fn,
            persist_directory=VECTORSTORE_DIRECTORY
        )

    async def add_texts(self, texts: List[str], metadatas: List[Dict] = None):
        """
        Async wrapper for adding a list of text documents to the Chroma store with optional metadata.
        """
        if not metadatas:
            metadatas = [{} for _ in texts]

        try:
            logger.info(f"[ADD_TEXTS] Adding {len(texts)} documents to VectorStore.")
            # Wrap synchronous add_texts in asyncio.to_thread
            await asyncio.to_thread(self.vstore.add_texts, texts, metadatas)
            # Wrap synchronous persist in asyncio.to_thread
            await asyncio.to_thread(self.vstore.persist)
            logger.info("[ADD_TEXTS] Done persisting data.")
        except Exception as e:
            logger.error(f"[ADD_TEXTS] Error adding texts to vector store: {e}")

    async def similarity_search_with_scores(
        self, query: str, k: int = 3
    ) -> List[Tuple[str, Dict, float]]:
        """
        Perform a similarity search that returns (doc_text, metadata, score).
        """
        logger.info(f"[SIMILARITY_SEARCH] Query='{query}', top_k={k}")
        results_with_scores = []
        try:
            # Wrap synchronous similarity_search_with_score in asyncio.to_thread
            results = await asyncio.to_thread(self.vstore.similarity_search_with_score, query, k=k)
            # results is typically List[Tuple[Document, float]]
            for doc, score in results:
                doc_text = doc.page_content
                doc_meta = doc.metadata
                logger.debug(f"[SIM_SEARCH] doc metadata={doc_meta}, score={score:.4f}, preview='{doc_text[:80]}...'")
                results_with_scores.append((doc_text, doc_meta, score))
        except Exception as e:
            logger.error(f"[SIMILARITY_SEARCH] Error in similarity search: {e}")

        return results_with_scores

    async def delete_document(self, page_id: str):
        """
        Delete a document from the vector store based on page_id.
        """
        try:
            logger.info(f"[DELETE_DOCUMENT] Deleting document with page_id={page_id}")
            # Chroma doesn't support deletion by metadata directly.
            # Workaround: Retrieve all documents, filter out the one with page_id, and recreate the collection.
            # This is not efficient for large datasets. Consider using a more suitable vector store if deletion is frequent.

            all_docs = await asyncio.to_thread(self.vstore.get, where={}, limit=-1)
            docs_to_keep = [doc for doc in all_docs.documents if doc.metadata.get("page_id") != page_id]

            # Clear existing collection
            await asyncio.to_thread(self.vstore.delete_collection)

            # Re-add the filtered documents
            texts = [doc.page_content for doc in docs_to_keep]
            metadatas = [doc.metadata for doc in docs_to_keep]
            await self.add_texts(texts, metadatas)

            logger.info(f"[DELETE_DOCUMENT] Document with page_id={page_id} deleted successfully.")
        except Exception as e:
            logger.error(f"[DELETE_DOCUMENT] Error deleting document: {e}", exc_info=True)
