from typing import List, Dict, Type, Tuple

from app.adapters.langchain import langchain_tools
from app.domain import model
import pydantic


info_agent_instructions = """Eres Claudia, una secretaria altamente experimentada en la organización y programación 
de citas, y actualmente trabajas para la doctora Mariana. Al iniciar la conversación y solo al iniciar, asegúrate de 
presentarte. Si ya cuentas con la información necesaria del paciente, como su nombre, edad y motivo de consulta, 
procede a enviarla directamente a la doctora. amablemente al paciente que proporcione la información faltante en un 
solo mensaje. No es necesario pedir detalles del motivo de consulta. Si las intenciones del paciente para agendar una 
cita son evidentes, evita hacer preguntas genéricas como '¿Quieres agendar una cita?' o '¿En qué puedo ayudarte?'. En 
lugar de eso, enfócate en recopilar la información específica necesaria para la programación de la cita. Si te 
pregunta y solo si te preguntan, puedes proporcionar información sobre las especialidades de la doctora, 
como la ansiedad y los problemas familiares. La doctora NO trabaja otros temas diferentes.  Es Mandatorio NO 
mencionar que enviarás esta información a la doctora durante la conversación.  Es muy importante que solo respondas 
sobre la informacion que tienes en este prompt"""


class Agent(pydantic.BaseModel):
    name: str
    instruction: str
    tools: List


class _InfoRecollectionAgent(Agent):
    name: str = "info_recollection"
    instruction: str = info_agent_instructions
    tools: List


class _AppointmentSchedulingAgent(Agent):
    name: str = "appointment_scheduling"
    instruction: str = "I can help you with appointment scheduling"
    tools: List


_agent_strategy: Dict[model.ChatStatus, Tuple[Type[Agent], List]] = {
    model.ChatStatus.recollecting_info: (
        _InfoRecollectionAgent,
        [langchain_tools.SendPatientInfo],
    ),
    model.ChatStatus.scheduling_appointment: (_AppointmentSchedulingAgent, []),
}


def get_agent(chat_history: model.Chat) -> Agent:
    agent, tools = _agent_strategy[chat_history.status]
    configured_tools = [tool(chat_history=chat_history) for tool in tools]
    return agent(tools=configured_tools)
