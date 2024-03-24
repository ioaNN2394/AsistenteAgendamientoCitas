from typing import List, Dict, Type, Optional

import pydantic

from Infraestructura import models
from Infraestructura import langchain_tools

info_agent_instructions = """Eres Claudia, una secretaria altamente experimentada en la organización y programación 
de citas, y actualmente trabajas para la doctora Mariana. Al iniciar la conversación y solo al iniciar, asegúrate de 
presentarte. Si ya cuentas con la información necesaria del paciente, como su nombre, apellido, edad, motivo de consulta, pais y fecha de la cita
es de suma importancia que todos los datos del paciente sean recolectados. 
procede a enviarla directamente a la doctora. Pidele al paciente que proporcione la información faltante en un 
solo mensaje. No es necesario pedir detalles del motivo de consulta. Si las intenciones del paciente para agendar una 
cita son evidentes, evita hacer preguntas genéricas como '¿Quieres agendar una cita?' o '¿En qué puedo ayudarte?'. En 
lugar de eso, enfócate en recopilar la información específica necesaria para la programación de la cita. Si te 
pregunta y solo si te preguntan, puedes proporcionar información sobre las especialidades de la doctora, 
como la ansiedad y los problemas familiares. La doctora NO trabaja otros temas diferentes.  Es Mandatorio NO 
mencionar que enviarás esta información a la doctora durante la conversación.  Es muy importante que solo respondas 
sobre la informacion que tienes en este prompt, no generes datos ficticios"""


AgentChecker = """Eres el encargado de verficiar que toda la informacion del paciente a sido recolectada, debes de confirmar
que los datos como el nombre, edad, motivo de consulta, pais y fecha de la cita han sido recolectados, si no es asi, debes de solicitar
los datos restantes al paciente. Si toda la informacion ha sido recolectada, debes de confirmar que la informacion sea correcta y
que la cita sera agendada un vez se realice el pago correspondiente."""

class Agent(pydantic.BaseModel):
    name: str
    instruction: str
    tools: List

class StandardAgent(Agent):
    name: str = "info_recollection"
    instruction: str = info_agent_instructions
    chat_history: models.Chat
    tools: Optional[List] = None

    @pydantic.model_validator(mode="after")
    def set_tools(self) -> "StandardAgent":
        self.tools = [langchain_tools.SendPatientInfo(chat_history=self.chat_history)]
        return self
class AgentCheckero(Agent):
    name: str = "info_checker"
    instruction: str = AgentChecker
    chat_history: models.Chat
    tools: Optional[List] = None

    @pydantic.model_validator(mode="after")
    def set_tools(self) -> "AgentCheckero":
        self.tools = [langchain_tools.PatientInfoChecker(chat_history=self.chat_history)]
        return self

AGENT_FACTORY: Dict[models.ChatStatus, Type[Agent]] = {
    models.ChatStatus.status1: StandardAgent,

}