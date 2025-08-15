import redis.asyncio
from _typeshed import Incomplete
from abc import ABC, abstractmethod
from typing import Awaitable, Callable, Literal, TypedDict
from virt_llm.inference_engine._types import LLMChatMessage
from virtualitics_sdk.llm.chat import ChatSource as ChatSource, ChatSourceCard as ChatSourceCard, RawChatContext as RawChatContext

logger: Incomplete

class StreamMessage(TypedDict):
    """Event for a single message token in the stream."""
    t: Literal['message']
    d: str

class StreamPostProcessing(TypedDict):
    """Event for the final, post-processed response."""
    t: Literal['post_processing']
    d: list[ChatSourceCard]

class StreamChatEnd(TypedDict):
    """Event to signal the end of the chat stream."""
    t: Literal['chat_end']
    d: Literal['']
StreamEvent = StreamMessage | StreamPostProcessing | StreamChatEnd

class DispatcherAgentInterface(ABC):
    """
    Abstract Base Class for a dispatcher agent.

    This interface defines the contract for agents that handle the lifecycle of a
    chat interaction. This includes pre-processing user prompts, streaming responses
    from a language model, and post-processing the final response.

    It provides hooks (`on_llm_request`, `on_llm_response`) that can be used to
    customize the agent's behavior.
    """
    default_prompts: Incomplete
    redis: Incomplete
    chat_stream_channel: Incomplete
    def __init__(self, *, default_prompts: list[str] | None = None, **kwargs) -> None:
        """
        Initializes the DispatcherAgentInterface.

        :param default_prompts: An optional list of default prompts to be used by the agent.
        """
    async def init(self, redis_client: redis.asyncio.Redis, chat_stream_channel: str):
        """
        Initializes the agent with a Redis client and a channel for streaming.

        This will be called by the platform prior to calling the run function

        :param redis_client: An asynchronous Redis client instance.
        :param chat_stream_channel: The name of the Redis channel to publish stream events to.
        """
    async def publish_message(self, content: str):
        """
        Publish a message token, this will be relayed to the frontend exactly as published
        """
    async def publish_sources(self, sources: list[ChatSourceCard]):
        """
        Publish source_data (clickable chips) from post-processing LLM response
        """
    async def publish_chat_end(self):
        """
        Publish a chat end message that signals the backend to close the chat stream with the frontend
        """
    async def publish_thinking(self) -> None: ...
    async def publish_executing_tool(self) -> None: ...
    async def publish_waiting_for_input(self) -> None: ...
    async def get_page_context(self, chat_context: RawChatContext): ...
    @staticmethod
    def summarize_page(page_context: dict): ...
    @abstractmethod
    async def run(self, chat_context: RawChatContext):
        """
        The main entry point for the agent's execution logic.

        Subclasses must implement this method to define how they process a chat request.
        """

class DefaultDispatcherAgent(DispatcherAgentInterface):
    """
    A default, concrete implementation of the `DispatcherAgentInterface`.

    This agent provides a standard workflow for handling chat interactions:
    1.  Pre-processes the user prompt using `default_on_llm_request`.
    2.  Streams the response from the language model.
    3.  Post-processes the final response using `default_on_llm_response`.

    It is designed to be used out-of-the-box for simple chat use cases but can be
    customized by providing `on_llm_request` and `on_llm_response` hooks during
    initialization. It is also useful as an example implementation of extending the DispatcherAgentInterface
    """
    on_llm_request: Incomplete
    on_llm_response: Incomplete
    chat_sources: list[ChatSourceCard]
    def __init__(self, default_prompts: list[str] | None = None, on_llm_request: Callable[[RawChatContext], Awaitable[list[LLMChatMessage]]] | None = None, on_llm_response: Callable[[RawChatContext], Awaitable[ChatSourceCard]] | None = None) -> None: ...
    async def default_on_llm_request(self, chat_context: RawChatContext) -> list[LLMChatMessage]:
        """
        Handles pre-processing of the user's prompt.

        If `on_llm_request` is provided, it's called to transform the `RawChatContext`.
        Otherwise, it defaults to a simple message format containing the user's prompt.

        :param chat_context: The raw chat context containing the user's prompt.
        :return: A list of messages formatted for the LLM.
        """
    async def default_pre_processing(self, chat_context: RawChatContext) -> list[LLMChatMessage]:
        """Prepares the chat messages for the language model.

        This method orchestrates the pre-processing of a user's query by:
        1.  Fetching the full context of the current dashboard page.
        2.  Attempting to identify specific dashboard elements relevant to the user's
            prompt using an LLM-based extraction method.
        3.  If relevant elements are found, the context is filtered to include only
            the data for those elements.
        4.  If no specific elements are identified, a summary of the entire page
            context is generated instead.
        5.  Constructs a final prompt that includes system instructions, the
            processed page context (either filtered data or a summary), and the
            original user question.

        :param chat_context: The raw context of the chat, including the user's prompt.

        :return: A list containing a single `LLMChatMessage` ready to be sent to the LLM
        """
    async def extract_relevant_elements(self, chat_context: RawChatContext, simplified_context: dict):
        '''Identifies dashboard elements relevant to the user\'s question using an LLM.

        This method constructs a specialized prompt that asks the language model to act as a "matching engine." It
        provides the user\'s question and a simplified view of the available dashboard elements (plots, tables, etc.).
        The LLM is instructed to return a JSON array containing the unique IDs of the elements it deems relevant to
        the user\'s query.

        The resulting string from the LLM is then parsed to extract a clean list  of element IDs.

        :param chat_context: The context of the chat, including the user\'s prompt and the LLM client.
        :param simplified_context: A dictionary representing a summarized view of the dashboard elements.

        :return: A list of strings, where each string is the ID of a relevant dashboard element. Returns an empty list
                 if no elements are matched or if an error occurs during processing.
        '''
    def extract_list_from_json(self, json_string: str, retry_count: int = 0) -> list[str]: ...
    async def default_on_llm_response(self, chat_context: RawChatContext, response_text: list[str]) -> list[dict]:
        """
        Handles post-processing of the LLM's response.

        If `on_llm_response` is provided, it's called with the complete response text.
        Otherwise, it returns a default `ChatOutput` object.

        :param chat_context: The chat context for the current request.
        :param response_text: A list of strings representing the complete, streamed
            response from the LLM.
        :return: A dictionary representation of the processed `ChatOutput`.
        """
    async def run(self, chat_context: RawChatContext) -> dict:
        """
        Executes the default chat processing pipeline.

        This method orchestrates the agent's workflow by first preparing the
        messages for the LLM via `default_on_llm_request` and then passing them
        to `_stream_chat` to handle the streaming and post-processing.

        :param chat_context: The context for the current chat interaction.
        :return: The final, post-processed response from the LLM as a dictionary.
        """
