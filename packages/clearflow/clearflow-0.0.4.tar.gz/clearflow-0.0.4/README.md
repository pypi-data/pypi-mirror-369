# ClearFlow

[![codecov](https://codecov.io/gh/consent-ai/ClearFlow/graph/badge.svg?token=29YHLHUXN3)](https://codecov.io/gh/consent-ai/ClearFlow)
[![PyPI](https://badge.fury.io/py/clearflow.svg)](https://pypi.org/project/clearflow/)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)

Reliable language model orchestration. Type-safe with 100% test coverage.

## Quick Example

```python
from clearflow import Flow, Node, NodeResult

class ChatNode(Node[dict]):
    async def exec(self, state: dict) -> NodeResult[dict]:
        messages = state.get("messages", [])
        # Call your language model here:
        # response = await openai_client.chat.completions.create(messages=messages)
        # content = response.choices[0].message.content
        content = "Hello!"  # Placeholder response
        new_messages = [*messages, {"role": "assistant", "content": content}]
        return NodeResult({**state, "messages": new_messages}, outcome="success")

# Build flow with explicit routing
chat = ChatNode()
flow = (
    Flow[dict]("ChatBot")
    .start_with(chat)
    .route(chat, "success", None)  # Single termination
    .build()
)

result = await flow({"messages": []})
```

## Installation

```bash
pip install clearflow
```

## Why ClearFlow?

- **<200 lines** - Read the entire source in 5 minutes
- **Zero dependencies** - No bloat, no conflicts  
- **100% tested** - Every line covered, no surprises
- **Type-safe** - Catch errors at compile time, not production
- **Composable** - Build complex agents from simple pieces

## Examples

- [Chat](examples/chat/) - Language model conversation with state management
- [Structured Output](examples/structured_output/) - Extract typed data from text

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md)

## Acknowledgments

Inspired by [PocketFlow](https://github.com/The-Pocket/PocketFlow)'s Node-Flow-State pattern.

## License

MIT
