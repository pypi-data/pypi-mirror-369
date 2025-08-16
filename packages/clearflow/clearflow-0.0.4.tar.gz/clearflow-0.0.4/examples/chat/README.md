# ClearFlow Chat Example

A simple chat application using OpenAI's API, demonstrating how ClearFlow provides explicit routing for language model conversations.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Set your OpenAI API key
export OPENAI_API_KEY="your-api-key"

# Run
python main.py
```

## Structure

- **`main.py`** - UI handling (input/output)
- **`nodes.py`** - ChatNode with conversation logic
- **`flow.py`** - Single-node flow definition

## Key Pattern

ClearFlow separates concerns cleanly:

```python
# flow.py - Simple single-node flow
flow = (
    Flow[ChatState]("ChatBot")
    .start_with(chat)
    # No routes needed - single node returns outcomes directly
    .build()
)

# nodes.py - Business logic with explicit outcomes
if user_input is None:
    return NodeResult(new_state, outcome="awaiting_input")
# ... process language model call ...
return NodeResult(new_state, outcome="responded")

# main.py - UI handles the conversation loop
while True:
    user_input = get_user_input()
    if user_input is None:
        break
    # Update state with user input and process
    result = await flow(state)
```

The separation ensures that UI logic (looping, input/output) stays in main.py, while business logic (language model calls, state management) stays in the node.
