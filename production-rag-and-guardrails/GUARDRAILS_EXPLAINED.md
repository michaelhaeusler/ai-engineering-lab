# Guardrails Implementation - Beginner's Guide

## What are Guardrails?

Think of guardrails like security guards at a building entrance. They check:
- **Input Guardrails**: What people say BEFORE it reaches your AI agent (like checking IDs at the door)
- **Output Guardrails**: What your AI agent says BEFORE it reaches the user (like checking bags on the way out)

This protects your application from malicious users and prevents your AI from saying inappropriate things.

---

## Architecture Overview: The Two-File System

The implementation is split into two files:

1. **`guardrails.py`**: Contains the "security guard" functions (validation logic)
2. **`agents.py`**: Contains the agent that uses these security guards (integration into the workflow)

---

## Part 1: guardrails.py - The Security Guards

### 1.1 Creating Guards (`create_guardrails_guard` function)

**Location**: Lines 39-120 in `guardrails.py`

```python
def create_guardrails_guard(
    valid_topics: Optional[List[str]] = None,
    invalid_topics: Optional[List[str]] = None,
    enable_jailbreak_detection: bool = True,
    # ... more options
) -> Guard:
```

**What it does**: This function builds a "guard" - a collection of security checks.

**Think of it like this**: You're building a checklist for your security guard. You tell them:
- "Only allow conversations about these topics" (`valid_topics`)
- "Block any conversations about these topics" (`invalid_topics`)
- "Watch out for people trying to trick you" (`enable_jailbreak_detection`)
- "Check for personal information like credit cards" (`enable_pii_protection`)

**How it works**:
```python
guard = Guard()  # Start with an empty guard

# Add topic checking
if valid_topics or invalid_topics:
    guard = guard.use(RestrictToTopic(...))

# Add jailbreak detection
if enable_jailbreak_detection:
    guard = guard.use(DetectJailbreak())
```

Each `.use()` call adds another "check" to the guard. It's like adding more items to your security checklist.

---

### 1.2 Two Types of Guards

The code creates TWO separate guards for input:

#### A) PII Guard (lines 459-464)

```python
pii_guard = Guard().use(
    GuardrailsPII(
        entities=["CREDIT_CARD", "SSN", "PHONE_NUMBER", "EMAIL_ADDRESS"],
        on_fail="fix"  # Redact instead of failing
    )
)
```

- **Purpose**: Find and hide sensitive information like credit card numbers
- **Action**: When it finds a credit card number like "4532-1234-5678-9012", it replaces it with `<CREDIT_CARD>`
- **Important**: `on_fail="fix"` means "don't reject the message, just clean it up"

#### B) Content Guard (lines 467-473)

```python
content_guard = create_guardrails_guard(
    valid_topics=valid_topics,
    invalid_topics=invalid_topics,
    enable_jailbreak_detection=True,
    enable_profanity_check=True
)
```

- **Purpose**: Check if the message is appropriate
- **Action**: Reject messages that are off-topic, contain profanity, or are jailbreak attempts
- **Important**: `on_fail="exception"` (default) means "reject the message completely"

---

### 1.3 Input Validation Node (`create_input_validation_node`)

**Location**: Lines 261-357 in `guardrails.py`

This creates a function that acts as a "checkpoint" in your agent's workflow.

#### Two-Stage Process:

```python
# Stage 1: PII Redaction (optional, never fails)
if pii_guard:
    pii_result = validate_input(pii_guard, content, raise_on_failure=False)
    redacted_content = pii_result.get("validated_output", content)
    if redacted_content != content:
        pii_redacted = True
        content = redacted_content

# Stage 2: Content validation
content_result = validate_input(content_guard, content, raise_on_failure=False)
```

#### Why two stages?

1. **First**, we clean the message (remove PII)
2. **Then**, we check if the cleaned message is appropriate

#### Example:
- User says: "My SSN is 123-45-6789. Tell me about politics"
- After Stage 1: "My SSN is `<SSN>`. Tell me about politics"
- Stage 2 checks: "Is this about valid topics?" → NO (politics is invalid) → REJECT

#### Returns:
```python
{
    "input_validation_passed": True/False,
    "validation_error": "error message" or None,
    "messages": [updated message with PII redacted]
}
```

---

### 1.4 Output Validation Node (`create_output_validation_node`)

**Location**: Lines 360-442 in `guardrails.py`

This checks what the AI agent is about to say to the user.

