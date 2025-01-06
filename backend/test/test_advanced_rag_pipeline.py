# nymcard_project/test/test_advanced_rag_pipeline.py

import unittest
from unittest.mock import MagicMock, patch
from core.advanced_rag_pipeline import CustomConversationalRAGPipeline
from utils.helpers import get_project_root
from unittest.mock import AsyncMock
import os

class TestAdvancedRAGPipeline(unittest.TestCase):

    @patch("core.advanced_rag_pipeline.HybridRetriever")
    @patch("core.advanced_rag_pipeline.ConversationBufferMemory")
    @patch("core.advanced_rag_pipeline.ChatOpenAI")
    def setUp(self, MockChatOpenAI, MockMemory, MockRetriever):
        self.mock_memory = MockMemory.return_value
        self.mock_memory.load_memory_variables.return_value = {"chat_history": []}
        
        self.mock_retriever = MockRetriever.return_value
        self.mock_retriever.retrieve = AsyncMock(return_value=[])
        
        self.mock_llm = MockChatOpenAI.return_value
        self.mock_llm.content = "Mocked LLM Response"
        
        self.pipeline = CustomConversationalRAGPipeline(
            vectorstore_manager=self.mock_retriever,
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            all_docs_text=["Document 1 content", "Document 2 content"]
        )

    def run_async(self, coro):
        return asyncio.get_event_loop().run_until_complete(coro)

    @patch("core.advanced_rag_pipeline.fetch_and_ingest_pages")
    def test_basic_query_with_embedding_retrieval(self, MockFetchAndIngest):
        """
        Test a basic query that triggers embedding-based retrieval without any specialized extraction.
        """
        # Setup mocks
        MockFetchAndIngest.return_value = (1, ["Document 1 content", "Document 2 content"])
        self.mock_retriever.retrieve = AsyncMock(return_value=[("Relevant document content", {"meta": "data"})])
        self.mock_llm.content = "Basic Query Answer"

        # Perform the query
        response = self.run_async(self.pipeline.query("What is the status of Project Aurora?"))

        # Assertions
        self.assertEqual(response, "Basic Query Answer")
        self.mock_retriever.retrieve.assert_awaited_once_with("What is the status of Project Aurora?")
        self.mock_llm.assert_called_once()


if __name__ == "__main__":
    unittest.main()
