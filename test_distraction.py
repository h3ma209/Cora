import requests
import time
import sys

# Configuration
API_URL = "http://localhost:8001"
RED = "\033[91m"
GREEN = "\033[92m"
BLUE = "\033[94m"
RESET = "\033[0m"


def ask(question, session_id=None):
    url = f"{API_URL}/ask"
    payload = {"question": question, "language": "en"}
    if session_id:
        payload["session_id"] = session_id

    try:
        response = requests.post(url, json=payload)
        data = response.json()
        answer = data.get("answer", "")
        sid = data.get("session_id")

        print(f"User: {question}")
        print(f"{GREEN}AI:   {answer}{RESET}")

        return data

    except Exception as e:
        print(f"{RED}❌ Connection error: {e}{RESET}")
        return None


def test_distraction():
    print(f"{BLUE}🚀 Starting Distraction Memory Test{RESET}")
    print("-" * 50)

    # 1. Establish Facts
    print(f"\n{BLUE}[Phase 1] Establishing Facts{RESET}")
    data1 = ask("Hi, my name is Rayied and I'm having trouble with my eSIM activation.")
    session_id = data1.get("session_id")
    time.sleep(1)

    # 2. Distraction Phase (3 turns)
    print(f"\n{BLUE}[Phase 2] Distraction (3 turns){RESET}")
    distractions = [
        "What is the capital of France?",
        "Tell me a joke.",
        "How many planets are in the solar system?",
    ]

    for q in distractions:
        ask(q, session_id=session_id)
        time.sleep(1)

    # 3. Recall Phase
    print(f"\n{BLUE}[Phase 3] Testing Recall{RESET}")
    data_final = ask(
        "What was my name and what problem did I have?", session_id=session_id
    )
    answer = data_final.get("answer", "").lower()

    # Verification
    has_name = "rayied" in answer
    has_problem = "esim" in answer or "activation" in answer

    print("-" * 50)
    if has_name and has_problem:
        print(f"{GREEN}✅ PASS: Remembered name and problem after distractions.{RESET}")
    elif has_name:
        print(f"{RED}❌ FAIL: Remembered name but forgot problem.{RESET}")
    elif has_problem:
        print(f"{RED}❌ FAIL: Remembered problem but forgot name.{RESET}")
    else:
        print(f"{RED}❌ FAIL: Forgot everything.{RESET}")


if __name__ == "__main__":
    test_distraction()
