import time
import re
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import httpx
import logging

logging.basicConfig(filename="watchdog.log", level=logging.INFO, format='%(asctime)s - %(message)s')

async def send_loan_to_composite_service(loan_request):
    composite_service_url = "http://localhost:8000/evaluate_loan/"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(composite_service_url, json=loan_request)
        decision = response.json()
        logging.info(f"Loan Evaluation Result: {decision}")
        return decision
    except Exception as e:
        logging.error(f"Failed to send loan request to composite service: {e}")
        return None

def extract_loan_information(file_content):
    loan_request = {}
    loan_request["nom"] = re.search(r"Nom du Client:\s*(.+)", file_content).group(1)
    loan_request["adresse"] = re.search(r"Adresse:\s*(.+)", file_content).group(1)
    loan_request["email"] = re.search(r"Email:\s*(.+)", file_content).group(1)
    loan_request["telephone"] = re.search(r"Numéro de Téléphone:\s*(.+)", file_content).group(1)
    loan_request["montant"] = int(re.search(r"Montant du Prêt Demandé:\s*(\d+)", file_content).group(1))
    loan_request["duree"] = int(re.search(r"Durée du Prêt:\s*(\d+)", file_content).group(1))
    loan_request["description_propriete"] = re.search(r"Description de la Propriété:\s*(.+)", file_content).group(1)
    loan_request["revenu_mensuel"] = int(re.search(r"Revenu Mensuel:\s*(\d+)", file_content).group(1))
    loan_request["depenses_mensuelles"] = int(re.search(r"Dépenses Mensuelles:\s*(\d+)", file_content).group(1))

    return loan_request

def is_valid_loan_file(file_content):
    required_fields = ["Nom du Client", "Adresse", "Montant du Prêt Demandé", "Revenu Mensuel"]
    return all(field in file_content for field in required_fields)

class MyHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            file_path = event.src_path
            logging.info(f"File {file_path} has been created.")
            
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    file_content = file.read()
                    if is_valid_loan_file(file_content):
                        loan_request = extract_loan_information(file_content)
                        logging.info(f"Extracted Loan Request:\n{loan_request}")
                        import asyncio
                        asyncio.run(send_loan_to_composite_service(loan_request))
                    else:
                        logging.error(f"Invalid file format: {file_path}")
            except Exception as e:
                logging.error(f"Error reading the file {file_path}: {e}")

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
