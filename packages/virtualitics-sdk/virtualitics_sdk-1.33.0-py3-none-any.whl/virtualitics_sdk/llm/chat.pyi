from _typeshed import Incomplete
from pydantic import BaseModel
from typing import Literal
from virt_llm import AsyncLLMClient as AsyncLLMClient
from virtualitics_sdk import Page as Page

logger: Incomplete

class RawChatContext(BaseModel):
    user_id: str
    app_id: str
    chat_id: str
    chat_index: int
    step_name: str
    element_id: str
    prompt: str
    llm_host: str
    model: str
    response: str | None
    llm_client: AsyncLLMClient | None
    class Config:
        arbitrary_types_allowed: bool

class ProcessedChatMessage(BaseModel):
    role: Literal['user', 'system']
    content: str

class ChatSource(BaseModel):
    title: str
    element_type: str

class ChatSourceCard(BaseModel):
    title: str
    data: list[ChatSource]
    def to_dict(self): ...

def extract_context_from_page(page: Page): ...
