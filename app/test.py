import os
import unittest
from unittest.mock import patch

from dotenv import load_dotenv

from AccesoDatos.patient_model import PatientModel
from Infraestructura.agenda import GoogleCalendarManager
from Infraestructura.langchain_tools import (
    PatientInfoChecker,
    SendEmail,
    VerifyDoctorMPatient,
    SendPatientInfo,
    VerifyPatientInfo,
    InformPsychologist,
    _QuotetInfo,
    DoctorMPatient,
    _PatientInfo,
)
from Infraestructura.models import Chat, ChatStatus, Message, SenderEnum
from LogicaNegocio import langchain_executor
from LogicaNegocio.langchain_executor import invoke

load_dotenv()  # take environment variables from .env.


# ----------------------------------Pruebas Integracion----------------------------------


class TestSendEmail(unittest.TestCase):
    def setUp(self):
        self.patient_info = _PatientInfo(
            name="John Doe",
            age=30,
            motive="Consultation",
            country="CANADA",
            date="2022-12-12",
        )

    @patch("smtplib.SMTP_SSL")
    def test_send_email_to_patient(self, mock_smtp):
        patient_info = _PatientInfo(
            name="John Doe",
            age=30,
            motive="Consultation",
            country="CANADA",
            date="2022-12-12",
        )
        email_sender = SendEmail(patient_info)
        result, error = email_sender.send()
        self.assertTrue(result)
        self.assertIsNone(error)


class TestPatientModel_Insert_in_DataBase(unittest.TestCase):
    def setUp(self):
        self.patient_model = PatientModel()
        self.patient_info = _PatientInfo(
            name="John Doe",
            age=30,
            motive="Consultation",
            country="USA",
            date="2022-12-12",
        )

    def test_insert_patient_into_database(self):
        # Insert the app patient into the database
        self.patient_model.insert_patient(self.patient_info)

        # Retrieve the patient from the database
        patient_in_db = self.patient_model.collection.find_one(
            {"name": self.patient_info.name}
        )

        # Verify that the retrieved patient's information matches the app patient's information
        self.assertEqual(patient_in_db["name"], self.patient_info.name)
        self.assertEqual(patient_in_db["age"], self.patient_info.age)
        self.assertEqual(patient_in_db["motive"], self.patient_info.motive)
        self.assertEqual(patient_in_db["country"], self.patient_info.country)
        self.assertEqual(patient_in_db["date"], self.patient_info.date)


class TestGoogleCalendarManager(unittest.TestCase):
    def setUp(self):
        self.patient_model = PatientModel()
        self.patient_info = _PatientInfo(
            name="Test Name",
            motive="TEST",
            date="2024-5-5",
            age=30,
            country="Country Name",
        )
        self.calendar = GoogleCalendarManager()

    def test_create_calendar_event_for_patient(self):
        # Test get_free_busy_agenda
        response = self.calendar.get_free_busy_agenda()
        self.assertIsNotNone(response)

        # Test get_upcoming_events
        self.calendar.get_upcoming_events()

        # Test create_patient_event
        self.calendar.create_patient_event(self.patient_info)


class TestOpenAIConnection(unittest.TestCase):
    @patch(
        "os.environ",
        {"OPENAI_API_KEY": " "},
    )
    def test_openai_connection(self):
        # Create a app chat
        chat = Chat()

        # Call the invoke function with a simple query
        response = invoke(query="Hello, world!", chat_history=chat)

        # Check if the response is not empty
        self.assertIsNotNone(response)


# ----------------------------------Pruebas Unitarias----------------------------------


class TestPatientInfoChecker(unittest.TestCase):
    def setUp(self):
        self.patient_info = _PatientInfo(
            name="John Doe",
            age=30,
            motive="Consultation",
            country="USA",
            date="2022-12-12",
        )

    def test_patient_info_completeness(self):
        checker = PatientInfoChecker(self.patient_info)
        self.assertTrue(checker.is_info_complete())

    def test_doctor_patient_info_completeness(self):
        verify_all_info = DoctorMPatient(
            MeetPatient=True,
            AllInfo="All info",
            name="John Doe",
            age=30,
            motive="Consultation",
            country="USA",
            date="2022-12-12",
        )
        self.assertTrue(VerifyDoctorMPatient.is_info_complete(verify_all_info))