```python
def output_validation_node(state: Dict[str, Any]) -> Dict[str, Any]:
    last_message = state.get("messages", [])[-1]

    # Only validate AI responses
    if not isinstance(last_message, AIMessage):
        return {"output_validation_passed": True}

    result = validate_output(output_guard, last_message.content)

    if result["validation_passed"]:
        return {"output_validation_passed": True}
    else:
        # Replace AI message with error message
        error_response = AIMessage(
            content="I apologize, but I cannot provide that response..."
        )
        return {"messages": [error_response]}
```

**What it does**:
- Checks the AI's response for PII, profanity, or inappropriate content
- If bad: Replaces the response with an apology message
- If good: Lets it through

---

## Part 2: agents.py - Integrating Guards into Agent

### 2.1 Agent State (Lines 35-41)

```python
class GuardrailsAgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    input_validation_passed: bool
    output_validation_passed: bool
    validation_error: Optional[str]
```

**What is this?**

Think of "state" as a notebook that gets passed around. Each step in your agent can:
- Read what's in the notebook
- Write new information to it
- Pass it to the next step

This state includes:
- `messages`: The conversation history
- `input_validation_passed`: Did the user's message pass security?
- `validation_error`: If not, why?

---

### 2.2 Building the Agent with Guards (`create_langgraph_agent`)

**Location**: Lines 83-190 in `agents.py`

This is where the magic happens! Let me break down the workflow:

#### Step 1: Set up validation nodes (lines 151-162)

```python
if with_input_guardrails:
    from .guardrails import create_input_validation_node, create_default_input_guards
    pii_guard, content_guard = create_default_input_guards(valid_topics, invalid_topics)
    input_validation_node = create_input_validation_node(content_guard, pii_guard)
    graph.add_node("validate_input", input_validation_node)
    graph.add_node("input_error", create_input_error_message)
```

**Translation**:
- Import the guard creators we made earlier
- Create the two guards (PII and content)
- Create a validation node using those guards
- Add the node to our workflow graph

#### Step 2: Add core agent nodes (lines 165-166)

```python
graph.add_node("agent", call_model)  # The AI model
graph.add_node("action", tool_node)  # Tools (search, RAG, etc.)
```

#### Step 3: Set up the workflow routing (lines 169-189)

This is like drawing a flowchart. Here's what it looks like:

**WITH Input Guardrails**:
```
START
  ↓
validate_input (check user message)
  ↓
[Did it pass?]
  ├─ YES → agent (run AI model)
  └─ NO → input_error (send error message) → END
        ↓
     [Does agent need tools?]
        ├─ YES → action (use tools) → back to agent
        └─ NO → [Output guardrails?]
                  ├─ YES → validate_output → END
                  └─ NO → END
```

**WITHOUT Guardrails** (simple):
```
START → agent → [tools?] → action → agent → END
```

---

### 2.3 Routing Functions (Decision Points)

#### Input Routing (lines 134-139)

```python
def route_after_input_validation(state: Dict[str, Any]):
    if state.get("input_validation_passed", False):
        return "agent"  # Go to AI model
    else:
        return "input_error"  # Show error message
```

This checks the notebook (state) to see if validation passed, then decides where to go next.

#### Output Routing (lines 124-132)

```python
def should_continue(state: Dict[str, Any]):
    last_message = state["messages"][-1]
    if getattr(last_message, "tool_calls", None):
        return "action"  # Agent wants to use a tool
    if with_output_guardrails:
        return "validate_output"  # Check output first
    return END  # We're done!
```

This decides what happens after the agent generates a response.

---

## Key Concepts for Beginners

### 1. Conditional Edges vs Regular Edges

**Regular edge** (always goes to the same place):
```python
graph.add_edge("action", "agent")  # After using tools, ALWAYS go back to agent
```

**Conditional edge** (decision point):
```python
graph.add_conditional_edges(
    "validate_input",  # From this node
    route_after_input_validation,  # Use this function to decide
    {"agent": "agent", "input_error": "input_error"}  # Possible destinations
)
```

### 2. Why Separate PII and Content Guards?

**PII Guard**:
- Mode: "fix" (clean up the message)
- Never rejects - always processes

**Content Guard**:
- Mode: "exception" (reject if bad)
- Can block messages completely

