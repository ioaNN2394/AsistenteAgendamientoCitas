import unittest
from Infraestructura.langchain_tools import InformPsychologist, models

class TestInformPsychologist(unittest.TestCase):
    def setUp(self):
        self.chat_history = models.Chat()
        self.chat_history.status = models.ChatStatus.status3
        self.tool = InformPsychologist(chat_history=self.chat_history)

    def test_run_MeetPatient_true_status3(self):
        self.tool._run(
            MeetPatient=True,
            name="Test",
            age=30,
            motive="Test",
            country="Test",
            date="Test",
            run_manager=None
        )
        # Verificar que el estado del chat cambió a status4
        self.assertEqual(self.chat_history.status, models.ChatStatus.status4)

if __name__ == '__main__':
    unittest.main()