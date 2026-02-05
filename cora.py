import ollama
import json
import utils


# Your engineered prompt
def get_json_classification(user_input):
    """
    Calls the local Ollama instance running Qwen2.5:1.5b.
    """

    # Ensure model is present locally
    ollama.pull(utils.model_name)

    try:
        response = ollama.generate(
            model=utils.model_name,
            system=utils.read_prompt(),
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
