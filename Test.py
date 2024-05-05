import unittest
import pymongo
from unittest.mock import patch, MagicMock
from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure
from AccesoDatos.Mongo_Connection import MongoConnection

from Infraestructura.langchain_tools import PatientInfoChecker, VerifyPatientInfoChecker, SendEmail, VerifyDoctorMPatient, SendPatientInfo, VerifyPatientInfo, InformPsychologist
from Infraestructura.models import Chat, ChatStatus
from Infraestructura.langchain_tools import _PatientInfo, _QuotetInfo, DoctorMPatient
from langchain_core.callbacks import CallbackManagerForToolRun

from AccesoDatos.patient_model import PatientModel
from Infraestructura.langchain_tools import _PatientInfo

from Infraestructura.AvoidCircularImport import _PatientInfo
from Infraestructura.agenda import GoogleCalendarManager

import os
from LogicaNegocio.langchain_executor import invoke
from dotenv import load_dotenv
load_dotenv()  # take environment variables from .env.

#----------------------------------Pruebas Integracion----------------------------------


class TestSendEmail(unittest.TestCase):
    def setUp(self):
        self.patient_info = _PatientInfo(name="John Doe", age=30, motive="Consultation", country="CANADA", date="2022-12-12")


    @patch('smtplib.SMTP_SSL')
    def test_send(self, mock_smtp):
        patient_info = _PatientInfo(name="John Doe", age=30, motive="Consultation", country="CANADA", date="2022-12-12")
        email_sender = SendEmail(patient_info)
        result, error = email_sender.send()
        self.assertTrue(result)
        self.assertIsNone(error)
class TestPatientModel(unittest.TestCase):
    def setUp(self):
        self.patient_model = PatientModel()
        self.patient_info = _PatientInfo(name="John Doe", age=30, motive="Consultation", country="USA", date="2022-12-12")

    def test_insert_patient(self):
        # Insert the test patient into the database
        self.patient_model.insert_patient(self.patient_info)

        # Retrieve the patient from the database
        patient_in_db = self.patient_model.collection.find_one({"name": self.patient_info.name})

        # Verify that the retrieved patient's information matches the test patient's information
        self.assertEqual(patient_in_db["name"], self.patient_info.name)
        self.assertEqual(patient_in_db["age"], self.patient_info.age)
        self.assertEqual(patient_in_db["motive"], self.patient_info.motive)
        self.assertEqual(patient_in_db["country"], self.patient_info.country)
        self.assertEqual(patient_in_db["date"], self.patient_info.date)

class TestGoogleCalendarManager(unittest.TestCase):
    def setUp(self):
        self.patient_model = PatientModel()
        self.patient_info = _PatientInfo(name="Test Name", motive="TEST", date="2024-5-5", age=30, country="Country Name")
        self.calendar = GoogleCalendarManager()

    def test_create_event(self):
        # Test get_free_busy_agenda
        response = self.calendar.get_free_busy_agenda()
        self.assertIsNotNone(response)

        # Test get_upcoming_events
        self.calendar.get_upcoming_events()

        # Test create_patient_event
        self.calendar.create_patient_event(self.patient_info)

#----------------------------------Pruebas Unitarias----------------------------------


class TestOpenAIConnection(unittest.TestCase):
    @patch('os.environ', {'OPENAI_API_KEY': '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'})
    def test_openai_connection(self):
        # Create a test chat
        chat = Chat()

        # Call the invoke function with a simple query
        response = invoke(query='Hello, world!', chat_history=chat)

        # Check if the response is not empty
        self.assertIsNotNone(response)
#Tools

class TestPatientInfoChecker(unittest.TestCase):
    def setUp(self):
        self.patient_info = _PatientInfo(name="John Doe", age=30, motive="Consultation", country="USA", date="2022-12-12")

    def test_is_info_complete(self):
        checker = PatientInfoChecker(self.patient_info)
        self.assertTrue(checker.is_info_complete())

    def test_doctor_patient_info_is_complete(self):
        verify_all_info = DoctorMPatient(MeetPatient=True, AllInfo="All info", name="John Doe", age=30, motive="Consultation", country="USA", date="2022-12-12")
        self.assertTrue(VerifyDoctorMPatient.is_info_complete(verify_all_info))

