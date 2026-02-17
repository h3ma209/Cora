import os
import requests
from typing import Dict, Any
from src.config import TRANSLATOR_API_URL

# read the prompt.txt and return the prompt as string


def read_prompt():
    # Get path relative to project root
    base_dir = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    prompt_path = os.path.join(base_dir, "config", "prompt.txt")
    with open(prompt_path, "r") as f:
        return f.read()


def call_mt_api(text: str, source: str = "auto", target: str = "en") -> Dict[str, Any]:
    """
    Call the external Machine Translation API.

    Args:
        text: Text to translate
        source: Source language code (default: auto)
        target: Target language code (default: en)

    Returns:
        Dictionary with keys: translated_text, source_lang, target_lang
    """
    try:
        response = requests.post(
            f"{TRANSLATOR_API_URL}/translate",
            json={"text": text, "source_lang": source, "target_lang": target},
            timeout=30,
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"MT API Error: {e}")
        return {
            "translated_text": text,
            "source_lang": source,
            "target_lang": target,
        }


def call_mt_all_langs_api(
    text: str, source: str = "auto", target: str = "en"
) -> Dict[str, Any]:
    """
    Call the external Machine Translation API.

    Args:
        text: Text to translate
        source: Source language code (default: auto)
        target: Target language code (default: en)

    Returns:
        Dictionary with keys: translated_text, source_lang, target_lang
    """
    try:
        response = requests.post(
            f"{TRANSLATOR_API_URL}/translate/all",
            json={"text": text, "source_lang": source, "target_lang": target},
            timeout=30,
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"MT API Error: {e}")
        return {
            "translated_text": text,
            "source_lang": source,
            "target_lang": target,
        }
