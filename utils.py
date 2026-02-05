
# read the prompt.txt and return the prompt as string

def read_prompt():
    with open("prompt.txt", "r") as f:
        return f.read()

model_name = "qwen2.5:1.5b"

