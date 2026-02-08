#!/usr/bin/env python3
"""
Knowledge Base Indexer for Cora RAG System
Indexes JSON articles and PDF documents into the vector store.

Usage:
    python3 indexer.py                    # Index all files
    python3 indexer.py --reset            # Reset and reindex
    python3 indexer.py --stats            # Show statistics
"""

import json
import os
import sys
from pathlib import Path
from typing import List
import argparse

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

from src.rag.vector_store import get_vector_store


class KnowledgeIndexer:
    """
    Indexes documents from JSON and PDF files into the vector store.
    """

    def __init__(self):
        self.vector_store = get_vector_store()
        self.documents = []
        self.metadatas = []
        self.ids = []

    def _add_document(self, text: str, metadata: dict, doc_id: str):
        """
        Add a document to the internal buffer.

        Args:
            text: Document content
            metadata: Document metadata
            doc_id: Unique document ID
        """
        self.documents.append(text)
        self.metadatas.append(metadata)
        self.ids.append(doc_id)

    def index_json_file(self, file_path: str) -> int:
        """
        Index articles from a JSON file.

        Args:
            file_path: Path to JSON file

        Returns:
            Number of articles indexed
        """
        print(f"\nProcessing JSON: {file_path}")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            articles = data if isinstance(data, list) else [data]
            count = 0

            for article in articles:
                article_id = str(article.get("id", "unknown"))
                app_name = article.get("app_name", "unknown")
                title = article.get("title", "Untitled")

                # Index each language variant separately
                languages = {
                    "en": article.get("content", ""),
                    "ar": article.get("content_ar", ""),
                    "ku": article.get("content_ku", ""),
                }

                for lang, content in languages.items():
                    if content and content.strip():
                        # Create document text
                        doc_text = f"Title: {title}\n\n{content}"

                        # Create unique ID
                        doc_id = f"article_{article_id}_{lang}"

                        # Create metadata
                        metadata = {
                            "source_type": "article",
                            "source_file": os.path.basename(file_path),
                            "article_id": article_id,
                            "app_name": app_name,
                            "title": title,
                            "language": lang,
                        }

                        self._add_document(doc_text, metadata, doc_id)
                        count += 1

            print(f"  Indexed {count} article variants")
            return count

        except Exception as e:
            print(f"  Error: {e}")
            return 0

    def index_pdf_file(self, file_path: str, chunk_size: int = 1000) -> int:
        """
        Index content from a PDF file.

        Args:
            file_path: Path to PDF file
            chunk_size: Size of text chunks (characters)

        Returns:
            Number of chunks indexed
        """
        print(f"\nProcessing PDF: {file_path}")

        if PyPDF2 is None:
            print("  PyPDF2 not installed")
            return 0

        try:
            with open(file_path, "rb") as f:
                pdf_reader = PyPDF2.PdfReader(f)
                num_pages = len(pdf_reader.pages)

                print(f"  Pages: {num_pages}")

                # Extract all text
                full_text = ""
                for page_num in range(num_pages):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    if text.strip():
                        full_text += f"\n--- Page {page_num + 1} ---\n{text}"

                # Chunk the text
                chunks = self._chunk_text(full_text, chunk_size)
                count = 0

                for idx, chunk in enumerate(chunks):
                    if chunk.strip():
                        # Create unique ID
                        doc_id = f"pdf_{Path(file_path).stem}_chunk_{idx}"

                        # Create metadata
                        metadata = {
                            "source_type": "pdf",
                            "source_file": os.path.basename(file_path),
                            "chunk_index": idx,
                            "total_chunks": len(chunks),
                            "language": "en",  # Assume English for PDFs
                        }

                        self._add_document(chunk, metadata, doc_id)
                        count += 1

                print(f"  Indexed {count} chunks")
                return count

        except Exception as e:
            print(f"  ✗ Error: {e}")
            return 0

    def _chunk_text(
        self, text: str, chunk_size: int = 1000, overlap: int = 100
    ) -> List[str]:
        """
        Split text into overlapping chunks.

        Args:
            text: Text to chunk
            chunk_size: Size of each chunk
            overlap: Overlap between chunks

        Returns:
            List of text chunks
        """
        chunks = []
        start = 0
        text_length = len(text)

        while start < text_length:
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start += chunk_size - overlap

        return chunks

    def index_directory(self, directory: str, recursive: bool = True) -> int:
        """
        Index all JSON and PDF files in a directory.

        Args:
            directory: Directory path
            recursive: Whether to search recursively

        Returns:
            Total number of documents indexed
        """
        print(f"\nIndexing directory: {directory}")

        total_count = 0

        # Find all JSON and PDF files
        if recursive:
            json_files = list(Path(directory).rglob("*.json"))
            pdf_files = list(Path(directory).rglob("*.pdf"))
        else:
            json_files = list(Path(directory).glob("*.json"))
            pdf_files = list(Path(directory).glob("*.pdf"))

        print(f"  Found {len(json_files)} JSON files and {len(pdf_files)} PDF files")

        # Index JSON files
        for json_file in json_files:
            # Skip files with "ignored" in the name
            if "ignored" in json_file.name.lower():
                print(f"\nSkipping: {json_file} (ignored)")
                continue
            total_count += self.index_json_file(str(json_file))

        # Index PDF files
        for pdf_file in pdf_files:
            total_count += self.index_pdf_file(str(pdf_file))

        return total_count

    def commit(self) -> None:
        """
        Commit all indexed documents to the vector store.
        """
        if not self.documents:
            print("\nWarning: No documents to index")
            return

        print(f"\nCommitting {len(self.documents)} documents to vector store...")
        self.vector_store.add_documents(
            documents=self.documents, metadatas=self.metadatas, ids=self.ids
        )
        print("Indexing complete!")

        # Clear buffers
        self.documents = []
        self.metadatas = []
        self.ids = []


def main():
    parser = argparse.ArgumentParser(description="Index knowledge base for Cora RAG")
    parser.add_argument(
        "--reset", action="store_true", help="Reset vector store before indexing"
    )
    parser.add_argument(
        "--stats", action="store_true", help="Show vector store statistics"
    )
    parser.add_argument(
        "--data-dir", default="./data", help="Data directory to index (default: ./data)"
    )

    args = parser.parse_args()

    print("=" * 60)
    print("Cora Knowledge Base Indexer")
    print("=" * 60)

    indexer = KnowledgeIndexer()

    # Show stats
    if args.stats:
        stats = indexer.vector_store.get_collection_stats()
        print("\nVector Store Statistics:")
        print(f"  Collection: {stats['collection_name']}")
        print(f"  Documents: {stats['document_count']}")
        print(f"  Location: {stats['persist_directory']}")
        return

    # Reset if requested
    if args.reset:
        print("\nResetting vector store...")
        response = input("Are you sure? This will delete all indexed data (y/n): ")
        if response.lower() == "y":
            indexer.vector_store.reset()
        else:
            print("Aborted.")
            return

    # Check if data directory exists
    if not os.path.exists(args.data_dir):
        print(f"\nError: Data directory not found: {args.data_dir}")
        sys.exit(1)

    # Index all files
    total = indexer.index_directory(args.data_dir, recursive=True)

    # Commit to vector store
    indexer.commit()

    # Show final stats
    stats = indexer.vector_store.get_collection_stats()
    print("\nFinal Statistics:")
    print(f"  Total documents indexed: {total}")
    print(f"  Total in vector store: {stats['document_count']}")
    print(f"  Location: {stats['persist_directory']}")

    print("\nDone! Your knowledge base is ready for RAG.")


if __name__ == "__main__":
    main()
