import unittest
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import datetime
import os

SCOPES = ["https://www.googleapis.com/auth/calendar"]

class TestGoogleCalendarIntegration(unittest.TestCase):
    def setUp(self):
        creds = None
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "../client_secret_app_escritorio_oauth.json", SCOPES
                )
                creds = flow.run_local_server(port=0)
            with open("token.json", "w") as token:
                token.write(creds.to_json())
        self.service = build("calendar", "v3", credentials=creds)

    def test_create_event(self):
        calendar_id = 'primary'
        start_time = datetime.datetime(2024, 4, 9, 16, 0, 0)
        end_time = datetime.datetime(2024, 4, 9, 17, 0, 0)
        patient_name = 'Paciente Ficticio'
        consultation_reason = 'Consulta de rutina'
        event = {
            'summary': f'Cita con {patient_name} - {consultation_reason}',
            'start': {
                'dateTime': start_time.strftime("%Y-%m-%dT%H:%M:%S"),
                'timeZone': 'America/Bogota',
            },
            'end': {
                'dateTime': end_time.strftime("%Y-%m-%dT%H:%M:%S"),
                'timeZone': 'America/Bogota',
            },
        }
        try:
            created_event = self.service.events().insert(calendarId=calendar_id, body=event).execute()
            self.assertIsNotNone(created_event['id'])
        except HttpError as err:
            self.fail(f"Test failed with error: {err}")

if __name__ == '__main__':
    unittest.main()