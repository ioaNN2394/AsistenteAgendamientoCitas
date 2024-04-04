import unittest
from AccesoDatos.patient_model import PatientModel

class Test_Add_Patient_Data(unittest.TestCase):
    def test_insert_patient(self):
        # Create a PatientModel instance
        patient_model = PatientModel()

        # Define test data
        test_data = {
            "name": "TJohan",
            "age": 20,
            "motive": "Test Ansidad",
            "country": "Test Colombia",
            "date": "2024-02-12"
        }

        # Insert test data into the database
        insert_result = patient_model.insert_patient(test_data)

        # Check if the data was inserted
        if insert_result.inserted_id is None:
            print("Failed to insert data")
        else:
            print(f"Data inserted with id {insert_result.inserted_id}")

        # Close the connection
        patient_model.close_connection()

if __name__ == '__main__':
    unittest.main()