from flask import Flask, request, jsonify
import asyncio
from flask_cors import CORS  
import logging
import os

from ..core.vectorstore_manager import VectorStoreManager
from ..core.advanced_rag_pipeline import CustomConversationalRAGPipeline
from ..utils.helpers import run_async

app = Flask(__name__)
CORS(app) 


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

from dotenv import load_dotenv
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

vs_manager = VectorStoreManager()
pipeline = CustomConversationalRAGPipeline(
    vectorstore_manager=vs_manager,
    openai_api_key=OPENAI_API_KEY,
    all_docs_text=[] 
)

@app.route('/query', methods=['POST'])
def query():
    """
    Endpoint to handle user queries.
    Expects JSON payload: { "question": "Your question here" }
    """
    data = request.get_json()
    if not data or 'question' not in data:
        return jsonify({"error": "Invalid request. 'question' field is required."}), 400
    
    question = data['question']
    logger.info(f"Received query: {question}")
    
    try:
        answer = run_async(pipeline.query(question))
        return jsonify({"answer": answer}), 200
    except Exception as e:
        logger.error(f"Error processing query: {e}", exc_info=True)
        return jsonify({"error": "An error occurred while processing the query."}), 500

@app.route('/ingest', methods=['POST'])
def ingest():
    """
    Endpoint to trigger ingestion of Confluence pages.
    Expects JSON payload: { "space_key": "TD" } (optional)
    """
    data = request.get_json()
    space_key = data.get('space_key', 'TD') if data else 'TD'
    logger.info(f"Starting ingestion for space_key: {space_key}")
    
    from main import fetch_and_ingest_pages  # Import here to avoid circular imports
    
    try:
        updated_count, all_docs_text = run_async(fetch_and_ingest_pages(space_key, vs_manager))
        return jsonify({
            "message": "Ingestion complete.",
            "updated_count": updated_count
        }), 200
    except Exception as e:
        logger.error(f"Error during ingestion: {e}", exc_info=True)
        return jsonify({"error": "An error occurred during ingestion."}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """
    Simple health check endpoint to verify the API is running.
    """
    return jsonify({"status": "OK"}), 200

@app.route('/documents', methods=['GET'])
def get_documents():
    """
    Endpoint to retrieve all ingested documents.
    """
    from core.doc_registry import load_registry
    registry = load_registry()
    return jsonify({"documents": registry}), 200

@app.route('/documents/<page_id>', methods=['DELETE'])
def delete_document(page_id):
    """
    Endpoint to delete a document from the vector store based on page_id.
    """
    try:
        from core.vectorstore_manager import VectorStoreManager
        vs_manager = VectorStoreManager()
        vs_manager.delete_document(page_id)
        return jsonify({"message": f"Document {page_id} deleted successfully."}), 200
    except Exception as e:
        logger.error(f"Error deleting document {page_id}: {e}", exc_info=True)
        return jsonify({"error": "An error occurred while deleting the document."}), 500
