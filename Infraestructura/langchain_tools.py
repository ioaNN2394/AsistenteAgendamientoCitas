from typing import Type, Any, Optional
import os
from dotenv import load_dotenv
from email.message import EmailMessage
import ssl
import smtplib
import pydantic
from AccesoDatos.patient_model import PatientModel
from langchain_core import (
    tools as langchain_core_tools,
    callbacks as langchain_core_callbacks,
)

from Infraestructura import models
from Infraestructura.agenda import GoogleCalendarManager


class _PatientInfo(pydantic.BaseModel):
    name: str = pydantic.Field(..., description="Nombre del paciente")
    age: int = pydantic.Field(..., description="Edad del paciente")
    motive: str = pydantic.Field(..., description="Motivo de la consulta")
    country: str = pydantic.Field(..., description="País del paciente")
    date: str = pydantic.Field(..., description="Fecha de la cita")


class _QuotetInfo(pydantic.BaseModel):
    PatienData: bool = pydantic.Field(..., description="El paciente confirma sus datos")
    payment_method: str = pydantic.Field(..., description="Método de pago del paciente")
    agrees_to_policies: bool = pydantic.Field(
        ..., description="El paciente está de acuerdo con las políticas"
    )
    name: str = pydantic.Field(..., description="Ya tenemos el nombre del paciente")
    age: int = pydantic.Field(..., description="Ya tenemos la edad del paciente")
    motive: str = pydantic.Field(..., description="Ya tenemos su motivo de consulta")
    country: str = pydantic.Field(..., description="Ya tenemos su pais")
    date: str = pydantic.Field(..., description="Ya tenemos la fecha de la cita")


class PatientInfoChecker:
    def __init__(self, patient_info: _PatientInfo):
        self.patient_info = patient_info

    def is_info_complete(self) -> bool:
        return all(
            value not in (None, "") for value in self.patient_info.dict().values()
        )


class VerifyPatientInfoChecker:
    def __init__(self, VerifyPatient: _QuotetInfo):
        self.VerifyPatient = VerifyPatient

    def is_info_complete(self) -> bool:
        # Verificar que todos los valores no sean None o vacíos
        if not all(
            value not in (None, " ") for value in self.VerifyPatient.dict().values()
        ):
            return False

        # Verificar que los valores booleanos sean True
        bool_fields = [
            "PatienData",
            "agrees_to_policies",
        ]  # Añade aquí los nombres de los campos booleanos
        if not all(getattr(self.VerifyPatient, field) for field in bool_fields):
            return False

        return True


class SendEmail:
    def __init__(self, patient_info):
        load_dotenv()
        self.emailsender = "agentsendmail007@gmail.com"
        self.password = os.getenv("PASSWORD")
        self.email_reciever = "johansa2394@gmail.com"

        self.subject = "Datos de nuevo paciente "
        self.body = (
            f"Hola Doctora Mariana, Tiene un nuevo paciente sus datos son:\n "
            f"Nombre del paciente: {patient_info.name}\n "
            f"Edad del paciente: {patient_info.age}\n "
            f"Motivo de consulta: {patient_info.motive}\n"
            f"País del paciente: {patient_info.country}\n "
            f"Fecha de preferencia de la cita: {patient_info.date}"
        )

    def send(self):
        try:
            em = EmailMessage()
            em["From"] = self.emailsender
            em["To"] = self.email_reciever
            em["Subject"] = self.subject
            em.set_content(self.body)

            context = ssl.create_default_context()
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
                smtp.login(self.emailsender, self.password)
                smtp.sendmail(self.emailsender, self.email_reciever, em.as_string())
            return True, None
        except Exception as e:
            return False, str(e)


class DoctorMPatient(pydantic.BaseModel):
    MeetPatient: bool = pydantic.Field(
        ..., description="La doctora no tiene más dudas sobre el paciente"
    )
    AllInfo: str = pydantic.Field(
        ..., description="La doctora conoce todo sobre el paciente"
    )
    name: str = pydantic.Field(..., description="Nombre del paciente")
    age: int = pydantic.Field(..., description="Edad del paciente")
    motive: str = pydantic.Field(..., description="Motivo de la consulta")
    country: str = pydantic.Field(..., description="País del paciente")
    date: str = pydantic.Field(..., description="Fecha de la cita")


