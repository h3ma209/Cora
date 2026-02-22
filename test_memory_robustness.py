#!/usr/bin/env python3
"""
Robustness Test for Conversation Memory (Session Management)
"""

import requests
import json
import time
import sys

# Configuration
API_URL = "http://localhost:8001"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


def print_step(step_num, title):
    print(f"\n{BLUE}STEP {step_num}: {title}{RESET}")
    print("-" * 50)


def ask(question, session_id=None, expect_context=False):
    url = f"{API_URL}/ask"
    payload = {"question": question, "language": "en"}
    if session_id:
        payload["session_id"] = session_id

    try:
        start_time = time.time()
        response = requests.post(url, json=payload)
        elapsed = time.time() - start_time

        if response.status_code != 200:
            print(f"{RED}❌ Request failed: {response.status_code}{RESET}")
            print(response.text)
            return None

        data = response.json()
        answer = data.get("answer", "")
        sid = data.get("session_id")

        print(f"User: {question}")
        print(f"{GREEN}AI:   {answer}{RESET}")
        print(f"      (Session: {sid}, Time: {elapsed:.2f}s)")

        return data

    except Exception as e:
        print(f"{RED}❌ Connection error: {e}{RESET}")
        return None


def test_memory():
    print(f"🚀 Starting Memory Robustness Test on {API_URL}")

    # 1. Identity Memory
    print_step(1, "Identity Retention")
    # Turn 1: State name
    data1 = ask("Hi, my name is Alex.")
    if not data1:
        return
    session_id = data1.get("session_id")

    # Turn 2: Recall name
    time.sleep(1)
    data2 = ask("What is my name?", session_id=session_id)
    answer2 = data2.get("answer", "").lower()

    if "alex" in answer2:
        print(f"{GREEN}✅ PASS: Remembered name.{RESET}")
    else:
        print(f"{RED}❌ FAIL: Did not recall name.{RESET}")

    # 2. Contextual Reference (The "It" Test)
    print_step(2, "Contextual Reference (The 'It' Test)")
    # Turn 3: Statement implies topic
    time.sleep(1)
    ask("I'm having trouble with my eSIM activation.", session_id=session_id)

    # Turn 4: Ambiguous follow-up
    time.sleep(1)
    data4 = ask("Is it supported on iPhone 14?", session_id=session_id)
    answer4 = data4.get("answer", "").lower()

    # Check if answer mentions eSIM or relevant context
    if "esim" in answer4 or "support" in answer4:
        print(f"{GREEN}✅ PASS: Understood 'it' referred to eSIM.{RESET}")
    else:
        print(f"{YELLOW}⚠️  WARNING: Might have lost context.{RESET}")

    # 3. List Recall
    print_step(3, "Conversation Summary Recall")
    time.sleep(1)
    data5 = ask("Summarize what we have discussed so far.", session_id=session_id)
    answer5 = data5.get("answer", "").lower()

    expected_keywords = ["alex", "esim", "iphone"]
    found = [k for k in expected_keywords if k in answer5]

    if len(found) >= 2:
        print(f"{GREEN}✅ PASS: Summary includes key topics: {found}{RESET}")
    else:
        print(f"{RED}❌ FAIL: Summary missed key topics. Found: {found}{RESET}")

    # 4. Negative Constraint
    print_step(4, "Negative Constraint Memory")
    time.sleep(1)
    ask("I do not have an Android phone.", session_id=session_id)

    time.sleep(1)
    data7 = ask("Do I have a Samsung?", session_id=session_id)
    answer7 = data7.get("answer", "").lower()

    if (
        "no" in answer7 or "don't" in answer7 or "iphone" in answer7
    ):  # Assuming prior context
        print(f"{GREEN}✅ PASS: Correctly inferred negative.{RESET}")
    else:
        print(f"{YELLOW}⚠️  WARNING: inference might be weak.{RESET}")


if __name__ == "__main__":
    test_memory()
