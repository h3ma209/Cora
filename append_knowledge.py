#!/usr/bin/env python3
"""
Knowledge Appender for Cora AI Classification Engine
Reads JSON or PDF files and appends their content to the model's knowledge base.

Usage:
    python append_knowledge.py <file_path>
    python append_knowledge.py data/jsons/articles.json
    python append_knowledge.py data/pdfs/app-docs/Rayied-Rayied\ Application\ Documentation.pdf
"""

import sys
import json
import os
from pathlib import Path

# PDF parsing libraries (will be added to requirements)
try:
    import PyPDF2
except ImportError:
    PyPDF2 = None


def read_json_file(file_path):
    """
    Read and parse JSON file containing articles.
    Returns formatted knowledge text.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        knowledge_text = "\n### KNOWLEDGE BASE FROM JSON:\n"

        # Handle both list of articles and single article object
        articles = data if isinstance(data, list) else [data]

        for article in articles:
            article_id = article.get("id", "N/A")
            app_name = article.get("app_name", "N/A")
            title = article.get("title", "N/A")
            content_en = article.get("content", "")
            content_ar = article.get("content_ar", "")
            content_ku = article.get("content_ku", "")

            knowledge_text += f"\n[Article ID: {article_id}] [{app_name}] {title}\n"

            if content_en:
                knowledge_text += f"EN: {content_en}\n"
            if content_ar:
                knowledge_text += f"AR: {content_ar}\n"
            if content_ku:
                knowledge_text += f"KU: {content_ku}\n"

            knowledge_text += "-" * 80 + "\n"

        return knowledge_text

    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON file - {e}")
        return None
    except Exception as e:
        print(f"Error reading JSON file: {e}")
        return None


def read_pdf_file(file_path):
    """
    Read and extract text from PDF file.
    Returns formatted knowledge text.
    """
    if PyPDF2 is None:
        print("Error: PyPDF2 not installed. Install with: pip install PyPDF2")
        return None

    try:
        knowledge_text = "\n### KNOWLEDGE BASE FROM PDF:\n"
        knowledge_text += f"Source: {os.path.basename(file_path)}\n\n"

        with open(file_path, "rb") as f:
            pdf_reader = PyPDF2.PdfReader(f)
            num_pages = len(pdf_reader.pages)

            print(f"Extracting text from {num_pages} pages...")

            for page_num in range(num_pages):
                page = pdf_reader.pages[page_num]
                text = page.extract_text()

                if text.strip():
                    knowledge_text += f"\n--- Page {page_num + 1} ---\n"
                    knowledge_text += text + "\n"

        return knowledge_text

    except Exception as e:
        print(f"Error reading PDF file: {e}")
        return None


def append_to_prompt(knowledge_text, prompt_file="prompt.txt"):
    """
    Append the extracted knowledge to the prompt.txt file.
    Creates a backup before modifying.
    """
    try:
        # Create backup
        backup_file = f"{prompt_file}.backup"
        if os.path.exists(prompt_file):
            with open(prompt_file, "r", encoding="utf-8") as f:
                original_content = f.read()

            with open(backup_file, "w", encoding="utf-8") as f:
                f.write(original_content)

            print(f"✓ Backup created: {backup_file}")

        # Read current prompt
        with open(prompt_file, "r", encoding="utf-8") as f:
            current_prompt = f.read()

        # Check if knowledge already exists (avoid duplicates)
        if "### KNOWLEDGE BASE FROM" in current_prompt:
            print("Warning: Existing knowledge base found in prompt.")
            response = input("Do you want to append anyway? (y/n): ").lower()
            if response != "y":
                print("Aborted.")
                return False

        # Append knowledge before the closing """
        # Find the last """ and insert before it
        if '"""' in current_prompt:
            parts = current_prompt.rsplit('"""', 1)
            new_prompt = parts[0] + knowledge_text + '\n"""' + parts[1]
        else:
            # If no closing """, just append
            new_prompt = current_prompt + "\n" + knowledge_text

        # Write updated prompt
        with open(prompt_file, "w", encoding="utf-8") as f:
            f.write(new_prompt)

        print(f"✓ Knowledge appended to {prompt_file}")
        return True

    except Exception as e:
        print(f"Error appending to prompt: {e}")
        return False


def main():
    if len(sys.argv) < 2:
        print("Usage: python append_knowledge.py <file_path>")
        print("\nExamples:")
        print("  python append_knowledge.py data/jsons/articles.json")
        print(
            "  python append_knowledge.py data/pdfs/app-docs/Rayied-Rayied\\ Application\\ Documentation.pdf"
        )
        sys.exit(1)

    file_path = sys.argv[1]

    # Check if file exists
    if not os.path.exists(file_path):
        print(f"Error: File not found - {file_path}")
        sys.exit(1)

    # Determine file type and process
    file_ext = Path(file_path).suffix.lower()

    print(f"Processing file: {file_path}")
    print(f"File type: {file_ext}")

    knowledge_text = None

    if file_ext == ".json":
        knowledge_text = read_json_file(file_path)
    elif file_ext == ".pdf":
        knowledge_text = read_pdf_file(file_path)
    else:
        print(f"Error: Unsupported file type - {file_ext}")
        print("Supported types: .json, .pdf")
        sys.exit(1)

    if knowledge_text is None:
        print("Failed to extract knowledge from file.")
        sys.exit(1)

    print(f"\n✓ Extracted {len(knowledge_text)} characters of knowledge")

    # Show preview
    print("\n--- Preview (first 500 chars) ---")
    print(knowledge_text[:500])
    print("...\n")

    # Confirm before appending
    response = input("Append this knowledge to prompt.txt? (y/n): ").lower()
    if response != "y":
        print("Aborted.")
        sys.exit(0)

    # Append to prompt
    if append_to_prompt(knowledge_text):
        print("\n✅ Success! Knowledge has been appended to the model.")
        print("The model will now use this information for classification.")
        print("\nNote: Restart the server for changes to take effect:")
        print("  docker-compose restart cora-api")
    else:
        print("\n❌ Failed to append knowledge.")
        sys.exit(1)


if __name__ == "__main__":
    main()
