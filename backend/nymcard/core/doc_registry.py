import json
import hashlib
import os
from ..utils.helpers import get_project_root

REGISTRY_FILE = os.path.join(get_project_root(), "nymcard", "data", "ingested_docs.json")

def load_registry() -> dict:
    """Load the ingestion registry from a JSON file."""
    if not os.path.exists(REGISTRY_FILE):
        return {}
    with open(REGISTRY_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_registry(registry: dict):
    """Save the ingestion registry to a JSON file."""
    with open(REGISTRY_FILE, 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=2)

def compute_content_hash(text: str) -> str:
    """Compute a simple SHA256 hash of the text content."""
    return hashlib.sha256(text.encode('utf-8')).hexdigest()
