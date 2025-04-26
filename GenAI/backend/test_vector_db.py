import os
import logging
from dotenv import load_dotenv
from app.database.vector_store import VectorStore

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def test_vector_search():
    """Test vector database search functionality."""
    
    # Initialize vector store
    collection_name = os.getenv("VECTOR_COLLECTION_NAME", "insurance_data")
    persist_directory = os.getenv("VECTOR_DB_PATH", "./vector_db")
    
    logger.info(f"Initializing vector store with collection '{collection_name}' at '{persist_directory}'")
    vector_store = VectorStore(collection_name=collection_name, persist_directory=persist_directory)
    
    # Perform a test search
    query = "insurance underwriting for elderly applicants with health conditions"
    
    logger.info(f"Performing search with query: {query}")
    results = vector_store.similarity_search(query, k=2)
    
    logger.info(f"Retrieved {len(results)} results")
    for i, result in enumerate(results):
        logger.info(f"Result {i+1}: {result['content'][:100]}... (score: {result['similarity']})")
    
    return results

if __name__ == "__main__":
    logger.info("Starting vector database test")
    results = test_vector_search()
    logger.info("Vector database test completed successfully") 