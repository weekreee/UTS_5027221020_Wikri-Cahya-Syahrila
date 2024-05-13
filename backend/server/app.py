from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import grpc
import os
import sys
sys.path.append(r'D:\File Kampus\Semester 4\Integrasi Sistem\5027221020_ETS\backend')
import reminders_pb2
import reminders_pb2_grpc

app = Flask(__name__)
CORS(app)  # Aktifkan CORS untuk semua rute

# Pengaturan gRPC client
grpc_channel = grpc.insecure_channel('localhost:5000') 
grpc_stub = reminders_pb2_grpc.ReminderServiceStub(grpc_channel)

# Atur folder template html
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../frontend/src/'))
app.template_folder = template_dir

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/addReminder", methods=['GET', 'POST'])
def add_reminder():
    if request.method == 'GET':
        return render_template("addReminder.html")
    elif request.method == 'POST':
        data = request.json
        reminder_request = reminders_pb2.Reminder(
            id=data['id'],
            title=data['title'],
            deadline=data['deadline'],
            category=data['category'],
            deskripsi=data['deskripsi']
        )
        response = grpc_stub.AddReminder(reminder_request)
        return jsonify({"message": "Reminder added successfully"})

@app.route("/allReminder")
def get_all_reminders():
    response = grpc_stub.GetAll(reminders_pb2.Empty())
    reminder_list = [{"id": reminder.id, "title": reminder.title, "deadline": reminder.deadline, "category": reminder.category, "deskripsi": reminder.deskripsi} for reminder in response.reminders]
    return jsonify({"reminders": reminder_list})

@app.route("/reminder/<reminder_title>")
def get_reminder(reminder_title):
    response = grpc_stub.GetReminder(reminders_pb2.ReminderTitle(title=reminder_title))
    if response.id:
        reminder_data = {"id": response.id, "title": response.title, "deadline": response.deadline, "category": response.category, "deskripsi": response.deskripsi}
        return jsonify(reminder_data)
    else:
        return jsonify({"message": "Reminder not found"}), 404
    
@app.route("/updateReminder/<reminder_id>", methods=['PUT'])
def update_reminder(reminder_id):
    data = request.json
    reminder_request = reminders_pb2.Reminder(
        id=reminder_id,
        title=data.get('title', ''),
        deadline=data.get('deadline', ''),
        category=data.get('category', ''),
        deskripsi=data.get('deskripsi', '')
    )
    response = grpc_stub.UpdateReminder(reminder_request)
    if response.id:
        return jsonify({"message": "Reminder updated successfully"})
    else:
        return jsonify({"message": "Reminder not found"}), 404

@app.route("/deleteReminder/<reminder_id>", methods=['DELETE'])
def delete_reminder(reminder_id):
    grpc_stub.DeleteReminder(reminders_pb2.ReminderId(id=reminder_id))
    return jsonify({"message": "Reminder deleted successfully"})

if __name__ == '__main__':
    app.run(debug=True)