class TestSendPatientInfo(unittest.TestCase):
    def setUp(self):
        self.chat_history = Chat(status=ChatStatus.status1)
        self.patient_info = _PatientInfo(
            name="John Doe",
            age=30,
            motive="Consultation",
            country="USA",
            date="2022-12-12",
        )
        self.tool = SendPatientInfo(chat_history=self.chat_history)

    def test_send_patient_info_run(self):
        result = self.tool._run(
            name=self.patient_info.name,
            age=self.patient_info.age,
            motive=self.patient_info.motive,
            country=self.patient_info.country,
            date=self.patient_info.date,
        )
        self.assertEqual(
            result,
            "Hola otra vez, para continuar con el agendamiento de la cita envía (Continuar)",
        )


class TestVerifyPatientInfo(unittest.TestCase):
    def setUp(self):
        self.chat_history = Chat(status=ChatStatus.status2)
        self.verify_patient = _QuotetInfo(
            PatienData=True,
            payment_method="Cash",
            agrees_to_policies=True,
            name="John Doe",
            age=30,
            motive="Consultation",
            country="USA",
            date="2022-12-12",
        )
        self.tool = VerifyPatientInfo(chat_history=self.chat_history)

    def test_verify_patient_info_run(self):
        result = self.tool._run(
            PatienData=self.verify_patient.PatienData,
            payment_method=self.verify_patient.payment_method,
            agrees_to_policies=self.verify_patient.agrees_to_policies,
            name=self.verify_patient.name,
            age=self.verify_patient.age,
            motive=self.verify_patient.motive,
            country=self.verify_patient.country,
            date=self.verify_patient.date,
        )
        self.assertEqual(
            result, "Hola doctora Mariana ya tengo la información del paciente"
        )


class TestInformPsychologist(unittest.TestCase):
    def setUp(self):
        self.chat_history = Chat(status=ChatStatus.status3)
        self.verify_all_info = DoctorMPatient(
            MeetPatient=True,
            AllInfo="All info",
            name="John Doe",
            age=30,
            motive="Consultation",
            country="USA",
            date="2022-12-12",
        )
        self.tool = InformPsychologist(chat_history=self.chat_history)

    def test_inform_psychologist_run(self):
        result = self.tool._run(
            MeetPatient=self.verify_all_info.MeetPatient,
            AllInfo=self.verify_all_info.AllInfo,
            name=self.verify_all_info.name,
            age=self.verify_all_info.age,
            motive=self.verify_all_info.motive,
            country=self.verify_all_info.country,
            date=self.verify_all_info.date,
        )
        self.assertEqual(
            result,
            "Ya tengo la respuesta de la Doctora Mariana, gracias por tu tiempo.",
        )

    # ----------------------------------Prueba End to End----------------------------------


class TestEndToEndStatus1(unittest.TestCase):
    def setUp(self):
        os.environ["OPENAI_API_KEY"] = " "

    def test_workflow_status1(self):
        # Crear una instancia de chat con el estado inicial
        chat = Chat()

        # Definir los inputs del usuario
        user_inputs = [
            "Hola",
            "Quiero agendar una cita",
            "Mi nombre es Juan",
            "Tengo 30 años",
            "Vivo en México",
            "Tengo ansiedad",
            "La cita puede ser el 30 de marzo",
            "Continuar",
        ]

        # Palabras clave o frases esperadas en las respuestas del agente
        expected_keywords = [
            "Claudia",
            "agendar",
            "Juan",
            "Juan",
            "cita",
            "cita",
            "Continuar",
        ]

        for user_input, expected_keyword in zip(user_inputs, expected_keywords):
            # Invocar la función con el input del usuario y la instancia de chat
            print("chat.status: ", chat.status)
            ai_response = langchain_executor.invoke(query=user_input, chat_history=chat)

            # Verificar que la respuesta del agente contiene la palabra clave o frase esperada
            self.assertIn(expected_keyword, ai_response)

            # Añadir los mensajes al historial de chat
            human_message = Message(sender=SenderEnum.HumanMessage, message=user_input)
            ai_message = Message(sender=SenderEnum.AIMessage, message=ai_response)
            chat.messages.extend([human_message, ai_message])

            # Si el estado del chat es 'status2', terminar la prueba
            if chat.status == ChatStatus.status2:
                break

        # Verificar que el estado del chat es el esperado
        self.assertEqual(chat.status, "status2")


if __name__ == "__main__":
    unittest.main()
