import unittest
from unittest.mock import patch, AsyncMock, MagicMock
import asyncio

from core.vectorstore_manager import VectorStoreManager
from core.hybrid_retriever import HybridRetriever

class TestHybridRetriever(unittest.IsolatedAsyncioTestCase):

    @patch('core.hybrid_retriever.VectorStoreManager')
    async def test_retrieve_url_query(self, MockVectorStoreManager):
        # Setup mock vector store manager
        mock_vs_manager = MockVectorStoreManager.return_value
        mock_vs_manager.similarity_search_with_scores = AsyncMock(return_value=[
            ("Check our website at https://example.com for more info.", {"source": "doc1"}, 0.95)
        ])
        
        retriever = HybridRetriever(vectorstore_manager=mock_vs_manager, all_docs_text=[])
        result = await retriever.retrieve("Provide all URLs related to authentication.")
        
        expected = [
            ("Check our website at https://example.com for more info.", {"source": "doc1", "score": 0.95}),
            ("https://example.com", {"type": "url_extraction"})
        ]
        
        self.assertEqual(result, expected)

    @patch('core.hybrid_retriever.VectorStoreManager')
    async def test_retrieve_phone_query(self, MockVectorStoreManager):
        # Setup mock vector store manager
        mock_vs_manager = MockVectorStoreManager.return_value
        mock_vs_manager.similarity_search_with_scores = AsyncMock(return_value=[
            ("Contact us at +1-800-555-1234 for support.", {"source": "doc2"}, 0.90)
        ])
        
        retriever = HybridRetriever(vectorstore_manager=mock_vs_manager, all_docs_text=[])
        result = await retriever.retrieve("What is the contact phone number?")
        
        expected = [
            ("Contact us at +1-800-555-1234 for support.", {"source": "doc2", "score": 0.90}),
            ("+1-800-555-1234", {"type": "phone_extraction"})
        ]
        
        self.assertEqual(result, expected)

    @patch('core.hybrid_retriever.VectorStoreManager')
    async def test_retrieve_semantic_query(self, MockVectorStoreManager):
        # Setup mock vector store manager
        mock_vs_manager = MockVectorStoreManager.return_value
        mock_vs_manager.similarity_search_with_scores = AsyncMock(return_value=[
            ("Project Aurora user data handling.", {"source": "doc3"}, 0.85)
        ])
        
        retriever = HybridRetriever(vectorstore_manager=mock_vs_manager, all_docs_text=[])
        result = await retriever.retrieve("How does user data handling work in Project Aurora?")
        
        expected = [
            ("Project Aurora user data handling.", {"source": "doc3", "score": 0.85})
        ]
        
        self.assertEqual(result, expected)

    @patch('core.hybrid_retriever.VectorStoreManager')
    async def test_retrieve_fallback_query(self, MockVectorStoreManager):
        # Setup mock vector store manager
        mock_vs_manager = MockVectorStoreManager.return_value
        mock_vs_manager.similarity_search_with_scores = AsyncMock(return_value=[])
        
        retriever = HybridRetriever(vectorstore_manager=mock_vs_manager, all_docs_text=[])
        result = await retriever.retrieve("Explain the backup procedures.")
        
        expected = []
        
        self.assertEqual(result, expected)

if __name__ == "__main__":
    unittest.main()
