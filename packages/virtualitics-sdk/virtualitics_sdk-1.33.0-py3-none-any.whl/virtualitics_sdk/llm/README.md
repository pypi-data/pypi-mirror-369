# Implementing a Custom DispatcherAgent

The `DispatcherAgentInterface` provides a structured way to control the entire lifecycle of a chat interaction within IRIS Chat Interface. 


## Core Concepts

The `DispatcherAgentInterface` is an Abstract Base Class (ABC) that defines the contract for all dispatcher agents. Its primary purpose is to handle:

1. **Entry Point**: It provides an entrypoint for how IRIS will call your agent's run method and provide some general context
2. **LLM Interaction**: Creates an AsyncLLMClient for your agents to interact with
3. **Communication**: Provides standardized functions for interacting with the user

## The DispatcherAgentInterface

To create a custom agent, you'll subclass `DispatcherAgentInterface` and implement its abstract methods.

### Abstract Method: `run()`

This is the main entry point for your agent's logic. You must implement this method.

```python
from virtualitics_sdk.llm.agent import DispatcherAgentInterface, RawChatContext

class MyCustomAgent(DispatcherAgentInterface):
    @abstractmethod
    async def run(self, chat_context: RawChatContext):
        """
        The main entry point for the agent's execution logic.
        """
        raise NotImplementedError
```

The `chat_context` object gives you access to everything you need for the interaction, including:

- `chat_context.user_id`: The user_id of the user who initiated the chat.
- `chat_context.app_id`: The app_id of the Virtualitics App that initiated the IRIS chat window.
- `chat_context.chat_id`: A unique id to refer to the chat, equivalent to flow_id
- `chat_context.step_name`: The name of the Step ("page") the user is currently viewing
- `chat_context.element_id`: The specific element_id the user is viewing (e.g dashboard tab)
- `chat_context.prompt`: The user's message.
- `chat_context.llm_host`: The ollama/vllm host specified by the platform.
- `chat_context.model`: The selected model for the chat.
- `chat_context.response`: [Optional] The response from the LLM (useful for having a consistent input format for pre/post-processing)
- `chat_context.llm_client`: The `AsyncLLMClient` client for making calls to the LLM.
### Initialization: `__init__()` and `init()`

- **`__init__()`**: Your class's standard constructor. Use it to set up any initial state or configuration your agent needs. Contains a single argument: `default_prompts` which is an optional list of strings to serve as default prompts to users
- **`init()`**: This async method is called by the platform after `__init__` but before `run`. It provides your agent with a connected `redis_client` and the `chat_stream_channel` for publishing events. You should call `super().init()` if you override it.

### Publishing Helper Methods

The base class provides several async helper methods to communicate with the frontend via a Redis stream

- **`publish_message(content: str)`**: Sends a single token or chunk of the LLM's response. This is what makes the text appear word-by-word in the chat window.
- **`publish_sources(sources: list[ChatSourceCard])`**: Sends the final, post-processed data. This is typically used to display "source" chips that link back to specific dashboard elements.
- **`publish_chat_end()`**: This signals to the backend that the interaction is complete and the stream can be closed. You should always call this, preferably in a finally block.
- **`publish_thinking()`, `publish_executing_tool()`**: Not currently implemented.

### Context Helper Methods

- **`get_page_context()`**: Fetches the full data context of the current dashboard page.
- **`summarize_page()`**: A utility to generate a human-readable text summary of the page context, which can be useful for prompts when the full context is too large.

## Step-by-Step Implementation Guide


### Step 1: Create Your Agent Class

Create a new Python file and define your class, inheriting from `DispatcherAgentInterface`.

```python
# /path/to/your/custom_agent.py
from virtualitics_sdk.llm.agent import DispatcherAgentInterface, RawChatContext
from virt_llm.inference_engine._types import LLMChatMessage

class MyCustomAgent(DispatcherAgentInterface):
    async def run(self, chat_context: RawChatContext):
        # We will implement the logic here
        pass
```

### Step 2: Implement the `run` Method

The `run` method orchestrates the entire process. A typical implementation follows these steps:

1. **Pre-process Input**: Prepare the prompt for the LLM or call other Agents
2. **Stream Response**: Call the LLM and stream the response back, publishing messages as they arrive.
3. **Post-process Response**: Once the stream is complete, analyze the full text or call other Agents
4. **Clean Up**: End the chat stream.

Here is a complete example within the `run` method:

```python
# /path/to/your/custom_agent.py
import asyncio
from virtualitics_sdk.llm.agent import DispatcherAgentInterface, RawChatContext, ChatSource, ChatSourceCard
from virt_llm.inference_engine._types import LLMChatMessage

class MyCustomAgent(DispatcherAgentInterface):
    """
    A custom agent that gets dashboard context, asks the LLM a question,
    and streams the response.
    """
    async def run(self, chat_context: RawChatContext) -> dict:
        llm_response_text = []
        post_processed_data = {}

        try:
            # 1. PRE-PROCESSING
            # Get the context of the current dashboard page.
            page_context_data = await self.get_page_context(chat_context)
            page_summary = self.summarize_page(page_context_data.get('context', {}))

            # Create a detailed prompt for the LLM.
            system_prompt = "You are a helpful assistant. Here is a summary of the dashboard you are looking at."
            full_prompt = (
                f"{system_prompt}\n\n"
                f"## Page Summary\n{page_summary}\n\n"
                f"## User Question\n{chat_context.prompt}"
            )
            messages = [LLMChatMessage(role="user", content=full_prompt)]

            # 2. LLM INTERACTION & STREAMING
            # Use the llm_client from the context to stream the chat.
            stream = await chat_context.llm_client.chat(
                model=chat_context.model,
                messages=messages,
                stream=True
            )

            async for response_chunk in stream:
                content = response_chunk.message.content
                # Publish each piece of the response to the frontend.
                await self.publish_message(content=content)
                # Collect the pieces for post-processing.
                llm_response_text.append(content)

            # 3. POST-PROCESSING
            # Now that the stream is done, process the full response.
            # For this example, we'll create a simple source card.
            final_response = "".join(llm_response_text)
            source_card = ChatSourceCard(
                title="Analysis Source",
                data=[ChatSource(title="Dashboard Summary", element_type="summary")]
            )
            
            # Publish the structured post-processing data.
            await self.publish_sources(sources=[source_card])
            
            post_processed_data = {"response": final_response, "sources": [source_card.model_dump()]}

        except Exception as e:
            # Log any errors that occur.
            logger.exception(f"An error occurred in MyCustomAgent: {e}")
            # You could publish an error message to the user here.
            await self.publish_message("Sorry, an error occurred.")

        finally:
            # 4. END THE CHAT
            # This is critical to ensure the connection is closed properly.
            await self.publish_chat_end()

        return post_processed_data
```

## How DefaultDispatcherAgent Works

The `DefaultDispatcherAgent` is a pre-built implementation that you can use as a reference and a default implementation in the absence of one specified by the App developer. It introduces a more advanced pre-processing step.

- **`default_pre_processing`**: Instead of just summarizing the page, it first makes an LLM call to `extract_relevant_elements`. This asks the LLM to identify which specific charts or tables on the page are relevant to the user's question.

- **Contextual Prompting**:
  - If relevant elements are found, it injects the full JSON data for only those elements into the prompt. This gives the LLM rich, targeted data to work with.
  - If no specific elements are found, it falls back to using `summarize_page`, just like in our example.

- **Streaming and Post-processing**: Its `_stream_chat` and `default_on_llm_response` methods follow the same pattern we implemented: stream tokens, then publish the final `ChatSourceCard` data.

