from typing import Type, Any, Optional

import pydantic

from langchain_core import (
    tools as langchain_core_tools,
    callbacks as langchain_core_callbacks,
)

from Infraestructura import models


class _PatientInfo(pydantic.BaseModel):
    name: str = pydantic.Field(..., description="Nombre del paciente")
    age: int = pydantic.Field(..., description="Edad del paciente")
    motive: str = pydantic.Field(..., description="Motivo de la consulta")
    country: str = pydantic.Field(..., description="Pais del paciente")
    date: str = pydantic.Field(..., description="Fecha de la cita")


class PatientInfoChecker:
    def __init__(self, patient_info: _PatientInfo):
        self.patient_info = patient_info

    def is_info_complete(self) -> bool:
        return all(value not in (None, '') for value in self.patient_info.dict().values())

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
            country: str,
            date: str,
            run_manager: Optional[
                langchain_core_callbacks.CallbackManagerForToolRun
            ] = None,
    ) -> str:
        patient_info = _PatientInfo(name=name, age=age, motive=motive, country=country, date=date)
        info_checker = PatientInfoChecker(patient_info)

        if not info_checker.is_info_complete():
            return "Please provide all the required information: name, age, motive, country, and date."

        if self.chat_history:
            self.chat_history.status = models.ChatStatus.status2
        return f"Vale, regalame un momento"
