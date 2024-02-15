from typing import Callable, List, Dict, Any, Optional

from app.adapters import repository
from app.adapters.langchain import langchain_executor
from app.domain import model
from app.adapters.langchain import langchain_tools


class AgentManager:
    @classmethod
    def invoke_initial_agent(
        cls,
        repo: repository.AbstractRepository,
        query: str,
        agent_executor: Callable[[List[str], str, List], str],
        id_: str,
    ) -> Optional[str]:
        chat_history_dict = repo.get_by_id(id_=id_, table_name=model.Chat.table_name)
        if not chat_history_dict:
            chat_history = model.Chat(chat_id=id_)
        else:
            if (
                chat_history_dict["status"] == model.ChatStatus.waiting_professional
                or chat_history_dict["status"] == model.ChatStatus.rejected
            ):
                return
            chat_history = model.Chat(**chat_history_dict)

        agent_result = agent_executor(chat_history=chat_history, query=query)  # type: ignore

        new_pair_chat = cls.create_new_pair_conversation(query, agent_result)
        chat_history.messages.extend(new_pair_chat)
        repo.put(chat_history)
        return agent_result

    @classmethod
    def invoke_agent_to_accept_or_reject_patient(
        cls,
        repo: repository.AbstractRepository,
        professional_response: str,
        calendar: Callable,
        id_: str,
    ) -> str:
        chat_history_dict = repo.get_by_id(id_=id_, table_name=model.Chat.table_name)
        if not chat_history_dict:
            return "No se encuentra el paciente"
        if (
            chat_history_dict["status"] != model.ChatStatus.waiting_professional
            and chat_history_dict["status"] != model.ChatStatus.recollecting_info
        ):
            return "La solicitud del paciente ya fue atendida"
        if professional_response not in ["aceptar", "rechazar"]:
            return "La respuesta debe ser aceptar o rechazar"
        if professional_response == "rechazar":
            chat_history_dict["status"] = model.ChatStatus.rejected
            chat_history = model.Chat(**chat_history_dict)
            response = "lamentamos informarte que tu motivo de consulta no es una especialidad que atendemos en este momento"
            ai_message = model.Message(
                sender=model.SenderEnum.AIMessage,
                message=response,
            )
            chat_history.messages.append(ai_message)
            cls.send_response_to_patient(message=response)
            repo.put(chat_history)
            return "La solicitud del paciente fue rechazada"
        if professional_response == "aceptar":
            chat_history_dict["status"] = model.ChatStatus.scheduling_appointment
            chat_history = model.Chat(**chat_history_dict)
            calendar_response = calendar(query=query, tools=tools)  # type: ignore
            ai_message = model.Message(
                sender=model.SenderEnum.AIMessage, message=calendar_response
            )
            chat_history.messages.append(ai_message)
            cls.send_response_to_patient(calendar_response)
            repo.put(chat_history)
            return "La solicitud del paciente fue aceptada"

    @staticmethod
    def create_new_pair_conversation(query, agent_result) -> List[model.Message]:
        human_message = model.Message(
            sender=model.SenderEnum.HumanMessage, message=query
        )
        ai_message = model.Message(
            sender=model.SenderEnum.AIMessage, message=agent_result
        )
        return [human_message, ai_message]

    @staticmethod
    def send_response_to_patient(message:str):
        print(message)


r = repository.DynamoRepository(region_name="us-east-1")
# query_: str = "Hola buen dia, quisiera agendar una cita."
# query_ = "Claro, mi nombre es pepito tengo 22 años, motivo de consulta ansiedad"
query_: str = "hola"
agent_executor_: Callable = langchain_executor.invoke

AgentManager.invoke_initial_agent(
    repo=r, query=query_, agent_executor=agent_executor_, id_="25"
)
