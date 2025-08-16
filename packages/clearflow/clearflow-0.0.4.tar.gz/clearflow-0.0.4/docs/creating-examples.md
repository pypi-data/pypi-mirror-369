# Creating Examples

## Structure

```text
examples/
└── your-example/
    ├── main.py           # Entry point
    ├── nodes.py          # Node implementations
    ├── flow.py           # Flow construction
    ├── requirements.txt  # Dependencies
    └── README.md         # Documentation
```

## Quality Checks

Examples must pass:

```bash
./check-examples.sh
```

This runs:

- Linting (ruff)
- Type checking (mypy, pyright)
- Formatting

## Key Patterns

### State Management

```python
# Immutable transformations only
new_state = state.transform(lambda d: {**d, "processed": True})
```

### Flow Construction

```python
Flow[State]("Example")
    .start_with(node1)
    .route(node1, "success", None)  # Single termination
    .build()
```

### Separation of Concerns

- `main.py`: User interaction, I/O
- `nodes.py`: Business logic
- `flow.py`: Orchestration

## Checklist

- [ ] Passes `./check-examples.sh`
- [ ] Minimal dependencies
- [ ] Clear README with quick start
- [ ] Demonstrates one concept well

See [chat example](../examples/chat/) for reference.
