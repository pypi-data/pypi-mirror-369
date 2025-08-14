# PromptStudio Python SDK

A Python SDK for interacting with PromptStudio API and AI platforms directly.

## Installation

### From PyPI

```bash
pip install promptstudio-sdk
```

### From Source

```bash
git clone https://github.com/your-repo/promptstudio-sdk.git
cd promptstudio-sdk
pip install -e .
```

## Development Setup

1. Create a virtual environment:

```bash
python -m venv venv
```

2. Activate the virtual environment:

```bash
# On Windows
venv\Scripts\activate

# On Unix or MacOS
source venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Usage

### Initializing the SDK

```python
from promptstudio_sdk import PromptStudio

client = PromptStudio({
    'api_key': 'YOUR_API_KEY',
    'env': 'prod',  # Use 'prod' for production environment
    'bypass': True,
    'is_logging': True,
    'timeout': 5000  # Timeout in milliseconds
})
```

### Configuration Options

#### `bypass` (default: `False`)

The `bypass` parameter determines whether to use the local AI provider directly or route requests through PromptStudio's API:

* When `bypass=True`: Requests go directly to the AI provider, bypassing PromptStudio's API
* When `bypass=False`: Requests are routed through PromptStudio's API for additional processing and logging

When `bypass=True`, you can use the role-based message format in `user_message`, such as:

```python
user_message = [
    {"role": "user", "content": [{"type": "text", "text": "Hi"}]},
    {"role": "assistant", "content": [{"type": "text", "text": "Hello! How can I help you?"}]},
    {"role": "user", "content": [{"type": "text", "text": "What is Python?"}]}
]
```

> **Note:** This format is **only supported when `bypass=True`**. If used with `bypass=False`, an error will be raised.

When `bypass=False`, you must use the simpler format:

```python
user_message = [
    {"type": "text", "text": "Hello"}
]
```

#### `is_session_enabled` (default: `True`)

Controls whether conversation history is maintained across requests.

#### `is_logging` (default: `True`)

Determines whether interactions are logged for analytics.

#### `shot` (default: `-1`)

Controls how many message pairs to include from the beginning of the conversation:

* `-1`: All previous messages are included
* `0`: No previous messages are included
* `n > 0`: First `n` pairs (2n messages) are included

#### `timeout` (default: 25)

Sets the maximum time (in milliseconds) to wait for a response. If exceeded, raises a `TimeoutError`.

---

### Using `shot`

```python
# Example: Using shot to include first 2 pairs of messages
response = client.chat_with_prompt(
    prompt_id="your_prompt_id",
    user_message=[{"type": "text", "text": "Hello"}],
    session_id="your_session_id",
    shot=2
)
```
### Memory Control

#### `memory_type` (default: `"fullMemory"`)

Controls how past conversation context is included in each request.

Supported values:

* **`"fullMemory"`**: Maintains the complete conversation history.
* **`"windowMemory"`**: Keeps a sliding window of recent messages,includes only the latest N messages, controlled via `window_size`.
* **`"summarizedMemory"`**:Maintains a summarized version of the conversation history.

#### `window_size` (used with `"windowMemory"`)

When `memory_type` is set to `"windowMemory"`, `window_size` defines how many past messages to include.

Example:

```python
response = client.chat_with_prompt({
    "prompt_id": "abc123",
    "user_message": [{"type": "text", "text": "Tell me a joke"}],
    "session_id": "session_xyz",
    "memory_type": "windowMemory",
    "window_size": 6
})
```
---

### Chatting with a Prompt

```python
response = client.chat_with_prompt(
    prompt_id="your_prompt_id",
    user_message=[
        {
            "type": "text",
            "text": "Hello, how are you?"
        }
    ],
    memory_type="fullMemory",
    window_size=0,
    session_id="your_session_id",
    variables={},
    is_session_enabled=True,
    shot=2,
)

print(response)
```

---

### Tag Field (Optional Metadata)

You can pass a `tag` dictionary to include custom metadata such as user identifiers :

```python
tag = {
    "userId": "680b5b825149777520281b5b",
    "userName":"Roshni",
    "Location":"India"
}
```

* Useful for custom tracking, filtering, or analytics

---

### Complete Example

```python
from promptstudio_sdk import PromptStudio

def main():
    client = PromptStudio({
        'api_key': 'YOUR_API_KEY',
        'env': 'test',
        'bypass': True,
        'is_logging': True,
        'timeout': 500 
    })

    try:

        response = client.chat_with_prompt(
            prompt_id="your_prompt_id",
            user_message=[
                {"type": "text", "text": "Hello, how are you?"}
            ],
            memory_type="windowMemory",
            window_size=10,
            session_id="your_session_id",
            variables={},
            is_session_enabled=True,
            shot=2,
        )
        print("Chat response:", response)

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
```

---

## Session Retrieval

```python
response = await client.get_session(session_id="your_session_id")
```

This returns the complete session state, including historical messages and any metadata.

---

---

## Type Hints

```python
from typing import Dict, List, Union, Optional

ImageMessage = Dict[str, Union[str, Dict[str, str]]]
TextMessage = Dict[str, str]
UserMessage = List[Union[ImageMessage, TextMessage]]

Memory = Literal["fullMemory", "windowMemory", "summarizedMemory"]

RequestPayload = Dict[str, Union[UserMessage, Memory, int, str, Dict[str, str], Optional[int]]]
```

---

## Contributing

1. Fork the repository
2. Create a new branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

This SDK is released under the MIT License.



