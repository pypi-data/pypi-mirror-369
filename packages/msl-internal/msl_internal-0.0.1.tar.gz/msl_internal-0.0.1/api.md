# Chat

Types:

```python
from msl_internal.types import (
    CompletionMessage,
    CreateChatCompletionResponse,
    CreateChatCompletionResponseStreamChunk,
    MessageImageContentItem,
    MessageTextContentItem,
    SystemMessage,
    ToolResponseMessage,
    UserMessage,
)
```

## Completions

Types:

```python
from msl_internal.types.chat import CompletionCreateResponse
```

Methods:

- <code title="post /chat/completions">client.chat.completions.<a href="./src/msl_internal/resources/chat/completions.py">create</a>(\*\*<a href="src/msl_internal/types/chat/completion_create_params.py">params</a>) -> <a href="./src/msl_internal/types/chat/completion_create_response.py">CompletionCreateResponse</a></code>
