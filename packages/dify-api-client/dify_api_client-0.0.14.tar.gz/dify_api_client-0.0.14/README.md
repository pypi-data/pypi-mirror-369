# dify-api-client

This package is a fork of [`dify-client-python`](https://github.com/haoyuhu/dify-client-python) with custom modifications

It provides a convenient and powerful interface to interact with the Dify API, supporting both synchronous and asynchronous operations.

## Main Features

* **Synchronous and Asynchronous Support**: The client offers both synchronous and asynchronous methods, allowing for
  flexible integration into various Python codebases and frameworks.
* **Stream and Non-stream Support**: Seamlessly work with both streaming and non-streaming endpoints of the Dify API for
  real-time and batch processing use cases.
* **Comprehensive Endpoint Coverage**: Support completion, chat, workflows, feedback, file uploads, etc., the client
  covers all available Dify API endpoints.


## Quick Start
### Sync 
Here's a quick example of how you can use the `DifyClient` to send a chat message.

```python
import uuid
from dify_client import DifyClient, models

# Initialize the client with your API key
client = DifyClient(
    api_key="your-api-key",
    api_base="http://localhost/v1",
)
user = str(uuid.uuid4())

# Create a blocking chat request
blocking_chat_req = models.ChatRequest(
    query="Hi, dify-client-python!",
    inputs={"city": "Beijing"},
    user=user,
    response_mode=models.ResponseMode.BLOCKING,
)

# Send the chat message
chat_response = client.chat_messages(blocking_chat_req, timeout=60.)
print(chat_response)

# Create a streaming chat request
streaming_chat_req = models.ChatRequest(
    query="Hi, dify-client-python!",
    inputs={"city": "Beijing"},
    user=user,
    response_mode=models.ResponseMode.STREAMING,
)

# Send the chat message
for chunk in client.chat_messages(streaming_chat_req, timeout=60.):
    print(chunk)
```

### Async
For asynchronous operations, use the `AsyncDifyClient` in a similar fashion:

```python
import asyncio
import uuid

from dify_client import AsyncDifyClient, models
# Initialize the async client with your API key
async_client = AsyncDifyClient(
    api_key="your-api-key",
    api_base="http://localhost/v1",
)


# Define an asynchronous function to send a blocking chat message with BLOCKING ResponseMode
async def send_chat_message():
    user = str(uuid.uuid4())
    # Create a blocking chat request
    blocking_chat_req = models.ChatRequest(
        query="Hi, dify-client-python!",
        inputs={"city": "Beijing"},
        user=user,
        response_mode=models.ResponseMode.BLOCKING,
    )
    chat_response = await async_client.achat_messages(blocking_chat_req, timeout=60.)
    print(chat_response)


# Define an asynchronous function to send a chat message with STREAMING ResponseMode
async def send_chat_message_stream():
    user = str(uuid.uuid4())
    # Create a blocking chat request
    streaming_chat_req = models.ChatRequest(
        query="Hi, dify-client-python!",
        inputs={"city": "Beijing"},
        user=user,
        response_mode=models.ResponseMode.STREAMING,
    )
    async for chunk in await async_client.achat_messages(streaming_chat_req, timeout=60.):
        print(chunk)


# Run the asynchronous function
asyncio.gather(send_chat_message(), send_chat_message_stream())
```

## Development
- Setup env
```
uv sync --extra dev
```
- Export python path to run dev
```
export PYTHONPATH=.
```