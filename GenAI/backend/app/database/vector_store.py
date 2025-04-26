import os
import logging
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VectorStore:
    """
    Production-ready vector database implementation using ChromaDB
    """
    def __init__(self, collection_name: str = "insurance_data", persist_directory: str = "./vector_db"):
        """
        Initialize the vector store with HuggingFace embeddings
        """
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        
        # Create persist directory if it doesn't exist
        os.makedirs(self.persist_directory, exist_ok=True)
        
        # Initialize embedding model
        logger.info("Initializing embedding model")
        self.embedding_model = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",  # Lightweight but effective model
            model_kwargs={"device": "cpu"}  # Use GPU if available: "cuda"
        )
        
        # Initialize ChromaDB with persistent storage
        logger.info(f"Initializing ChromaDB with collection {collection_name}")
        self.db = Chroma(
            collection_name=collection_name,
            embedding_function=self.embedding_model,
            persist_directory=self.persist_directory
        )
        logger.info("Vector store initialized")
    
    def add_documents(self, texts: List[str], metadatas: Optional[List[Dict[str, Any]]] = None) -> List[str]:
        """
        Add documents to the vector store
        
        Args:
            texts: List of text content to add
            metadatas: Optional list of metadata dictionaries, one per text
            
        Returns:
            List of document IDs
        """
        logger.info(f"Adding {len(texts)} documents to vector store")
        try:
            return self.db.add_texts(texts=texts, metadatas=metadatas)
        except Exception as e:
            logger.error(f"Error adding documents to vector store: {e}")
            raise
    
    def similarity_search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar documents in the vector store
        
        Args:
            query: The search query text
            k: Number of results to return
            
        Returns:
            List of documents with their content and metadata
        """
        logger.info(f"Performing similarity search for query: {query[:30]}...")
        try:
            docs = self.db.similarity_search_with_score(query, k=k)
            results = []
            
            for doc, score in docs:
                results.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "similarity": float(score)
                })
            
            return results
        except Exception as e:
            logger.error(f"Error during similarity search: {e}")
            raise
    
    def delete_collection(self):
        """Delete the entire collection"""
        logger.info(f"Deleting collection {self.collection_name}")
        try:
            self.db.delete_collection()
            logger.info("Collection deleted successfully")
        except Exception as e:
            logger.error(f"Error deleting collection: {e}")
            raise

# Create a singleton instance for global use
vector_store = VectorStore()

def get_vector_store() -> VectorStore:
    """Dependency to get vector store instance"""
    return vector_store 