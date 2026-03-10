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


def test_sim_troubleshooting():
    print(f"{BLUE}🚀 Starting Complex Troubleshooting Memory Test{RESET}")
    print("-" * 50)

    # Turn 1
    print(f"\n{BLUE}[Turn 1] Initial Problem{RESET}")
    data = ask(
        "hello there I currently have a problem with my sim I keep losing signal during calls whats the cause"
    )
    session_id = data.get("session_id")
    time.sleep(1)

    # Turn 2
    print(f"\n{BLUE}[Turn 2] Follow up action{RESET}")
    ask(
        "I tried restarting the phone, but the signal still drops.",
        session_id=session_id,
    )
    time.sleep(1)

    # Turn 3
    print(f"\n{BLUE}[Turn 3] Injecting Entity (Phone Model){RESET}")
    ask("By the way, I'm using an iPhone 13 Pro.", session_id=session_id)
    time.sleep(1)

    # Turn 4
    print(f"\n{BLUE}[Turn 4] Contextual action{RESET}")
    ask(
        "Okay, I checked the network settings like you might have suggested. VoLTE is on.",
        session_id=session_id,
    )
    time.sleep(1)

    # Turn 5
    print(f"\n{BLUE}[Turn 5] Injecting Entity (Location/Environment){RESET}")
    ask(
        "I just noticed it mostly happens when I go down to the basement.",
        session_id=session_id,
    )
    time.sleep(1)

    # Turn 6
    print(f"\n{BLUE}[Turn 6] Memory Test - Phone Model{RESET}")
    data_phone = ask(
        "Wait, what phone did I tell you I'm using?", session_id=session_id
    )
    ans_phone = data_phone.get("answer", "").lower()
    if "iphone" in ans_phone and "13" in ans_phone:
        print(f"{GREEN}✅ PASS: Remembered phone model.{RESET}")
    else:
        print(f"{RED}❌ FAIL: Forgot phone model.{RESET}")
    time.sleep(1)

    # Turn 7
    print(f"\n{BLUE}[Turn 7] Memory Test - Original Issue{RESET}")
    data_issue = ask(
        "Can you remind me what my original problem was?", session_id=session_id
    )
    ans_issue = data_issue.get("answer", "").lower()
    if "signal" in ans_issue and "drop" in ans_issue or "call" in ans_issue:
        print(f"{GREEN}✅ PASS: Remembered original issue.{RESET}")
    else:
        print(f"{RED}❌ FAIL: Forgot original issue.{RESET}")
    time.sleep(1)

    # Turn 8
    print(f"\n{BLUE}[Turn 8] Memory Test - Full Summary{RESET}")
    data_summary = ask(
        "Can you summarize everything we've figured out so far?", session_id=session_id
    )
    ans_summary = data_summary.get("answer", "").lower()

    expected = ["iphone", "basement", "restarted", "volte"]
    found = [k for k in expected if k in ans_summary]

    if len(found) >= 2:
        print(f"{GREEN}✅ PASS: Summary includes key details: {found}{RESET}")
    else:
        print(f"{RED}❌ FAIL: Summary missed key details. Found: {found}{RESET}")


if __name__ == "__main__":
    test_sim_troubleshooting()
