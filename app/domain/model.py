import enum
import uuid
from typing import List, Dict, Type, ClassVar
from langchain_core.messages import HumanMessage, AIMessage
import pydantic
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
    recollecting_info: str = "recollecting_info"
    waiting_professional: str = "waiting_professional"
    scheduling_appointment: str = "scheduling_appointment"
    rejected: str = "rejected"


class Chat(Entity):
    messages: List[Message] = pydantic.Field(default_factory=list)
    table_name: ClassVar[str] = "chats"
    status: ChatStatus = ChatStatus.recollecting_info
