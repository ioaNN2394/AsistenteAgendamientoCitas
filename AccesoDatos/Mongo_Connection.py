import pymongo

class MongoConnection:
    def __init__(self, host="localhost", port=27017, timeout=1000):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.client = None

    def connect(self):
        mongo_uri = f"mongodb://{self.host}:{self.port}/"
        try:
            self.client = pymongo.MongoClient(mongo_uri, serverSelectionTimeoutMS=self.timeout)
            self.client.server_info()  # This line will raise an exception if connection fails
            print("Conectado a MongoDB")
        except pymongo.errors.ServerSelectionTimeoutError as err:
            print("Tiempo excedido: ", err)
            self.client = None
        except pymongo.errors.ConnectionFailure as err:
            print("Error al conectar a MongoDB: ", err)
            self.client = None

    def close(self):
        if self.client is not None:
            self.client.close()
            print("Desconectado de MongoDB")

# Usage
mongo_connection = MongoConnection()
mongo_connection.connect()
# Do your operations here
mongo_connection.close()