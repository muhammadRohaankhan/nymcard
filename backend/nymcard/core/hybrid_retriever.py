
import logging
from typing import List, Tuple, Dict

from .vectorstore_manager import VectorStoreManager
from ..utils.helpers import extract_urls, extract_phone_numbers

logger = logging.getLogger(__name__)


class HybridRetriever:
    def __init__(self, vectorstore_manager: VectorStoreManager, all_docs_text: List[str] = None):
        self.vs_manager = vectorstore_manager
        self.all_docs_text = all_docs_text or []

    async def retrieve(self, query: str) -> List[Tuple[str, Dict]]:
        """
        Always runs embedding-based doc retrieval,
        then specialized extraction (URL/phone) if the query indicates so.
        """
        logger.info(f"[HybridRetriever] Processing query: {query}")

        # 1) Embedding-based doc retrieval
        embed_results = await self.embedding_search(query)
        logger.info(f"[HybridRetriever] Found {len(embed_results)} embed-based docs.")

        # 2) Specialized extractions based on query
        specialized_extractions: List[Tuple[str, Dict]] = []

        if self.is_url_query(query):
            urls = []
            for doc_text, _, _ in embed_results:
                extracted = extract_urls(doc_text)
                for url in extracted:
                    urls.append((url, {"type": "url_extraction"}))
            specialized_extractions.extend(urls)
            logger.info(f"[HybridRetriever] Extracted {len(urls)} URLs.")

        if self.is_phone_query(query):
            phones = []
            for doc_text, _, _ in embed_results:
                extracted = extract_phone_numbers(doc_text)
                for phone in extracted:
                    phones.append((phone, {"type": "phone_extraction"}))
            specialized_extractions.extend(phones)
            logger.info(f"[HybridRetriever] Extracted {len(phones)} phone numbers.")

        # 3) Combine embedding results with specialized extractions
        unified_results: List[Tuple[str, Dict]] = []

        for doc_text, md, score in embed_results:
            new_meta = md.copy()
            new_meta["score"] = score
            unified_results.append((doc_text, new_meta))

        # Add specialized extractions at the end
        unified_results.extend(specialized_extractions)

        return unified_results

    async def embedding_search(self, query: str) -> List[Tuple[str, Dict, float]]:
        """
        Perform embedding-based similarity search.
        Returns list of (doc_text, metadata, score)
        """
        logger.info(f"[HybridRetriever] Doing embedding search for: {query}")
        search_results = await self.vs_manager.similarity_search_with_scores(query, k=5)
        if search_results:
            # search_results is a list of (doc_text, metadata, score)
            return search_results
        else:
            return []

    def is_url_query(self, query: str) -> bool:
        """
        Determine if the query is about URLs.
        """
        keywords = ['url', 'link', 'website', 'endpoint']
        return any(keyword in query.lower() for keyword in keywords)

    def is_phone_query(self, query: str) -> bool:
        """
        Determine if the query is about phone numbers.
        """
        keywords = ['phone', 'contact number', 'telephone', 'contact']
        return any(keyword in query.lower() for keyword in keywords)