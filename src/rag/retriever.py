"""
Retriever Module for Cora RAG System
Handles retrieval of relevant context from the vector store.
"""

from typing import List, Dict, Optional
from src.rag.vector_store import get_vector_store


class RAGRetriever:
    """
    Retrieves relevant context for RAG-enhanced classification.
    """

    def __init__(self, n_results: int = 3, similarity_threshold: float = 0.08):
        """
        Initialize the retriever.

        Args:
            n_results: Number of results to retrieve
            similarity_threshold: Minimum similarity score (0-1)
        """
        self.vector_store = get_vector_store()
        self.n_results = n_results
        self.similarity_threshold = similarity_threshold

    def retrieve(
        self, query: str, language: Optional[str] = None, app_name: Optional[str] = None
    ) -> List[Dict]:
        """
        Retrieve relevant context for a query.

        Args:
            query: User query text
            language: Optional language filter (en, ar, ku)
            app_name: Optional app name filter

        Returns:
            List of relevant documents with metadata
        """
        # Build metadata filter
        filter_metadata = {}
        if language:
            filter_metadata["language"] = language
        if app_name:
            filter_metadata["app_name"] = app_name

        # Search vector store
        results = self.vector_store.search(
            query=query,
            n_results=self.n_results,
            filter_metadata=filter_metadata if filter_metadata else None,
        )

        # Filter by similarity threshold
        # ChromaDB returns distances (lower is better), convert to similarity
        filtered_results = []
        for doc, metadata, distance in zip(
            results["documents"], results["metadatas"], results["distances"]
        ):
            # Convert distance to similarity (1 - normalized_distance)
            # Assuming L2 distance, normalize by dividing by max expected distance
            similarity = 1 / (1 + distance)  # Simple conversion

            if similarity >= self.similarity_threshold:
                filtered_results.append(
                    {
                        "document": doc,
                        "metadata": metadata,
                        "similarity": similarity,
                        "distance": distance,
                    }
                )

        return filtered_results

    def format_context(self, retrieved_docs: List[Dict]) -> str:
        """
        Format retrieved documents into context string for the prompt.

        Args:
            retrieved_docs: List of retrieved documents

        Returns:
            Formatted context string
        """
        if not retrieved_docs:
            return ""

        context = "\n### RETRIEVED CONTEXT:\n"
        context += "Use the following information to inform your classification:\n\n"

        for idx, doc_info in enumerate(retrieved_docs, 1):
            doc = doc_info["document"]
            metadata = doc_info["metadata"]
            similarity = doc_info["similarity"]

            # Add document with metadata
            context += f"[Source {idx}] "

            if metadata.get("source_type") == "article":
                context += f"[Article ID: {metadata.get('article_id')}] "
                context += f"[App: {metadata.get('app_name')}] "
                context += f"[Title: {metadata.get('title')}]\n"
            elif metadata.get("source_type") == "pdf":
                context += f"[PDF: {metadata.get('source_file')}] "
                context += f"[Chunk {metadata.get('chunk_index')}]\n"

            context += f"{doc}\n"
            context += "-" * 80 + "\n\n"

        return context

    def retrieve_and_format(
        self, query: str, language: Optional[str] = None, app_name: Optional[str] = None
    ) -> str:
        """
        Retrieve and format context in one step.

        Args:
            query: User query text
            language: Optional language filter
            app_name: Optional app name filter

        Returns:
            Formatted context string
        """
        retrieved_docs = self.retrieve(
            query=query, language=language, app_name=app_name
        )
        return self.format_context(retrieved_docs)

    def get_article_recommendations(
        self, query: str, language: Optional[str] = None, n_results: int = 3
    ) -> List[str]:
        """
        Get article ID recommendations based on query.

        Args:
            query: User query text
            language: Optional language filter
            n_results: Number of recommendations

        Returns:
            List of article IDs
        """
        # Retrieve relevant articles
        filter_metadata = {"source_type": "article"}
        if language:
            filter_metadata["language"] = language

        results = self.vector_store.search(
            query=query, n_results=n_results, filter_metadata=filter_metadata
        )

        # Extract unique article IDs
        article_ids = []
        seen_ids = set()

        for metadata in results["metadatas"]:
            article_id = metadata.get("article_id")
            if article_id and article_id not in seen_ids:
                article_ids.append(article_id)
                seen_ids.add(article_id)

        return article_ids


# Singleton instance
_retriever_instance = None


def get_retriever() -> RAGRetriever:
    """
    Get or create the singleton retriever instance.

    Returns:
        RAGRetriever instance
    """
    global _retriever_instance
    if _retriever_instance is None:
        _retriever_instance = RAGRetriever()
    return _retriever_instance
