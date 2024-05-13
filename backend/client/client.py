import grpc
import sys
sys.path.append('../')  
import reminders_pb2
import reminders_pb2_grpc

def create_reminder(stub):
    reminder_id = input("Masukkan ID pengingat: ")
    title = input("Masukkan judul pengingat: ")
    deadline = input("Masukkan batas waktu pengingat: ")

    reminder = reminders_pb2.Reminder(id=reminder_id, title=title, deadline=deadline)
    response = stub.AddReminder(reminder)
    print("Respon AddReminder:", response)

def get_all_reminders(stub):
    all_reminders = stub.GetAll(reminders_pb2.Empty())
    print("Respon GetAll:", all_reminders)

def get_reminder(stub):
    reminder_id = input("Masukkan ID pengingat: ")
    reminder = stub.GetReminder(reminders_pb2.ReminderId(id=reminder_id))
    print("Respon GetReminder:", reminder)

def run():
    channel = grpc.insecure_channel('localhost:5000')
    stub = reminders_pb2_grpc.ReminderServiceStub(channel)

    while True:
        print("\n1. Tambah Pengingat\n2. Dapatkan Semua Pengingat\n3. Dapatkan Pengingat\n4. Keluar")
        choice = input("Masukkan pilihan Anda: ")

        if choice == '1':
            create_reminder(stub)
        elif choice == '2':
            get_all_reminders(stub)
        elif choice == '3':
            get_reminder(stub)
        elif choice == '4':
            break
        else:
            print("Pilihan tidak valid! Harap masukkan opsi yang valid.")

if __name__ == '__main__':
    run()
