"""
Tests for the Vector Store component
"""
import pytest
from app.database.vector_store import VectorStore


def test_vector_store_initialization(mock_vector_store):
    """Test that the vector store initializes correctly"""
    assert mock_vector_store is not None
    assert mock_vector_store.collection_name == "test_insurance_data"
    assert mock_vector_store.persist_directory == "./test_vector_db"
    assert mock_vector_store.db is not None
    assert mock_vector_store.embedding_model is not None


def test_add_documents_and_query(mock_vector_store):
    """Test adding documents and querying"""
    # Test documents
    test_docs = [
        "Insurance policy for diabetes covers medication and regular check-ups",
        "Health insurance for heart conditions requires additional premium",
        "Life insurance policy with coverage for terminal illness",
        "Travel insurance coverage for medical emergencies abroad",
        "Property insurance does not cover intentional damage"
    ]
    
    # Add documents
    doc_ids = mock_vector_store.add_documents(test_docs)
    
    # Verify IDs were returned
    assert len(doc_ids) == 5
    assert all(isinstance(id, str) for id in doc_ids)
    
    # Query for diabetes-related information
    results = mock_vector_store.similarity_search("diabetes medication coverage")
    
    # Should return results with the most relevant first
    assert len(results) > 0
    assert "diabetes" in results[0]["content"].lower()
    
    # Query for heart-related information
    results = mock_vector_store.similarity_search("heart condition insurance")
    
    # Should return results with the most relevant first
    assert len(results) > 0
    assert "heart" in results[0]["content"].lower()


def test_add_documents_with_metadata(mock_vector_store):
    """Test adding documents with metadata"""
    # Test documents with metadata
    test_docs = [
        "Insurance policy for diabetes covers medication and regular check-ups",
        "Health insurance for heart conditions requires additional premium"
    ]
    
    test_metadata = [
        {"category": "health", "condition": "diabetes", "coverage_level": "standard"},
        {"category": "health", "condition": "heart", "coverage_level": "premium"}
    ]
    
    # Add documents with metadata
    doc_ids = mock_vector_store.add_documents(test_docs, metadatas=test_metadata)
    
    # Verify IDs were returned
    assert len(doc_ids) == 2
    
    # Query for diabetes
    results = mock_vector_store.similarity_search("diabetes coverage")
    
    # Check first result has the expected metadata
    assert len(results) > 0
    assert "diabetes" in results[0]["content"].lower()
    assert results[0]["metadata"]["category"] == "health"
    assert results[0]["metadata"]["condition"] == "diabetes"


def test_error_handling(monkeypatch):
    """Test error handling in vector store methods"""
    vector_store = VectorStore(
        collection_name="test_error_handling",
        persist_directory="./test_error_db"
    )
    
    # Create a mock to simulate an error in the add_texts method
    class MockChroma:
        def add_texts(self, texts, metadatas):
            raise ValueError("Simulated error in add_texts")
        
        def similarity_search_with_score(self, query, k):
            raise ValueError("Simulated error in similarity_search")
        
        def delete_collection(self):
            raise ValueError("Simulated error in delete_collection")
    
    # Replace the db with our mock
    vector_store.db = MockChroma()
    
    # Test add_documents error handling
    with pytest.raises(ValueError):
        vector_store.add_documents(["test document"])
    
    # Test similarity_search error handling
    with pytest.raises(ValueError):
        vector_store.similarity_search("test query")
    
    # Test delete_collection error handling
    with pytest.raises(ValueError):
        vector_store.delete_collection() 