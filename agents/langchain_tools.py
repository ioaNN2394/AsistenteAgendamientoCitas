from typing import Type, Any, Optional

import pydantic
from langchain_core import (
    tools as langchain_core_tools,
    callbacks as langchain_core_callbacks,
)

import models


class _PatientInfo(pydantic.BaseModel):
    name: str = pydantic.Field(..., description="Nombre del paciente")
    age: int = pydantic.Field(..., description="Edad del paciente")
    motive: str = pydantic.Field(..., description="Motivo de la consulta")


class SendPatientInfo(langchain_core_tools.BaseTool):
    """Tool that fetches active deployments."""

    name: str = "send_patient_info_to_professional"
    description: str = (
        "Util cuando el paciente quiere agendar una cita con la doctora, para enviar informacion"
    )
    args_schema: Type[pydantic.BaseModel] = _PatientInfo
    chat_history: Optional[models.Chat] = None
    return_direct = True

    def __init__(
        self, chat_history: Optional[models.Chat] = None, **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)
        self.chat_history = chat_history

    def _run(
        self,
        name: str,
        age: int,
        motive: str,
        run_manager: Optional[
            langchain_core_callbacks.CallbackManagerForToolRun
        ] = None,
    ) -> str:
        if self.chat_history:
            self.chat_history.status = models.ChatStatus.status2
        return f"Vale, regalame un momento"
