import os

# read the prompt.txt and return the prompt as string


def read_prompt():
    # Get path relative to project root
    base_dir = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    prompt_path = os.path.join(base_dir, "config", "prompt.txt")
    with open(prompt_path, "r") as f:
        return f.read()


model_name = "qwen2.5:1.5b"
