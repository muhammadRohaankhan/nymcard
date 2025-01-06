import unittest
from unittest.mock import patch, AsyncMock
from core.confluence_loader import ConfluenceLoader

class TestConfluenceLoader(unittest.TestCase):

    @patch('core.confluence_loader.Confluence')
    def test_fetch_all_pages_in_space(self, MockConfluence):
        # Setup mock
        mock_confluence_instance = MockConfluence.return_value
        mock_confluence_instance.cql.return_value = {
            "results": [
                {"content": {"id": "123", "title": "Page 1"}, "title": "Page 1"},
                {"content": {"id": "124", "title": "Page 2"}, "title": "Page 2"}
            ],
            "size": 2
        }
        mock_confluence_instance.get_page_by_id.return_value = {
            "body": {"storage": {"value": "<p>Content of Page 1</p>"}}
        }

        loader = ConfluenceLoader(url="http://example.com", username="user", api_token="token")
        result = asyncio.run(loader.fetch_all_pages_in_space("TD", limit=2))

        expected = [
            {
                "id": "123",
                "title": "Page 1",
                "body": {
                    "storage": {
                        "value": "<p>Content of Page 1</p>"
                    }
                }
            },
            {
                "id": "124",
                "title": "Page 2",
                "body": {
                    "storage": {
                        "value": "<p>Content of Page 1</p>"  # Adjust as needed
                    }
                }
            }
        ]

        self.assertEqual(result, expected)
        mock_confluence_instance.cql.assert_called_once()
        mock_confluence_instance.get_page_by_id.assert_called()

if __name__ == "__main__":
    unittest.main()
