from typing import Type, Any, Optional

import pydantic
from AccesoDatos.Mongo_Connection import MongoConnection
from AccesoDatos.patient_model import PatientModel
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

class _QuotetInfo(pydantic.BaseModel):
    PatienData: bool = pydantic.Field(..., description="El paciente confirma sus datos")
    payment_method: str = pydantic.Field(..., description="Metodo de pago del paciente")
    agrees_to_policies: bool = pydantic.Field(..., description="El paciente esta de acuerdo con las politicas")

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


class DoctorMPatient(pydantic.BaseModel): # M = Meet
    MeetPatient: bool = pydantic.Field(..., description="La doctora no tiene mas dudas sobre el paciente")




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
        self, chat_history: Optional[models.Chat] = None,**kwargs: Any
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
            return "Porfavor suministra todos los datos necesarios para agendar tu cita de manera correcta"

        if self.chat_history.status == models.ChatStatus.status1:
            self.chat_history.status = models.ChatStatus.status2
        return "Hola otra vez, para continuar con el agendamiento de la cita envia (Continuar)"



class VerifyPatientInfo(langchain_core_tools.BaseTool):
    """Tool that fetches active deployments."""

    name: str = "Verify_patient_info"
    description: str = (
        "Util cuando para verificar las politicas de la cita y tipo de pago del paciente"
    )
    args_schema: Type[pydantic.BaseModel] = _QuotetInfo
    chat_history: Optional[models.Chat] = None
    return_direct = True

    def __init__(
        self, chat_history: Optional[models.Chat] = None, **kwargs: Any

    ) -> None:
        super().__init__(**kwargs)
        self.chat_history = chat_history


    def _run(
            self,
            PatienData: bool,
            payment_method: str,
            agrees_to_policies: bool,
            name: str,
            age: int,
            motive: str,
            country: str,
            date: str,
            run_manager: Optional[
                langchain_core_callbacks.CallbackManagerForToolRun
            ] = None,
    ) -> str:

        if PatienData and agrees_to_policies:
            if self.chat_history.status == models.ChatStatus.status2:
                patient_info = _PatientInfo(name=name, age=age, motive=motive, country=country, date=date)
                self.chat_history.status = models.ChatStatus.status3

                patient_model = PatientModel()
                patient_model.insert_patient(patient_info)
                return "Hola Doctora Mariana."

class InformPsychologist(langchain_core_tools.BaseTool):
    """Tool that informs the psychologist about a new appointment."""

    name: str = "inform_psychologist_status3"
    description: str = (
        "Used when a patient has requested an appointment and the chat status is status3. This tool informs the psychologist about the appointment and provides all the patient's data."
    )
    args_schema: Type[pydantic.BaseModel] = DoctorMPatient
    chat_history: Optional[models.Chat] = None
    return_direct = True

    def __init__(
        self, chat_history: Optional[models.Chat] = None, **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)
        self.chat_history = chat_history

    def _run(
            self,
            MeetPatient: bool,
            run_manager: Optional[
                langchain_core_callbacks.CallbackManagerForToolRun
            ] = None,
    ) -> str:
        if MeetPatient and self.chat_history.status == models.ChatStatus.status3:
            self.chat_history.status = models.ChatStatus.status4
        else:
            return "No entiendo lo que quieres decir"



