import grpc
import pymongo
import logging
from concurrent import futures
import sys
sys.path.append('../') 
import reminders_pb2
import reminders_pb2_grpc



class ReminderService(reminders_pb2_grpc.ReminderServiceServicer):
    def __init__(self):
        self.client = pymongo.MongoClient("mongodb://localhost:27017/") 
        self.db = self.client["RemindersDB"]  
        self.collection = self.db["ReminderList"]  
        logging.info("Connected to MongoDB")  

    def AddReminder(self, request, context):
        logging.info("Received AddReminder request: %s", request)
        reminder_data = {
            "id": request.id,
            "title": request.title,
            "deadline": request.deadline,
            "category": request.category,
            "deskripsi": request.deskripsi
        }
        self.collection.insert_one(reminder_data) 
        return request

    def GetAll(self, request, context):
        logging.info("Received GetAll request")
        reminder_list = []
        for reminder_data in self.collection.find():
            reminder = reminders_pb2.Reminder(
                id=reminder_data["id"],
                title=reminder_data["title"],
                deadline=reminder_data["deadline"],
                category=reminder_data["category"],
                deskripsi=reminder_data["deskripsi"]
            )
            reminder_list.append(reminder)
        return reminders_pb2.ReminderList(reminders=reminder_list)
    
    def GetReminder(self, request, context):
        logging.info("Received GetReminder request for Reminder title: %s", request.title)
        reminder_data = self.collection.find_one({"title": request.title})
        if reminder_data:
            reminder = reminders_pb2.Reminder(
                id=reminder_data["id"],
                title=reminder_data["title"],
                deadline=reminder_data["deadline"],
                category=reminder_data["category"],
                deskripsi=reminder_data["deskripsi"]
            )
            return reminder
        else:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Reminder not found")
            return reminders_pb2.Reminder()
        
    def UpdateReminder(self, request, context):
        logging.info("Received UpdateReminder request for reminder ID: %s", request.id)
        reminder_data = self.collection.find_one({"id": request.id})
        if reminder_data:
            update_data = {}
            if request.title:
                update_data["title"] = request.title
            if request.deadline:
                update_data["deadline"] = request.deadline
            if request.category:
                update_data["category"] = request.category
            if request.deskripsi:
                update_data["deskripsi"] = request.deskripsi

            self.collection.update_one({"id": request.id}, {"$set": update_data})
            return reminders_pb2.Reminder(id=request.id, title=request.title, deadline=request.deadline, category=request.category, deskripsi=request.deskripsi)
        else:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Reminder not found")
            return reminders_pb2.Reminder()

    def DeleteReminder(self, request, context):
        logging.info("Received DeleteReminder request for Reminder ID: %s", request.id)
        result = self.collection.delete_one({"id": request.id})
        if result.deleted_count > 0:
            return reminders_pb2.Empty()
        else:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Reminder not found")
            return reminders_pb2.Empty()

def serve():
    logging.basicConfig(level=logging.INFO)
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    reminders_pb2_grpc.add_ReminderServiceServicer_to_server(ReminderService(), server)
    server.add_insecure_port('[::]:5000')
    server.start()
    logging.info("Server started. Listening on port 5000...")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()