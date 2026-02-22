import requests
import time

API_URL = "http://localhost:8001"
GREEN = "\033[92m"
BLUE = "\033[94m"
RESET = "\033[0m"


def ask(question, session_id=None):
    url = f"{API_URL}/ask"
    payload = {"question": question, "language": "en"}
    if session_id:
        payload["session_id"] = session_id
    response = requests.post(url, json=payload)
    data = response.json()
    print(f"User: {question}")
    print(f"{GREEN}AI:   {data.get('answer', '')}{RESET}\n")
    return data


def test_greeting():
    print(f"{BLUE}🚀 Testing Natural Conversational Prompt{RESET}")
    print("-" * 50)
    data = ask("hello how are you, how you have been lately")
    time.sleep(1)
    ask(
        "i am having some signal issues in the basement. can you help me?",
        session_id=data.get("session_id"),
    )


def test_out_of_scope():
    print(f"{BLUE}🚀 Testing Out-of-Scope Resiliency{RESET}")
    print("-" * 50)
    ask("can you provide me a link to download the hakki app?")


if __name__ == "__main__":
    test_out_of_scope()
