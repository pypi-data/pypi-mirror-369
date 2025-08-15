# SlotMatch

**SlotMatch** is a lightweight Python package for extracting structured key-value pairs from unstructured or noisy LLM outputs. It supports regex-based parsing, fuzzy key recovery, schema validation, and confidence scoring. Perfect for production RAG, chatbot, and NLU pipelines.

---

## Installation

```bash
pip install slotmatch

## Features

- Regex-based value extraction

- Fuzzy key mapping (e.g., intnt → intent)

- Schema validation for expected keys and types

- Type coercion (str, int, float, bool)

- Confidence scoring (regex = high, fuzzy = partial, fallback = 0)

- Lightweight, no external dependencies

## Usage

from slotmatch import SlotExtractor

schema = {
    "name": str,
    "intent": str,
    "destination": str
}

llm_output = '''
Hi, I'm Alice.
{
  "intnt": "book_flight",
  "dest": "NYC",
  "name": "Alice"
}
'''

extractor = SlotExtractor(schema)
print(extractor.extract(llm_output))

## Output

{
  'name': {'value': 'Alice', 'confidence': 1.0},
  'intent': {'value': 'book_flight', 'confidence': ~0.64},
  'destination': {'value': None, 'confidence': 0.0}
}

## Example Use Cases

- Post-processing LLM outputs (chatbots, assistants, tools)

- Extracting form fields or user intents

- Structuring data for downstream APIs or storage

- Integrating LLMs with business logic (field validation, routing)

## License

This project is licensed under the MIT License.