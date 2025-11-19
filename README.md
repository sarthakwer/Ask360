# Ask360 - FreshFoods Yogurt Insights POC

A minimal proof-of-concept that answers natural-language questions about FreshFoods yogurt using a mocked Insights360 dataset.

## Features

- Natural-language question routing to specific intents
- In-memory synthetic data generation (2023-2024 sales, segments, occasions)
- Multiple interfaces: CLI, FastAPI, and Streamlit chat UI
- Structured JSON responses with optional KPIs, tables, and charts

## Setup

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

### CLI Mode

Run with a question as argument:
```bash
python -m ask360.cli "How is yogurt doing? Show last 12 months"
```

Or run in interactive mode:
```bash
python -m ask360.cli
```

### API Mode

Start the FastAPI server:
```bash
uvicorn ask360.api:app --reload --port 8000
```

Then make POST requests:
```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "Which were the top 3 growth markets for yogurt last year?"}'
```

### Streamlit UI

Launch the chat interface:
```bash
streamlit run ask360/streamlit_app.py
```

The UI provides:
- Chat interface with question/answer history
- KPI metrics display
- Tabs for charts, tables, and raw JSON
- Example question buttons
- Optional AI insight toggle (placeholder)

## Example Questions

1. "How is yogurt doing at FreshFoods? Show the last 12 months trend."
2. "Which were the top 3 growth markets for yogurt last year?"
3. "Among 18–34 vs 35–54, who has higher repeat rate for yogurt?"
4. "What are the top consumption occasions for shelf-stable yogurt?"
5. "In e-commerce vs retail, which channel grew faster for multipack yogurt?"

## Architecture

The codebase follows a clear separation between core logic and UI:

- **`ask360/ask360_core.py`**: Core business logic
  - Intent routing (regex-based)
  - Synthetic data generation
  - Handler functions for each intent
  - Chart generation (matplotlib)

- **`ask360/cli.py`**: Command-line interface wrapper

- **`ask360/api.py`**: FastAPI REST endpoint wrapper

- **`ask360/streamlit_app.py`**: Streamlit chat UI wrapper

All interfaces call the same `answer(question: str)` function from `ask360_core.py`, ensuring consistent behavior across all modes.

## Testing

Run tests:
```bash
pytest tests/
```

## Project Structure

```
ask360/
  __init__.py
  ask360_core.py    # Core logic (routing + handlers + synthetic data)
  api.py            # FastAPI wrapper
  cli.py            # CLI entry point
  streamlit_app.py  # Streamlit chat UI
tests/
  test_intents.py   # Intent routing tests
requirements.txt
README.md
```

## Notes

- All data is generated synthetically in-memory (no external databases)
- Charts are saved as PNG files (e.g., `trend.png`)
- No external APIs or LLM calls (per requirements)
- Code is kept minimal and readable (< 350 LOC total)

