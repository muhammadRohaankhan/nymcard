import re
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

def clean_text(html_text: str) -> str:
    """Basic HTML cleanup."""
    text = re.sub(r"<[^>]+>", " ", html_text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def chunk_text(text: str, chunk_size=500, overlap=50) -> List[str]:
    """Split text into chunks with optional overlap."""
    words = text.split()
    chunks = []
    start = 0

    while start < len(words):
        end = start + chunk_size
        chunk = words[start:end]
        chunks.append(" ".join(chunk))
        start = end - overlap
        if start < 0:
            start = 0
        if start >= len(words):
            break

    return chunks

def process_confluence_page(page: Dict) -> Dict:
    """
    Returns a dict with: 
      - 'page_id'
      - 'title'
      - 'cleaned_text'
      - 'chunks' (list of chunked strings)
    """
    page_id = page.get("id", "")
    title = page.get("title", "")
    body = page.get("body", {}).get("storage", {}).get("value", "")

    logger.info(f"[PROCESS_PAGE] Processing page ID={page_id}, title={title}")
    cleaned = clean_text(body)
    chunks = chunk_text(cleaned)

    return {
        "page_id": page_id,
        "title": title,
        "cleaned_text": cleaned,
        "chunks": chunks
    }
