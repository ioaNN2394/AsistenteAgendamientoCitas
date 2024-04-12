import unittest
import dateparser
import datetime

class TestDateParser(unittest.TestCase):
    def test_parse_spanish_date(self):
        # Fecha en texto en español
        date_string = "1 de junio"

        # Convertir la fecha de texto a un objeto datetime
        date = dateparser.parse(date_string)

        # Verificar que el objeto datetime es correcto
        self.assertEqual(date.year, datetime.datetime.now().year)

if __name__ == '__main__':
    unittest.main()