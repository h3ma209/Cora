import json
import ollama
from src.config import DEFAULT_MODEL
from src.api.session import get_session_manager


def update_memory_background(session_id: str):
    """
    Background task to update session memory (Summary & Entities).
    """
    try:
        manager = get_session_manager()
        session = manager.get_session(session_id)
        if not session or not session.messages:
            return

        # 1. Entity Extraction (From last user message)
        last_user_msg = None
        for m in reversed(session.messages):
            if m["role"] == "user":
                last_user_msg = m["content"]
                break

        if last_user_msg:
            extract_entities(session, last_user_msg)

        # 2. Summarization (Every 2 turns)
        msg_count = len(session.messages)
        if msg_count > 0 and msg_count % 2 == 0:
            generate_summary(session)

    except Exception as e:
        print(f"❌ Memory update failed: {e}")


def extract_entities(session, text: str):
    """Extract key details into session.entities"""
    print(f"🧠 [Background] Analyzing entities in: '{text[:30]}...'")

    system_prompt = """Extract specific details from the user text into a flat JSON object.
    Target fields: name, phone_model, location, issue_type, plan_name.
    Return ONLY JSON. No markdown. If info is missing, omit the key."""

    try:
        response = ollama.generate(
            model=DEFAULT_MODEL,
            system=system_prompt,
            prompt=text,
            format="json",
            options={"temperature": 0.1},
            stream=False,
        )

        resp_text = response["response"]
        # Handle markdown blocks if present
        if "```" in resp_text:
            resp_text = resp_text.split("```")[-2]
            if resp_text.startswith("json"):
                resp_text = resp_text[4:]

        data = json.loads(resp_text)
        updates = {
            k: v for k, v in data.items() if v and isinstance(v, (str, int, float))
        }

        if updates:
            session.entities.update(updates)
            print(f"🧠 [Background] Updated Entities: {updates}")

    except Exception as e:
        print(f"⚠️ Entity extraction warning: {e}")


def generate_summary(session):
    """Update session.summary"""
    print("🧠 [Background] Updating conversation summary...")

    recent_msgs = session.messages[-8:]
    conversation_text = ""
    for m in recent_msgs:
        role = "User" if m["role"] == "user" else "Assistant"
        conversation_text += f"{role}: {m['content']}\n"

    current_summary = session.summary or "New conversation."

    prompt = f"""Update the conversation summary. Focus on the user's goal, technical details, and current status.
    Ensure you include specific details that might be needed later.
    OLD SUMMARY: {current_summary}
    RECENT CHAT:
    {conversation_text}
    UPDATED SUMMARY:"""

    try:
        response = ollama.generate(
            model=DEFAULT_MODEL,
            prompt=prompt,
            options={"temperature": 0.2, "num_predict": 250},
            stream=False,
        )

        new_summary = response["response"].strip()
        session.summary = new_summary
        print(f"🧠 [Background] New Summary: {new_summary}")

    except Exception as e:
        print(f"⚠️ Summarization warning: {e}")
