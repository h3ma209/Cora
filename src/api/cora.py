import ollama
import json
from src.api import utils
from src.rag.retriever import get_retriever


# Initialize retriever (lazy loading)
_retriever = None


def get_rag_retriever():
    """Get or create retriever instance."""
    global _retriever
    if _retriever is None:
        try:
            _retriever = get_retriever()
            print("✓ RAG retriever initialized")
        except Exception as e:
            print(f"⚠️  RAG retriever failed to initialize: {e}")
            print("   Falling back to non-RAG mode")
            _retriever = None
    return _retriever


# Your engineered prompt
def get_json_classification(user_input, use_rag=True):
    """
    Calls the local Ollama instance running Qwen2.5:1.5b.

    Args:
        user_input: User query text
        use_rag: Whether to use RAG for context retrieval (default: True)
    """

    # Ensure model is present locally
    ollama.pull(utils.model_name)

    # Get base system prompt
    base_prompt = utils.read_prompt()

    # Enhance with RAG if enabled
    enhanced_prompt = base_prompt
    if use_rag:
        try:
            retriever = get_rag_retriever()
            if retriever:
                # Retrieve relevant context
                context = retriever.retrieve_and_format(
                    query=user_input,
                    language=None,  # Auto-detect from all languages
                    app_name=None,  # Search across all apps
                )

                if context:
                    # Insert context before the closing """
                    if '"""' in base_prompt:
                        parts = base_prompt.rsplit('"""', 1)
                        enhanced_prompt = parts[0] + "\n" + context + '\n"""' + parts[1]
                    else:
                        enhanced_prompt = base_prompt + "\n" + context

                    print(f"✓ RAG: Retrieved {len(context)} chars of context")
        except Exception as e:
            print(f"⚠️  RAG retrieval failed: {e}")
            print("   Using base prompt without RAG")

    try:
        response = ollama.generate(
            model=utils.model_name,
            system=enhanced_prompt,
            prompt=user_input,
            format="json",  # CRITICAL: Forces Qwen into JSON-mode
            options={
                "temperature": 0.0,  # Zero randomness for mapping consistency
                "top_p": 0.1,  # Pick only the most certain words
                "seed": 42,  # Further ensures deterministic output
            },
        )

        # Parse the raw string into a Python Dictionary
        return json.loads(response["response"])

    except Exception as e:
        return {"error": f"Ollama connection failed: {str(e)}"}


# --- Example Usage ---
if __name__ == "__main__":
    # Assuming this text was already translated by our NLLB manual mode:
    english_payload = "i truly hate this company and its products"

    result = get_json_classification(english_payload)
    print(json.dumps(result, indent=2, ensure_ascii=False))
