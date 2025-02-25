from flask import Flask, request, jsonify
from pymongo import MongoClient


app = Flask (__name__)
MONGODB_URI="mongodb+srv://Digibyte:MieAyamTelur@cluster0.uap52.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
DB_NAME = "digibyte"
COLLECTION_NAME = "iot"
client = MongoClient(MONGODB_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]


@app.route('/save',methods=["POST"])
def save_data():
    data = request.get_json()
    suhu = data.get("suhu")
    kelembaban = data.get("kelembaban")
    
    simpan = {"suhu":suhu,"kelembaban":kelembaban}
    collection.insert_one(simpan)
    
    return jsonify({"message":"success"})

if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=True)