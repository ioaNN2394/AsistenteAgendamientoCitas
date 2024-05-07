from pymongo import MongoClient
from AccesoDatos.Mongo_Connection import MongoConnection

class PatientModel:
    def __init__(self):
        self.mongo_connection = None
        self.db = None
        self.collection = None

    def connect(self):
        self.mongo_connection = MongoConnection()
        self.mongo_connection.connect()
        self.db = self.mongo_connection.client['Citas']
        self.collection = self.db['Pacientes']

    def insert_patient(self, patient_info):
        if not self.mongo_connection:
            self.connect()
        return self.collection.insert_one(patient_info.dict())

    def close_connection(self):
        if self.mongo_connection:
            self.mongo_connection.close()