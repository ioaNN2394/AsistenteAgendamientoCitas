import pymongo

Mongo_Host = "localhost"
Mongo_Puerto = 27017
Mongo_Tiempo_espera = 1000

Mongo_URI = "mongodb://"+Mongo_Host+":"+str(Mongo_Puerto)+"/"

try:
    client = pymongo.MongoClient(Mongo_URI, serverSelectionTimeoutMS=Mongo_Tiempo_espera)
    client.server_info()
    print("Conectado a MongoDB")
    client.close()

except pymongo.errors.ServerSelectionTimeoutError as errorTiempo:
    print("Tiempo excedido: ", errorTiempo)
    client = None
except pymongo.errors.ConnectionFailure as errorConexion:
    print("Error al conectar a MongoDB: ", errorConexion)
    client = None