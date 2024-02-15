from typing import List, Optional, Tuple

from langchain import agents as langchain_agents_executor
from langchain import chat_models as langchain_chat_models
from langchain import prompts
from langchain.agents import format_scratchpad as langchain_format_scratchpad
from langchain.agents import output_parsers as langchain_output_parsers
from langchain.tools import render as langchain_render
from langchain_core.messages import base as base_langchain_messages
from app.adapters.langchain import langchain_agents
from app.domain import model


_MEMORY_KEY = "chat_history"


def invoke(
    chat_history: model.Chat,
    query: str,
) -> str:
    agent = langchain_agents.get_agent(chat_history=chat_history)
    if chat_history:
        return _invoke_with_chat_history(
            chat_history=chat_history, query=query, agent=agent
        )
    return _invoke(query=query, agent=agent)


def _deserialize_messages(messages: List) -> List[base_langchain_messages.BaseMessage]:
    messages_deserialized = []
    for message in messages:
        type_message = model.TYPE_MESSAGE_FACTORY[message.sender]
        messages_deserialized.append(type_message(content=message.message))
    return messages_deserialized


def _invoke(query: str, agent: langchain_agents.Agent) -> str:
    prompt = prompts.ChatPromptTemplate.from_messages(
        [
            ("system", agent.instruction),
            ("user", "{input}"),
            prompts.MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )
    llm = langchain_chat_models.ChatOpenAI(model="gpt-3.5-turbo", temperature=0.1)  # type: ignore

    llm_with_tools = llm.bind(
        functions=[
            langchain_render.format_tool_to_openai_function(t) for t in agent.tools
        ]
    )

    concreted_agent = (
        {
            "input": lambda x: x["input"],
            "agent_scratchpad": lambda x: langchain_format_scratchpad.format_to_openai_function_messages(
                x["intermediate_steps"]
            ),
        }
        | prompt
        | llm_with_tools
        | langchain_output_parsers.OpenAIFunctionsAgentOutputParser()
    )

    agent_executor = langchain_agents_executor.AgentExecutor(
        agent=concreted_agent, tools=agent.tools, verbose=True, return_intermediate_steps=True  # type: ignore
    )

    result = agent_executor.invoke({"input": query})
    return result["output"]


def _invoke_with_chat_history(
    chat_history: model.Chat,
    query: str,
    agent: langchain_agents.Agent,
) -> str:

    prompt = prompts.ChatPromptTemplate.from_messages(
        [
            ("system", agent.instruction),
            prompts.MessagesPlaceholder(variable_name=_MEMORY_KEY),
            ("user", "{input}"),
            prompts.MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )
    llm = langchain_chat_models.ChatOpenAI(model="gpt-3.5-turbo", temperature=0.1)  # type: ignore

    llm_with_tools = llm.bind(
        functions=[
            langchain_render.format_tool_to_openai_function(t) for t in agent.tools
        ]
    )

    concreted_agent = (
        {
            "input": lambda x: x["input"],
            "agent_scratchpad": lambda x: langchain_format_scratchpad.format_to_openai_function_messages(
                x["intermediate_steps"]
            ),
            "chat_history": lambda x: x["chat_history"],
        }
        | prompt
        | llm_with_tools
        | langchain_output_parsers.OpenAIFunctionsAgentOutputParser()
    )

    agent_executor = langchain_agents_executor.AgentExecutor(
        agent=concreted_agent, tools=agent.tools, verbose=True, return_intermediate_steps=True  # type: ignore
    )
    chat_history_deserialized = _deserialize_messages(chat_history.messages)
    result = agent_executor.invoke({"input": query, "chat_history": chat_history_deserialized})
    return result["output"]
