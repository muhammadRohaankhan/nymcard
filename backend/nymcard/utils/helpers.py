import os
import re
import logging
import asyncio

logger = logging.getLogger(__name__)

def extract_urls(text: str) -> list:
    """Extract URLs from the given text."""
    url_pattern = re.compile(r'https?://\S+', re.IGNORECASE)
    urls = url_pattern.findall(text)
    logger.debug(f"Extracted URLs: {urls}")
    return urls

def extract_phone_numbers(text: str) -> list:
    """Extract phone numbers from the given text."""
    phone_pattern = re.compile(r'(\+?\d{1,3}[-.\s]?(\d{2,4}[-.\s]?){1,3}\d{3,4})')
    phones = phone_pattern.findall(text)
    extracted_phones = [ph[0] for ph in phones]
    logger.debug(f"Extracted Phone Numbers: {extracted_phones}")
    return extracted_phones

def run_async(coro):
    """Helper function to run async coroutines in synchronous code."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)

def clean_text(html_text: str) -> str:
    """Basic HTML cleanup."""
    text = re.sub(r"<[^>]+>", " ", html_text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def get_project_root() -> str:
    """Returns the absolute path to the project root directory."""
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

