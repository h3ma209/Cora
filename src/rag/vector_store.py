"""
Vector Store Module for Cora RAG System
Handles ChromaDB operations for storing and retrieving document embeddings.
"""

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Optional


class VectorStore:
    """
    Manages vector embeddings and similarity search using ChromaDB.
    """

    def __init__(
        self,
        persist_directory: str = "./chroma_db",
        collection_name: str = "rayied_knowledge_base",
        embedding_model: str = "paraphrase-multilingual-mpnet-base-v2",
    ):
        """
        Initialize the vector store.

        Args:
            persist_directory: Directory to persist ChromaDB data
            collection_name: Name of the collection
            embedding_model: Sentence transformer model name
        """
        self.persist_directory = persist_directory
        self.collection_name = collection_name

        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(anonymized_telemetry=False, allow_reset=True),
        )

        # Initialize embedding model
        from src.config import DEVICE

        print(f"Loading embedding model: {embedding_model} on {DEVICE}")
        self.embedding_model = SentenceTransformer(embedding_model, device=DEVICE)
        print(f"✓ Embedding model loaded on {DEVICE}")

        # Get or create collection
        try:
            self.collection = self.client.get_collection(name=collection_name)
            print(f"✓ Loaded existing collection: {collection_name}")
        except:
            self.collection = self.client.create_collection(
                name=collection_name,
                metadata={"description": "Rayied knowledge base for RAG"},
            )
            print(f"✓ Created new collection: {collection_name}")

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.

        Args:
            texts: List of text strings

        Returns:
            List of embedding vectors
        """
        embeddings = self.embedding_model.encode(
            texts, convert_to_numpy=True, show_progress_bar=True
        )
        return embeddings.tolist()

    def add_documents(
        self, documents: List[str], metadatas: List[Dict], ids: List[str]
    ) -> None:
        """
        Add documents to the vector store.

        Args:
            documents: List of document texts
            metadatas: List of metadata dictionaries
            ids: List of unique document IDs
        """
        print(f"Generating embeddings for {len(documents)} documents...")
        embeddings = self.generate_embeddings(documents)

        print("Adding documents to collection...")
        self.collection.add(
            documents=documents, embeddings=embeddings, metadatas=metadatas, ids=ids
        )
        print(f"✓ Added {len(documents)} documents to vector store")

    def search(
        self, query: str, n_results: int = 5, filter_metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Search for similar documents.

        Args:
            query: Search query text
            n_results: Number of results to return
            filter_metadata: Optional metadata filters (e.g., {"app_name": "ana"})

        Returns:
            Dictionary with documents, metadatas, and distances
        """
        # Generate query embedding
        query_embedding = self.generate_embeddings([query])[0]

        # Search
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=filter_metadata if filter_metadata else None,
        )

        return {
            "documents": results["documents"][0] if results["documents"] else [],
            "metadatas": results["metadatas"][0] if results["metadatas"] else [],
            "distances": results["distances"][0] if results["distances"] else [],
        }

    def get_collection_stats(self) -> Dict:
        """
        Get statistics about the collection.

        Returns:
            Dictionary with collection statistics
        """
        count = self.collection.count()
        return {
            "collection_name": self.collection_name,
            "document_count": count,
            "persist_directory": self.persist_directory,
        }

    def delete_collection(self) -> None:
        """
        Delete the entire collection (use with caution).
        """
        self.client.delete_collection(name=self.collection_name)
        print(f"✓ Deleted collection: {self.collection_name}")

    def reset(self) -> None:
        """
        Reset the vector store (delete and recreate collection).
        """
        try:
            self.delete_collection()
        except:
            pass

        self.collection = self.client.create_collection(
            name=self.collection_name,
            metadata={"description": "Rayied knowledge base for RAG"},
        )
        print(f"✓ Reset collection: {self.collection_name}")


# Singleton instance
_vector_store_instance = None


def get_vector_store() -> VectorStore:
    """
    Get or create the singleton vector store instance.

    Returns:
        VectorStore instance
    """
    global _vector_store_instance
    if _vector_store_instance is None:
        _vector_store_instance = VectorStore()
    return _vector_store_instance
