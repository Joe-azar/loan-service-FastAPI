import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from suds.client import Client

def send_loan_to_composite_service(loan_request):
    composite_service_url = "http://localhost:8000/LoanEvaluationService?wsdl"
    client = Client(composite_service_url)
    
    try:
        decision = client.service.evaluate_loan(loan_request)
        print(f"Loan Evaluation Result: {decision}")
        return decision
    except Exception as e:
        print(f"Failed to send loan request to composite service: {e}")
        return None

# Watchdog logic
class MyHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            file_path = event.src_path
            print(f"File {file_path} has been created.")
            
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    loan_request = file.read()
                    print(f"File Content:\n{loan_request}")
                    send_loan_to_composite_service(loan_request)
            except Exception as e:
                print(f"Error reading the file {file_path}: {e}")

directory_to_watch = "./data"

observer = Observer()
observer.schedule(MyHandler(), path=directory_to_watch, recursive=False)
observer.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()

observer.join()