class TestSendPatientInfo(unittest.TestCase):
    def setUp(self):
        self.chat_history = Chat(status=ChatStatus.status1)
        self.patient_info = _PatientInfo(name="John Doe", age=30, motive="Consultation", country="USA", date="2022-12-12")
        self.tool = SendPatientInfo(chat_history=self.chat_history)

    def test_send_patient_info_run(self):
        result = self.tool._run(name=self.patient_info.name, age=self.patient_info.age, motive=self.patient_info.motive, country=self.patient_info.country, date=self.patient_info.date)
        self.assertEqual(result, "Hola otra vez, para continuar con el agendamiento de la cita envía (Continuar)")

class TestVerifyPatientInfo(unittest.TestCase):
    def setUp(self):
        self.chat_history = Chat(status=ChatStatus.status2)
        self.verify_patient = _QuotetInfo(PatienData=True, payment_method="Cash", agrees_to_policies=True, name="John Doe", age=30, motive="Consultation", country="USA", date="2022-12-12")
        self.tool = VerifyPatientInfo(chat_history=self.chat_history)

    def test_verify_patient_info_run(self):
        result = self.tool._run(PatienData=self.verify_patient.PatienData, payment_method=self.verify_patient.payment_method, agrees_to_policies=self.verify_patient.agrees_to_policies, name=self.verify_patient.name, age=self.verify_patient.age, motive=self.verify_patient.motive, country=self.verify_patient.country, date=self.verify_patient.date)
        self.assertEqual(result, "Hola doctora Mariana ya tengo la información del paciente")

class TestInformPsychologist(unittest.TestCase):
    def setUp(self):
        self.chat_history = Chat(status=ChatStatus.status3)
        self.verify_all_info = DoctorMPatient(MeetPatient=True, AllInfo="All info", name="John Doe", age=30, motive="Consultation", country="USA", date="2022-12-12")
        self.tool = InformPsychologist(chat_history=self.chat_history)

    def test_inform_psychologist_run(self):
        result = self.tool._run(MeetPatient=self.verify_all_info.MeetPatient, AllInfo=self.verify_all_info.AllInfo, name=self.verify_all_info.name, age=self.verify_all_info.age, motive=self.verify_all_info.motive, country=self.verify_all_info.country, date=self.verify_all_info.date)
        self.assertEqual(result, "Ya tengo la respuesta de la Doctora Mariana, gracias por tu tiempo.")


#----------------------------------Prueba End to End----------------------------------

class TestEndToEnd(unittest.TestCase):
    def setUp(self):
        self.chat = Chat()
        self.patient_info = _PatientInfo(name="John Doe", age=30, motive="Consultation", country="USA", date="2022-12-12")
        self.send_patient_info_tool = SendPatientInfo(chat_history=self.chat)
        self.verify_patient_info_tool = VerifyPatientInfo(chat_history=self.chat)
        self.inform_psychologist_tool = InformPsychologist(chat_history=self.chat)
        self.calendar_manager = GoogleCalendarManager()
        self.email_sender = SendEmail(self.patient_info)

    def test_end_to_end(self):
        # Simulate interaction in state 1
        self.send_patient_info_tool._run(name="John Doe", age=30, motive="Consultation", country="USA", date="2022-12-12")
        self.assertEqual(self.chat.status, ChatStatus.status2)

        # Supply patient data
        verify_patient = _QuotetInfo(PatienData=True, payment_method="Cash", agrees_to_policies=True, name="John Doe", age=30, motive="Consultation", country="USA", date="2022-12-12")

        # Simulate interaction in state 2
        self.verify_patient_info_tool._run(PatienData=True, payment_method="Cash", agrees_to_policies=True, name="John Doe", age=30, motive="Consultation", country="USA", date="2022-12-12")
        self.assertEqual(self.chat.status, ChatStatus.status3)

        # Confirm patient data and payment method
        verify_all_info = DoctorMPatient(MeetPatient=True, AllInfo="All info", name="John Doe", age=30, motive="Consultation", country="USA", date="2022-12-12")

        # Simulate interaction in state 3
        self.inform_psychologist_tool._run(MeetPatient=True, AllInfo="All info", name="John Doe", age=30, motive="Consultation", country="USA", date="2022-12-12")
        self.assertEqual(self.chat.status, ChatStatus.status4)

        # Create event
        self.calendar_manager.create_patient_event(self.patient_info)

        # Send email
        result, error = self.email_sender.send()
        self.assertTrue(result)
        self.assertIsNone(error)

if __name__ == '__main__':
    unittest.main()
