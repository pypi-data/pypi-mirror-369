# Structured Output Example

Extract structured data from unstructured text using OpenAI's Pydantic integration.

## Features

- **Type-safe extraction** using Pydantic models
- **Explicit routing** with clear outcomes
- **Validation** of extracted data
- **Formatted output** for display

## Setup

```bash
pip install -r requirements.txt
export OPENAI_API_KEY="your-key"
```

## Usage

```bash
python main.py
```

The example will:

1. Load resume text from `data.txt`
2. Extract structured information (name, email, experience, skills)
3. Validate the data meets requirements
4. Display formatted results

## Customization

Edit `data.txt` to test with different resumes. Adjust validation rules in `nodes.py`.

## Flow Structure

```mermaid
graph LR
    Start([Start]) --> E[extractor]
    E -->|extracted| V[validator]
    E -->|failed| C[complete]
    E -->|no_input| C
    V -->|valid| F[formatter]
    V -->|invalid| C
    F -->|formatted| C
    F -->|no_data| C
    C -->|done| End([End/None])
    
    style E fill:#e1f5fe
    style V fill:#fff3e0
    style F fill:#f3e5f5
    style C fill:#e8f5e9
```

ClearFlow enforces single termination - all paths converge to `complete` node.

**Node Outcomes:**

- `extractor`: extracted/failed/no_input
- `validator`: valid/invalid  
- `formatter`: formatted/no_data
- `complete`: done (→ None)
