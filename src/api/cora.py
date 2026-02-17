import ollama
import json
from src.api import utils
from src.rag.retriever import get_retriever
from src.config import (
    DEFAULT_MODEL,
    CLASSIFICATION_TEMPERATURE,
    CLASSIFICATION_TOP_P,
    CLASSIFICATION_SEED,
    CLASSIFICATION_FORMAT,
)


# Initialize retriever (lazy loading)
_retriever = None
supported_languages = ["en", "ar", "kmr", "ckb"]


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
    Calls the local Ollama instance running qwen2.5:7b.

    Args:
        user_input: User query text
        use_rag: Whether to use RAG for context retrieval (default: True)
    """

    # Ensure model is present locally
    ollama.pull(DEFAULT_MODEL)

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

    # translated user input to en for better context retrieval
    try:
        auto_translation = utils.call_mt_api(user_input, source="auto", target="en")
    except Exception as e:
        print(f"⚠️  Text translation failed: {str(e)}")
        print("   Continuing without translations")

    try:
        response = ollama.generate(
            model=DEFAULT_MODEL,
            system=enhanced_prompt,
            prompt=auto_translation["translated_text"],
            format=CLASSIFICATION_FORMAT,  # CRITICAL: Forces Qwen into JSON-mode
            options={
                "temperature": CLASSIFICATION_TEMPERATURE,  # Zero randomness for mapping consistency
                "top_p": CLASSIFICATION_TOP_P,  # Pick only the most certain words
                "seed": CLASSIFICATION_SEED,  # Further ensures deterministic output
            },
        )

        json_resp = json.loads(response["response"])

        # optional: this section will be removed in production this is only for demo
        summaries = json_resp["summaries"]
        en_summary = summaries["en"]

        # translate en_summary to all supported languages
        try:
            all_langs_translation = utils.call_mt_all_langs_api(
                en_summary, source="", target=""
            )
            for summary in all_langs_translation["translated_text"]:
                summaries[summary] = all_langs_translation["translated_text"][summary]
        except Exception as e:
            print(f"⚠️  Text translation failed: {str(e)}")
            print("   Continuing without translations")

        # Parse the raw string into a Python Dictionary
        return json_resp

    except Exception as e:
        return {"error": f"Ollama connection failed: {str(e)}"}


# --- Example Usage ---
if __name__ == "__main__":
    # Assuming this text was already translated by our NLLB manual mode:
    english_payload = "i truly hate this company and its products"

    result = get_json_classification(english_payload)
    print(json.dumps(result, indent=2, ensure_ascii=False))