class VerifyDoctorMPatient:
    @staticmethod
    def is_info_complete(VerifyAllInfo: DoctorMPatient) -> bool:
        # Verificar que todos los valores no sean None o vacíos
        if not all(value not in (None, "") for value in VerifyAllInfo.dict().values()):
            return False

        # Verificar que AllInfo no esté vacío
        if not VerifyAllInfo.AllInfo:
            return False

        return True


# Primer flujo
class SendPatientInfo(langchain_core_tools.BaseTool):
    name: str = "send_patient_info_to_professional"
    description: str = "Util cuando el paciente quiere agendar una cita con la doctora, para enviar información"
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
        patient_info = _PatientInfo(
            name=name, age=age, motive=motive, country=country, date=date
        )
        info_checker = PatientInfoChecker(patient_info)

        if not info_checker.is_info_complete():
            return "Por favor, suministra todos los datos necesarios para agendar tu cita de manera correcta"

        if self.chat_history.status == models.ChatStatus.status1:
            self.chat_history.status = models.ChatStatus.status2
            return "Hola otra vez, para continuar con el agendamiento de la cita envía (Continuar)"
        else:
            return "Error: Estado incorrecto del chat"


# Segundo flujo
class VerifyPatientInfo(langchain_core_tools.BaseTool):
    """Tool that fetches active deployments."""

    name: str = "Verify_patient_info"
    description: str = "Util cuando para verificar las politicas de la cita y tipo de pago del paciente"
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
        VerifyPatient = _QuotetInfo(
            PatienData=PatienData,
            payment_method=payment_method,
            agrees_to_policies=agrees_to_policies,
            name=name,
            age=age,
            motive=motive,
            country=country,
            date=date,
        )

        info_Verify = VerifyPatientInfoChecker(VerifyPatient)
        if not info_Verify.is_info_complete():
            return (
                "Debes de estar de acuerdo con las politicas para continuar con la cita"
            )

        if self.chat_history.status == models.ChatStatus.status2:
            self.chat_history.status = models.ChatStatus.status3
            patient_info = _PatientInfo(
                name=name, age=age, motive=motive, country=country, date=date
            )
            email_sender = SendEmail(patient_info)
            email_sender.send()
        return "Hola doctora Mariana ya tengo la información del paciente"


# Tercer flujo
class InformPsychologist(langchain_core_tools.BaseTool):
    name: str = "inform_psychologist_status3"
    description: str = (
        "Util cuando un paciente ha solicitado una cita y el estado del chat es status3. "
        "Esta herramienta informa al psicólogo sobre la cita programada y proporciona todos los"
        " datos del paciente."
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
        AllInfo: str,
        name: str,
        age: int,
        motive: str,
        country: str,
        date: str,
        run_manager: Optional[
            langchain_core_callbacks.CallbackManagerForToolRun
        ] = None,
    ) -> str:
        VerifyAllInfo = DoctorMPatient(
            MeetPatient=MeetPatient,
            AllInfo=AllInfo,
            name=name,
            age=age,
            motive=motive,
            country=country,
            date=date,
        )

        # Verificamos si los campos requeridos están completos
        if not VerifyDoctorMPatient.is_info_complete(VerifyAllInfo):
            return "Por favor, asegúrate de confirmar que estás dispuesta a agendar la cita."

        if self.chat_history.status == models.ChatStatus.status3:
            self.chat_history.status = models.ChatStatus.status4
            patient_info = _PatientInfo(
                name=name, age=age, motive=motive, country=country, date=date
            )
            calendar_manager = GoogleCalendarManager()
            calendar_manager.create_patient_event(patient_info)
            patient_model = PatientModel()
            patient_model.insert_patient(patient_info)
            return "Ya tengo la respuesta de la Doctora Mariana, gracias por tu tiempo."
        else:
            return "Error: Estado incorrecto del chat"
