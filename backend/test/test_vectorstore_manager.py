import unittest
from unittest.mock import patch, AsyncMock
from core.vectorstore_manager import VectorStoreManager

class TestVectorStoreManager(unittest.TestCase):

    @patch('core.vectorstore_manager.Chroma')
    @patch('core.vectorstore_manager.OpenAIEmbeddings')
    def setUp(self, MockOpenAIEmbeddings, MockChroma):
        self.mock_embeddings = MockOpenAIEmbeddings.return_value
        self.mock_chroma = MockChroma.return_value
        self.vs_manager = VectorStoreManager()

    @patch('core.vectorstore_manager.VectorStoreManager.add_texts', new_callable=AsyncMock)
    async def test_add_texts(self, mock_add_texts):
        texts = ["Sample text 1", "Sample text 2"]
        metadatas = [{"source": "doc1"}, {"source": "doc2"}]
        await self.vs_manager.add_texts(texts, metadatas)
        self.mock_chroma.add_texts.assert_called_once_with(texts, metadatas)
        self.mock_chroma.persist.assert_awaited_once()

    @patch('core.vectorstore_manager.VectorStoreManager.similarity_search_with_scores', new_callable=AsyncMock)
    async def test_similarity_search_with_scores(self, mock_similarity_search):
        mock_similarity_search.return_value = [
            ("Relevant document content", {"source": "doc1"}, 0.95)
        ]
        results = await self.vs_manager.similarity_search_with_scores("Test query")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][0], "Relevant document content")
        self.assertEqual(results[0][1], {"source": "doc1"})
        self.assertEqual(results[0][2], 0.95)

    @patch('core.vectorstore_manager.VectorStoreManager.delete_document', new_callable=AsyncMock)
    async def test_delete_document(self, mock_delete_document):
        await self.vs_manager.delete_document("123")
        self.mock_chroma.delete_document.assert_called_once_with("123")

if __name__ == "__main__":
    unittest.main()
