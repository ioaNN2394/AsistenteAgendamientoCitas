import enum
import uuid
from typing import List, Dict, Type

import pydantic
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.messages import base as base_langchain_messages


class SenderEnum(str, enum.Enum):
    HumanMessage: str = "HumanMessage"
    AIMessage: str = "AIMessage"


TYPE_MESSAGE_FACTORY: Dict[SenderEnum, Type[base_langchain_messages.BaseMessage]] = {
    SenderEnum.HumanMessage: HumanMessage,
    SenderEnum.AIMessage: AIMessage,
}


def _generate_id() -> str:
    return str(uuid.uuid4())


class Entity(pydantic.BaseModel):
    chat_id: str = pydantic.Field(default_factory=_generate_id)


class Message(pydantic.BaseModel):
    sender: SenderEnum
    message: str


class ChatStatus(str, enum.Enum):
    status1: str = "status1"
    status2: str = "status2"


class Chat(Entity):
    messages: List[Message] = pydantic.Field(default_factory=list)
    status: ChatStatus = ChatStatus.status1
