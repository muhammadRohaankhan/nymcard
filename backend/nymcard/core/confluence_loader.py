import logging
from atlassian import Confluence

logger = logging.getLogger(__name__)


class ConfluenceLoader:
    """
    Class responsible for fetching pages, attachments, etc. from Confluence.
    """

    def __init__(self, url: str, username: str, api_token: str):
        self.confluence = Confluence(
            url=url,
            username=username,
            password=api_token
        )

    async def fetch_all_pages_in_space(self, space_key: str, limit: int = 50):
        """
        Fetch all pages from a Confluence space using CQL, since 
        get_all_pages_from_space() is giving 'Current user not permitted' errors.
        
        Returns a list of dicts, each with:
            {
              "id": <page_id>,
              "title": <title_string>,
              "body": {
                "storage": {
                  "value": <page_body_html>
                }
              }
            }
        """
        logger.info(f"Fetching pages from space via CQL: {space_key}")
        all_pages = []
        start = 0

        while True:
            # Only fetch page-type content in that space
            cql_str = f"space='{space_key}' AND type=page"
            logger.debug(f"Running CQL: {cql_str} start={start}, limit={limit}")

            response = self.confluence.cql(cql_str, limit=limit, start=start)
            results = response.get("results", [])
            if not results:
                break

            for r in results:
                content = r.get("content", {})
                page_id = content.get("id")
                title = r.get("title")

                body = self._fetch_page_body(page_id)

                page_dict = {
                    "id": page_id,
                    "title": title,
                    "body": {
                        "storage": {
                            "value": body
                        }
                    }
                }
                all_pages.append(page_dict)

            returned_size = response.get("size", 0)
            if returned_size < limit:
                # No more results
                break
            start += limit

        logger.info(f"Found {len(all_pages)} pages via CQL for space={space_key}")
        return all_pages

    def _fetch_page_body(self, page_id: str) -> str:
        """
        Fetch the full HTML storage of a Confluence page by ID.
        This is a synchronous call, but easy for demonstration.
        """
        try:
            page = self.confluence.get_page_by_id(page_id, expand="body.storage")
            return page.get("body", {}).get("storage", {}).get("value", "")
        except Exception as e:
            logger.error(f"Error fetching page content for page_id={page_id}: {e}")
            return ""
