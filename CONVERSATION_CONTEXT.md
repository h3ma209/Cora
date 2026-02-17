# Conversation Context & Session Management

## Overview

Cora now supports **multi-turn conversations** with context retention. This means the AI remembers previous questions and answers within a conversation session, providing more relevant and contextual responses.

## How It Works

### Session Management

- Each conversation is tracked via a unique `session_id`
- Sessions automatically expire after **30 minutes** of inactivity
- Conversation history is stored in memory (last 3-5 turns)
- The AI references previous messages when generating responses

### Context Retention

- The system maintains up to **3 turns** (6 messages: 3 user + 3 assistant) in the prompt
- Previous questions and answers are formatted as conversation history
- The LLM is instructed to acknowledge and reference prior context naturally

## API Usage

### 1. Starting a New Conversation

**First Request** (no session_id):

```bash
curl -X POST http://localhost:9321/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "My SIM card is not working",
    "language": "en"
  }'
```

**Response**:

```json
{
  "answer": "Let's figure out what's going on with your SIM...",
  "sources": [...],
  "confidence": "high",
  "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

### 2. Continuing the Conversation

**Follow-up Request** (with session_id from previous response):

```bash
curl -X POST http://localhost:9321/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "I already tried restarting my phone",
    "language": "en",
    "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
  }'
```

**Response** (acknowledges previous context):

```json
{
  "answer": "Okay, since restarting didn't help, let's try toggling airplane mode...",
  "sources": [...],
  "confidence": "medium",
  "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

### 3. Streaming with Context

**Streaming Request**:

```bash
curl -X POST http://localhost:9321/ask/stream \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What else can I try?",
    "language": "en",
    "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
  }'
```

The streaming response will reference the conversation history naturally.

## Frontend Integration

### JavaScript Example

```javascript
// Store session ID in your app state
let currentSessionId = null;

async function askQuestion(question) {
  const response = await fetch('http://localhost:9321/ask', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      question: question,
      language: 'en',
      session_id: currentSessionId  // null for first message
    })
  });

  const data = await response.json();
  
  // Store session ID for next request
  currentSessionId = data.session_id;
  
  return data;
}

// Example usage
await askQuestion("My SIM is not working");
// Session created, ID stored

await askQuestion("I tried restarting");
// Uses same session, AI remembers context

await askQuestion("What about airplane mode?");
// AI knows you already tried restarting
```

### React Example

```jsx
function ChatInterface() {
  const [sessionId, setSessionId] = useState(null);
  const [messages, setMessages] = useState([]);

  const sendMessage = async (question) => {
    const response = await fetch('http://localhost:9321/ask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        question,
        language: 'en',
        session_id: sessionId
      })
    });

    const data = await response.json();
    
    // Update session ID
    setSessionId(data.session_id);
    
    // Add to messages
    setMessages([
      ...messages,
      { role: 'user', content: question },
      { role: 'assistant', content: data.answer }
    ]);
  };

  const resetConversation = () => {
    setSessionId(null);
    setMessages([]);
  };

  return (
    <div>
      <ChatMessages messages={messages} />
      <ChatInput onSend={sendMessage} />
      <button onClick={resetConversation}>New Conversation</button>
    </div>
  );
}
```

## Session Lifecycle

### Automatic Cleanup

- Sessions expire after **30 minutes** of inactivity
- Expired sessions are automatically removed from memory
- Starting a new conversation after expiry creates a fresh session

### Manual Reset

To start a fresh conversation, simply:

1. Don't send a `session_id` in the request, OR
2. Send a different/new `session_id`

## Best Practices

### 1. **Always Store the session_id**

```javascript
// ✅ Good
const response = await askQuestion(userInput);
sessionId = response.session_id;

// ❌ Bad - loses context
await askQuestion(userInput);
// session_id not stored
```

### 2. **Reset on Topic Change**

```javascript
// User changes topic completely
if (userChangedTopic) {
  sessionId = null;  // Start fresh conversation
}
```

### 3. **Handle Session Expiry**

```javascript
// If session expired (30+ min), backend creates new one
// Your app should handle this gracefully
const response = await askQuestion(question);
if (response.session_id !== currentSessionId) {
  console.log('New session started');
  currentSessionId = response.session_id;
}
```

### 4. **Multilingual Conversations**

```javascript
// Language can change mid-conversation
await askQuestion("My SIM doesn't work", "en");
await askQuestion("لقد جربت إعادة التشغيل", "ar");
// Context maintained across languages
```

## Implementation Details

### Context Window

- **Max turns in prompt**: 3 (last 3 user-assistant pairs)
- **Total messages stored**: Unlimited (until session expires)
- **Context format**:

  ```
  CONVERSATION HISTORY:
  Customer: My SIM is not working
  You: Let's figure out what's going on...
  Customer: I already tried restarting
  You: Okay, since restarting didn't help...
  
  Current question: What else can I try?
  ```

### Memory Management

- Sessions stored in-memory (not persistent across restarts)
- Automatic cleanup of expired sessions
- No database required

### Prompt Engineering

The system prompt includes:

- Instruction to reference conversation history naturally
- Acknowledgment of what user has already tried
- Contextual follow-up suggestions

## Testing

### Test Multi-Turn Conversation

```bash
# First message
curl -X POST http://localhost:9321/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "My phone has no signal", "language": "en"}' \
  | jq -r '.session_id' > session.txt

# Follow-up (using stored session ID)
SESSION_ID=$(cat session.txt)
curl -X POST http://localhost:9321/ask \
  -H "Content-Type: application/json" \
  -d "{\"question\": \"I tried restarting already\", \"language\": \"en\", \"session_id\": \"$SESSION_ID\"}"
```

### Test Session Expiry

```bash
# Wait 31 minutes, then try to use old session_id
# Backend will create new session automatically
```

## Monitoring

### Check Active Sessions

```python
from src.api.session import get_session_manager

manager = get_session_manager()
print(f"Active sessions: {manager.get_active_sessions_count()}")
```

### View Session History

```python
session = manager.get_session(session_id)
history = session.get_history(max_turns=10)
for msg in history:
    print(f"{msg['role']}: {msg['content']}")
```

## Troubleshooting

### Issue: Context not maintained

**Solution**: Ensure you're sending the `session_id` from previous response

### Issue: Session expired

**Solution**: Sessions expire after 30 min. Start new conversation.

### Issue: Irrelevant responses

**Solution**: Check that conversation history is relevant. Reset session if topic changed.

## Future Enhancements

Potential improvements:

- [ ] Persistent sessions (database storage)
- [ ] Configurable session timeout
- [ ] Session export/import
- [ ] Multi-user session management
- [ ] Session analytics and insights
