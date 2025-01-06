# nymcard_project/test/test_doc_processor.py

import unittest
from core.doc_processor import clean_text, chunk_text, process_confluence_page

class TestDocProcessor(unittest.TestCase):

    def test_clean_text(self):
        html = "<p>Test <b>HTML</b></p>"
        self.assertEqual(clean_text(html), "Test HTML")

    def test_chunk_text(self):
        text = "This is a sample text to test chunking."
        chunks = chunk_text(text, chunk_size=5, overlap=2)
        self.assertEqual(len(chunks), 3)
        self.assertEqual(chunks, [
            "This is a sample text",
            "text to test chunking.",
            "chunking."
        ])

    def test_process_confluence_page(self):
        page = {
            "id": "123",
            "title": "Test Page",
            "body": {"storage": {"value": "<p>Content</p>"}}
        }
        processed = process_confluence_page(page)
        self.assertEqual(processed["page_id"], "123")
        self.assertEqual(processed["title"], "Test Page")
        self.assertIn("Content", processed["cleaned_text"])
        self.assertEqual(processed["chunks"], ["Content"])

if __name__ == "__main__":
    unittest.main()