**Reason**: You want to ALWAYS clean PII, but only SOMETIMES reject messages (when they're actually bad).

### 3. State Management Pattern

```python
def my_node(state: Dict[str, Any]) -> Dict[str, Any]:
    # Read from state
    messages = state["messages"]

    # Do something
    result = process(messages)

    # Return updates to state
    return {"new_field": result}
```

Each node:
1. Receives the current state
2. Does some work
3. Returns ONLY the fields it wants to update
4. LangGraph merges the updates automatically

---

## Complete Flow Example

### User sends message
```
"My SSN is 123-45-6789, tell me about student loans"
```

### Input Validation (if enabled)
1. **PII Guard**: "My SSN is `<SSN>`, tell me about student loans"
2. **Content Guard**: "Is this about valid topics?" → YES → PASS

### Agent processes
- Calls OpenAI model with cleaned message

### Agent might use tools
- Search, RAG, etc.

### Output Validation (if enabled)
- Check response for PII, profanity
- If bad → Replace with apology
- If good → Let it through

### Return to user
- Final (validated) response

---

## Benefits of This Modular Design

You can:
- ✅ Turn guardrails on/off easily
- ✅ Add new types of validation
- ✅ Test each component separately
- ✅ Configure different guards for different use cases

---

## Code Reference Map

### guardrails.py
- **Lines 39-120**: `create_guardrails_guard()` - Main guard factory
- **Lines 122-153**: `create_factuality_guard()` - RAG factuality checking
- **Lines 156-204**: `validate_input()` - Input validation helper
- **Lines 207-258**: `validate_output()` - Output validation helper
- **Lines 261-357**: `create_input_validation_node()` - LangGraph input node
- **Lines 360-442**: `create_output_validation_node()` - LangGraph output node
- **Lines 445-475**: `create_default_input_guards()` - Default input setup
- **Lines 478-502**: `create_default_output_guard()` - Default output setup

### agents.py
- **Lines 35-41**: `GuardrailsAgentState` - State schema with validation
- **Lines 83-190**: `create_langgraph_agent()` - Main agent factory with guards
- **Lines 134-139**: `route_after_input_validation()` - Input routing logic
- **Lines 124-132**: `should_continue()` - Output routing logic
- **Lines 151-162**: Guard setup and node creation
- **Lines 169-189**: Graph routing and edge configuration

---

## Usage Examples

### Simple Agent (No Guardrails)

```python
from langgraph_agent_lib import create_langgraph_agent

agent = create_langgraph_agent(
    model_name="gpt-4o-mini",
    temperature=0.1,
    with_input_guardrails=False,
    with_output_guardrails=False
)
```

### Agent with Input Guardrails Only

```python
agent = create_langgraph_agent(
    model_name="gpt-4o-mini",
    temperature=0.1,
    with_input_guardrails=True,
    valid_topics=["student loans", "education financing"],
    invalid_topics=["politics", "cryptocurrency"]
)
```

### Agent with Both Input and Output Guardrails

```python
agent = create_langgraph_agent(
    model_name="gpt-4o-mini",
    temperature=0.1,
    with_input_guardrails=True,
    with_output_guardrails=True,
    valid_topics=["student loans", "education financing"],
    invalid_topics=["politics", "cryptocurrency"]
)
```

---

## Testing Your Understanding

Try to answer these questions:

1. **Why do we use two separate guards for input validation?**
   - Answer: PII guard (redacts) vs Content guard (rejects)

2. **What's the difference between `on_fail="fix"` and `on_fail="exception"`?**
   - Answer: "fix" modifies the input, "exception" rejects it

3. **What does a routing function return?**
   - Answer: The name of the next node to visit

4. **When does output validation happen?**
   - Answer: After the agent generates a response but before returning to user

5. **What is the "state" in LangGraph?**
   - Answer: A dictionary that gets passed between nodes, tracking conversation and validation status

---

## Next Steps

To extend this implementation, you could:

1. **Add custom validators**: Create your own guard types
2. **Add logging**: Track which messages fail and why
3. **Add metrics**: Measure validation latency and pass/fail rates
4. **Add caching**: Cache validation results for repeated queries
5. **Add refinement**: Auto-refine responses that fail output validation

---

## Common Troubleshooting

### "Validation is too slow"
- Use faster models for evaluation (gpt-4o-mini instead of gpt-4)
- Cache validation results
- Run validations in parallel where possible

### "Too many false positives"
- Adjust thresholds (e.g., profanity threshold)
- Tune topic lists to be more permissive
- Use `on_fail="fix"` instead of `on_fail="exception"`

### "PII not being redacted"
- Check entity types match your use case
- Verify PII guard is created with correct entities
- Enable logging to see what's detected

---

*Created: 2025-11-05*
*For: AI Makerspace Bootcamp - Session 16: Production RAG and Guardrails*
