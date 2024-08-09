from pymongo import MongoClient

class MongoDBManager:
    def __init__(self, db_name="transcripts_db", collection_name="questions"):
        self.client = MongoClient("mongodb+srv://admin:admin@cluster0.uvmcziq.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def insert_question_answer(self, question_list):
        self.collection.insert_many(question_list)        

    def get_top_questions(self, top_n=5):
        return list(self.collection.find().limit(top_n))

    def get_all_questions(self):
        return list(self.collection.find())

    def delete_all_questions(self):
        self.collection.delete_many({})

    def delete_question(self, question_id):
        self.collection.delete_one({"_id": question_id})
