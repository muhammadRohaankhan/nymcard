import unittest
from unittest.mock import patch, AsyncMock
import asyncio

from core.vectorstore_manager import VectorStoreManager
from core.confluence_loader import ConfluenceLoader
from core.doc_processor import process_confluence_page
from core.doc_registry import load_registry, save_registry
from main import fetch_and_ingest_pages, run_ingestion_only, run_all

class TestMain(unittest.TestCase):

    @patch('main.VectorStoreManager')
    @patch('main.ConfluenceLoader')
    @patch('main.process_confluence_page')
    @patch('main.load_registry')
    @patch('main.save_registry')
    def test_fetch_and_ingest_pages(self, mock_save_registry, mock_load_registry, mock_process_page, MockLoader, MockManager):
        mock_load_registry.return_value = {}  # Simulate no existing registry
        mock_loader_instance = MockLoader.return_value
        mock_loader_instance.fetch_all_pages_in_space = AsyncMock(return_value=[{
            "id": "1",
            "title": "Test Page",
            "body": {"storage": {"value": "<p>Test content</p>"}}
        }])
        mock_process_page.return_value = {
            "page_id": "1",
            "cleaned_text": "Test content",
            "chunks": ["Test content"],
            "title": "Test Page"
        }
        mock_manager_instance = MockManager.return_value
        mock_manager_instance.add_texts = AsyncMock()
        
        updated_count, all_docs_text = asyncio.run(fetch_and_ingest_pages("TEST_SPACE", mock_manager_instance))
        
        self.assertEqual(updated_count, 1)
        self.assertEqual(all_docs_text, ["Test content"])
        mock_manager_instance.add_texts.assert_awaited_once()

    @patch('main.VectorStoreManager')
    @patch('main.ConfluenceLoader')
    @patch('main.process_confluence_page')
    @patch('main.load_registry')
    @patch('main.save_registry')
    def test_run_ingestion_only(self, mock_save_registry, mock_load_registry, mock_process_page, MockLoader, MockManager):
        mock_load_registry.return_value = {}
    
        mock_loader_instance = MockLoader.return_value
        mock_loader_instance.fetch_all_pages_in_space = AsyncMock(return_value=[{
            "id": "1",
            "title": "Test Page",
            "body": {"storage": {"value": "<p>Test content</p>"}}
        }])
    
        mock_process_page.return_value = {
            "page_id": "1",
            "cleaned_text": "Test content",
            "chunks": ["Test content"],
            "title": "Test Page"
        }
    
        mock_manager_instance = MockManager.return_value
        mock_manager_instance.add_texts = AsyncMock()
    
        asyncio.run(run_ingestion_only())
    
        mock_manager_instance.add_texts.assert_awaited_once()

    @patch('main.VectorStoreManager')
    @patch('main.ConfluenceLoader')
    @patch('main.process_confluence_page')
    @patch('main.load_registry')
    @patch('main.save_registry')
    @patch('main.interactive_query_loop')
    def test_run_all(self, mock_query_loop, mock_save_registry, mock_load_registry, mock_process_page, MockLoader, MockManager):
        mock_load_registry.return_value = {}
    
        mock_loader_instance = MockLoader.return_value
        mock_loader_instance.fetch_all_pages_in_space = AsyncMock(return_value=[{
            "id": "1",
            "title": "Test Page",
            "body": {"storage": {"value": "<p>Test content</p>"}}
        }])
    
        mock_process_page.return_value = {
            "page_id": "1",
            "cleaned_text": "Test content",
            "chunks": ["Test content"],
            "title": "Test Page"
        }
    
        mock_manager_instance = MockManager.return_value
        mock_manager_instance.add_texts = AsyncMock()
    
        mock_query_loop.return_value = AsyncMock()
    
        asyncio.run(run_all())
    
        mock_manager_instance.add_texts.assert_awaited_once()
    
        mock_query_loop.assert_awaited_once()

if __name__ == "__main__":
    unittest.main()
