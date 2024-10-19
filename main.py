import subprocess
import time
import os
import tkinter as tk
from tkinter import messagebox, filedialog
import shutil
import signal
import sys

# Liste des services à lancer
services = [
    {"name": "Information Extraction Service", "script": "services/information_extraction_service.py"},
    {"name": "Solvency Check Service", "script": "services/solvency_check_service.py"},
    {"name": "Property Evaluation Service", "script": "services/property_evaluation_service.py"},
    {"name": "Approval Decision Service", "script": "services/approval_decision_service.py"},
    {"name": "Composite Loan Evaluation Service", "script": "web_composite_service.py"},
    {"name": "Watchdog Trigger", "script": "watchdog_trigger.py"}
]

processes = []

def launch_service(service):
    try:
        # Lancer le service en arrière-plan
        process = subprocess.Popen(["python", service["script"]])
        processes.append(process)
        print(f"{service['name']} lancé avec succès.")
    except Exception as e:
        print(f"Erreur lors du lancement de {service['name']}: {str(e)}")

# Fonction pour arrêter proprement tous les services
def stop_services():
    print("\nArrêt des services...")
    for process in processes:
        try:
            process.terminate()  # Essayer de terminer proprement
            process.wait(timeout=2)  # Attendre que le processus se termine
        except subprocess.TimeoutExpired:
            process.kill()  # Forcer l'arrêt si le processus ne s'arrête pas à temps
        print(f"Service {process.args[1]} arrêté.")
    print("Tous les services sont arrêtés.")
    sys.exit(0)  # Sortir proprement du programme

# Capture du signal Ctrl+C
def signal_handler(sig, frame):
    stop_services()

# Fonction pour soumettre une demande de prêt via l'interface graphique
def submit_request():
    # Récupérer les valeurs des champs
    nom = entry_nom.get()
    adresse = entry_adresse.get()
    email = entry_email.get()
    telephone = entry_telephone.get()
    montant = entry_montant.get()
    duree = entry_duree.get()
    description = entry_description.get()
    revenu = entry_revenu.get()
    depenses = entry_depenses.get()

    # Vérifier si tous les champs sont remplis
    if not all([nom, adresse, email, telephone, montant, duree, description, revenu, depenses]):
        messagebox.showwarning("Erreur", "Tous les champs doivent être remplis.")
        return

    # Création de la demande sous forme de texte
    loan_request = f"""
    Nom du Client: {nom}
    Adresse: {adresse}
    Email: {email}
    Numéro de Téléphone: {telephone}
    Montant du Prêt Demandé: {montant} EUR
    Durée du Prêt: {duree} ans
    Description de la Propriété: {description}
    Revenu Mensuel: {revenu} EUR
    Dépenses Mensuelles: {depenses} EUR
    """
    
    # Définir le chemin où le fichier sera créé
    data_directory = "data"
    if not os.path.exists(data_directory):
        os.makedirs(data_directory)

    # Sauvegarder la demande dans un fichier texte
    request_filename = os.path.join(data_directory, f"loan_request_{nom.replace(' ', '_')}.txt")
    with open(request_filename, "w", encoding="utf-8") as f:
        f.write(loan_request)

    messagebox.showinfo("Succès", "Votre demande de prêt a été soumise avec succès.")

# Fonction pour déposer un fichier existant
def submit_file():
    # Ouvrir une boîte de dialogue pour sélectionner un fichier
    file_path = filedialog.askopenfilename(title="Sélectionnez un fichier de demande",
                                           filetypes=(("Fichiers texte", "*.txt"), ("Tous les fichiers", "*.*")))

    if file_path:
        # Copier le fichier sélectionné dans le dossier data/
        data_directory = "data"
        if not os.path.exists(data_directory):
            os.makedirs(data_directory)

        try:
            shutil.copy(file_path, data_directory)
            messagebox.showinfo("Succès", "Le fichier a été déposé avec succès.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de copier le fichier: {str(e)}")

if __name__ == "__main__":
    # Lier la capture de Ctrl+C avec la fonction d'arrêt des services
    signal.signal(signal.SIGINT, signal_handler)

    print("Lancement de tous les services...")

    # Lancer chaque service
    for service in services:
        launch_service(service)
        time.sleep(1)  # Délai pour permettre à chaque service de démarrer correctement

    print("Tous les services sont en cours d'exécution.")

    # Créer l'interface graphique pour soumettre une demande de prêt
    root = tk.Tk()
    root.title("Soumission de Demande de Prêt Immobilier")

    # Création des champs de saisie
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

    # Création des labels et champs de saisie
    for label_text, variable_name in fields:
        frame = tk.Frame(root)
        label = tk.Label(frame, text=label_text)
        label.pack(side="left")
        entry = tk.Entry(frame)
        entry.pack(side="right", fill="x", expand=True)
        frame.pack(fill="x", padx=5, pady=5)
        
        # Ajout des entrées dans le dictionnaire d'entrées
        globals()[variable_name] = entry

    # Bouton de soumission
    submit_button = tk.Button(root, text="Soumettre une nouvelle demande", command=submit_request)
    submit_button.pack(pady=10)

    # Bouton pour déposer un fichier
    submit_file_button = tk.Button(root, text="Déposer un fichier de demande", command=submit_file)
    submit_file_button.pack(pady=10)

    # Lancement de l'interface graphique (bloque jusqu'à la fermeture de la fenêtre)
    root.mainloop()

    # En cas de fermeture de la fenêtre graphique (Ctrl+C ou fermeture de la fenêtre)
    stop_services()