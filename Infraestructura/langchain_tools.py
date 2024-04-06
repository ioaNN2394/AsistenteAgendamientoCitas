from typing import Type, Any, Optional
import os
from dotenv import load_dotenv
from email.message import EmailMessage
import ssl
import smtplib
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


class VerifyPatientInfoChecker:
    def __init__(self, VerifyPatient: _QuotetInfo):
        self.VerifyPatient = VerifyPatient

    def is_info_complete(self) -> bool:
        # Verificar que todos los valores no sean None o vacíos
        if not all(value not in (None, ' ') for value in self.VerifyPatient.dict().values()):
            return False

        # Verificar que los valores booleanos sean True
        bool_fields = ['PatienData', 'agrees_to_policies']  # Añade aquí los nombres de los campos booleanos
        if not all(getattr(self.VerifyPatient, field) for field in bool_fields):
            return False

        return True


class SendEmail():
    def __init__(self, patient_info):
        load_dotenv()

        self.emailsender = "agentsendmail007@gmail.com" #Se envia el correo electronico
        self.password = os.getenv("PASSWORD")
        self.email_reciever = "johansa2394@gmail.com" #Recibe el correo electronico enviado por "self.emailsender"

        self.subject = "Datos de nuevo paciente "
        self.body = (f"Hola Doctora Mariana, Tiene un nuevo paciente sus datos son:\n "
                     f"Nombre del paciente: {patient_info.name}\n "
                     f"Edad del paciente: {patient_info.age}\n "
                     f"Motivo de consulta: {patient_info.motive}\n"
                     f"Pais del paciente: {patient_info.country}\n "
                     f"Fecha de preferencia de la cita: {patient_info.date}")
        em = EmailMessage()
        em["From"] = self.emailsender
        em["To"] = self.email_reciever
        em["Subject"] = self.subject
        em.set_content(self.body)

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
            smtp.login(self.emailsender, self.password)
            smtp.sendmail(self.emailsender, self.email_reciever, em.as_string())

class DoctorMPatient(pydantic.BaseModel): # M = Meet
    MeetPatient: bool = pydantic.Field(..., description="La doctora no tiene mas dudas sobre el paciente")
    AllInfo: str = pydantic.Field(..., description="La doctora conoce todo sobre el paciente")
    name: str = pydantic.Field(..., description="Nombre del paciente")
    age: int = pydantic.Field(..., description="Edad del paciente")
    motive: str = pydantic.Field(..., description="Motivo de la consulta")
    country: str = pydantic.Field(..., description="Pais del paciente")
    date: str = pydantic.Field(..., description="Fecha de la cita")

class VerifyDoctorMPatient:
    def __init__(self, VerifyAllInfo: DoctorMPatient):
        self.VerifyAllInfo = VerifyAllInfo

    def is_info_complete(self) -> bool:
        # Verificar que todos los valores no sean None o vacíos
        if not all(value not in (None, '') for value in self.VerifyAllInfo.dict().values()):
            return False

        # Verificar que AllInfo no esté vacío
        if not self.VerifyAllInfo.AllInfo:
            return False

        return True




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
        VerifyPatient = _QuotetInfo(PatienData=PatienData, payment_method=payment_method, agrees_to_policies=agrees_to_policies, name=name, age=age, motive=motive, country=country, date=date)

        info_Verify = VerifyPatientInfoChecker(VerifyPatient)
        if not info_Verify.is_info_complete():
            return "Debes de estar de acuerdo con las politicas y confirmar tu informacion para continuar con la cita"
            #En este return seria prudente responder con "Cuales son las politicas"
        if self.chat_history.status == models.ChatStatus.status2:
            self.chat_history.status = models.ChatStatus.status3
            patient_info = _PatientInfo(name=name, age=age, motive=motive, country=country, date=date)
            SendEmail(patient_info)


        return "Hola Doctora Mariana"

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

        VerifyAllInfo = DoctorMPatient(MeetPatient=MeetPatient, AllInfo=AllInfo, name=name, age=age, motive=motive, country=country, date=date)

        info_Verify = VerifyDoctorMPatient(VerifyAllInfo)
        if not info_Verify.is_info_complete():
            return "¿Informo al paciente que usted esta dispuesta a agendar?"

        if self.chat_history.status == models.ChatStatus.status3:
            self.chat_history.status = models.ChatStatus.status4
            patient_info = _PatientInfo(name=name, age=age, motive=motive, country=country, date=date)

            patient_model = PatientModel()
            patient_model.insert_patient(patient_info)
        return "Ya tengo la respuesta de la Doctora Mariana, gracias por tu tiempo."



