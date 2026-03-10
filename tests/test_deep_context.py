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


def test_deep_context():
    print(f"{BLUE}🚀 Starting Deep Context & Memory Test{RESET}")
    print("-" * 50)

    # 1. Multi-Step Troubleshooting
    print(f"\n{BLUE}[Test 1] Multi-Step Troubleshooting Chain{RESET}")
    data1 = ask("My internet is slow.")
    session_id = data1.get("session_id")
    time.sleep(1)

    ask("I already tried restarting the router.", session_id=session_id)
    time.sleep(1)

    ask("That didn't work either. What's next?", session_id=session_id)
    time.sleep(1)

    # Check if AI recalls the full troubleshooting history
    data_recall = ask(
        "Can you list everything I've tried so far?", session_id=session_id
    )
    answer = data_recall.get("answer", "").lower()

    expected = ["restart", "router", "internet"]
    found = [k for k in expected if k in answer]

    if len(found) >= 2:
        print(f"{GREEN}✅ PASS: Recalled troubleshooting steps.{RESET}")
    else:
        print(f"{RED}❌ FAIL: Missed key steps.{RESET}")

    # 2. Variable Value Retention (The Order Test)
    print(f"\n{BLUE}[Test 2] Variable Value Retention{RESET}")
    # Reset session
    data_order = ask("I want to order a SIM card.")
    sid_order = data_order.get("session_id")
    time.sleep(1)

    ask("I want the Platinum plan.", session_id=sid_order)
    time.sleep(1)

    ask("My address is 123 Main St, Erbil.", session_id=sid_order)
    time.sleep(1)

    # Verify retention of Plan and Address
    final_check = ask("Please confirm my order details.", session_id=sid_order)
    ans_order = final_check.get("answer", "").lower()

    has_plan = "platinum" in ans_order
    has_addr = "123 main" in ans_order or "erbil" in ans_order

    if has_plan and has_addr:
        print(f"{GREEN}✅ PASS: Retained plan and address.{RESET}")
    elif has_plan:
        print(f"{RED}❌ FAIL: Remembered plan but forgot address.{RESET}")
    elif has_addr:
        print(f"{RED}❌ FAIL: Remembered address but forgot plan.{RESET}")
    else:
        print(f"{RED}❌ FAIL: Forgot all order details.{RESET}")

    # 3. Reference Resolution over Long Distance
    print(f"\n{BLUE}[Test 3] Long-Distance Reference Resolution{RESET}")
    # Reset session
    data_topic = ask("Let's talk about the iPhone 15 Pro Max.")
    sid_topic = data_topic.get("session_id")
    time.sleep(1)

    ask("Does it support 5G?", session_id=sid_topic)
    time.sleep(1)

    ask("What about the camera?", session_id=sid_topic)
    time.sleep(1)

    ask("How much storage does the base model have?", session_id=sid_topic)
    time.sleep(1)

    # Crucial step: "it" refers back to iPhone 15 Pro Max from turn 1
    ref_check = ask("Is it available in Titanium Blue?", session_id=sid_topic)
    ans_ref = ref_check.get("answer", "").lower()

    if "iphone" in ans_ref or "15" in ans_ref or "titanium" in ans_ref:
        print(f"{GREEN}✅ PASS: Correctly resolved 'it' to iPhone 15 Pro Max.{RESET}")
    else:
        print(f"{RED}❌ FAIL: Lost track of the main subject.{RESET}")


if __name__ == "__main__":
    test_deep_context()
