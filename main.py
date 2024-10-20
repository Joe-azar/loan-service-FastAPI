import subprocess
import time
import os
import tkinter as tk
from tkinter import messagebox, filedialog
import shutil
import signal
import sys
import logging
import requests  # Utilisé pour faire l'appel HTTP à l'API

# Initialiser les logs
logging.basicConfig(filename="service_logs.log", level=logging.INFO, format='%(asctime)s - %(message)s')

# Liste des services à lancer
services = [
    {"name": "Information Extraction Service", "script": "uvicorn services.information_extraction_service:app --reload --port 8001"},
    {"name": "Solvency Check Service", "script": "uvicorn services.solvency_check_service:app --reload --port 8002"},
    {"name": "Property Evaluation Service", "script": "uvicorn services.property_evaluation_service:app --reload --port 8003"},
    {"name": "Approval Decision Service", "script": "uvicorn services.approval_decision_service:app --reload --port 8004"},
    {"name": "Composite Loan Evaluation Service", "script": "uvicorn web_composite_service:app --reload --port 8000"},
    {"name": "Watchdog Trigger", "script": "python watchdog_trigger.py"}
]

processes = []

def launch_service(service):
    try:
        process = subprocess.Popen(service["script"], shell=True)
        processes.append(process)
        logging.info(f"{service['name']} lancé avec succès.")
    except Exception as e:
        logging.error(f"Erreur lors du lancement de {service['name']}: {str(e)}")

def stop_services():
    print("\nArrêt des services...")
    for process in processes:
        try:
            process.terminate()
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            process.kill()
        print(f"Service {process.args[1]} arrêté.")
    print("Tous les services sont arrêtés.")
    sys.exit(0)

def signal_handler(sig, frame):
    stop_services()

def submit_request():
    nom = entry_nom.get()
    adresse = entry_adresse.get()
    email = entry_email.get()
    telephone = entry_telephone.get()
    montant = entry_montant.get()
    duree = entry_duree.get()
    description = entry_description.get()
    revenu = entry_revenu.get()
    depenses = entry_depenses.get()

    if not all([nom, adresse, email, telephone, montant, duree, description, revenu, depenses]):
        messagebox.showwarning("Erreur", "Tous les champs doivent être remplis.")
        return

    loan_request = {
        "nom": nom,
        "adresse": adresse,
        "email": email,
        "telephone": telephone,
        "montant": montant,
        "duree": duree,
        "description_propriete": description,
        "revenu_mensuel": revenu,
        "depenses_mensuelles": depenses
    }

    data_directory = "data"
    if not os.path.exists(data_directory):
        os.makedirs(data_directory)

    request_filename = os.path.join(data_directory, f"loan_request_{nom.replace(' ', '_')}.txt")
    
    with open(request_filename, "w", encoding="utf-8") as f:
        f.write(str(loan_request))

    # Appel à l'API pour évaluer la demande de prêt
    try:
        response = requests.post("http://localhost:8000/evaluate_loan/", json=loan_request)
        response.raise_for_status()
        decision_data = response.json()
        decision = decision_data.get("decision", "Aucune décision reçue")

        # Afficher la décision dans une boîte de dialogue
        messagebox.showinfo("Décision de Prêt", f"La décision pour le prêt de {nom} est : {decision}")
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Erreur", f"Erreur lors de la soumission de la demande : {e}")

    logging.info("Demande de prêt soumise avec succès.")

def submit_file():
    file_path = filedialog.askopenfilename(title="Sélectionnez un fichier de demande",
                                           filetypes=(("Fichiers texte", "*.txt"), ("Tous les fichiers", "*.*")))

    if file_path:
        data_directory = "data"
        if not os.path.exists(data_directory):
            os.makedirs(data_directory)

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                loan_request = f.read()
            
            # Convertir le contenu du fichier en dictionnaire
            loan_request_dict = eval(loan_request)  # ATTENTION: Utilise une méthode plus sûre si possible

            # Appel à l'API pour évaluer la demande de prêt
            response = requests.post("http://localhost:8000/evaluate_loan/", json=loan_request_dict)
            response.raise_for_status()
            decision_data = response.json()
            decision = decision_data.get("decision", "Aucune décision reçue")

            # Afficher la décision dans une boîte de dialogue
            messagebox.showinfo("Décision de Prêt", f"La décision pour le prêt  est : {decision}")

            # Copie du fichier dans le répertoire "data"
            shutil.copy(file_path, data_directory)
            logging.info(f"Fichier {file_path} déposé avec succès.")
        except Exception as e:
            logging.error(f"Erreur lors de la copie du fichier ou de l'évaluation : {str(e)}")
            messagebox.showerror("Erreur", f"Impossible de copier ou d'évaluer le fichier : {str(e)}")

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)

    print("Lancement de tous les services...")

    for service in services:
        launch_service(service)
        time.sleep(1)

    print("Tous les services sont en cours d'exécution.")

    root = tk.Tk()
    root.title("Soumission de Demande de Prêt Immobilier")

    fields = [
        ("Nom du Client:", "entry_nom"),
        ("Adresse:", "entry_adresse"),
        ("Email:", "entry_email"),
        ("Numéro de Téléphone:", "entry_telephone"),
        ("Montant du Prêt Demandé (EUR):", "entry_montant"),
        ("Durée du Prêt (années):", "entry_duree"),
        ("Description de la Propriété:", "entry_description"),
        ("Revenu Mensuel (EUR):", "entry_revenu"),
        ("Dépenses Mensuelles (EUR):", "entry_depenses")
    ]

    for label_text, variable_name in fields:
        frame = tk.Frame(root)
        label = tk.Label(frame, text=label_text)
        label.pack(side="left")
        entry = tk.Entry(frame)
        entry.pack(side="right", fill="x", expand=True)
        frame.pack(fill="x", padx=5, pady=5)
        globals()[variable_name] = entry

    submit_button = tk.Button(root, text="Soumettre une nouvelle demande", command=submit_request)
    submit_button.pack(pady=10)

    submit_file_button = tk.Button(root, text="Déposer un fichier de demande", command=submit_file)
    submit_file_button.pack(pady=10)

    root.mainloop()

    stop_services()
