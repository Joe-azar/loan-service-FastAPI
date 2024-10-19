import re
import sqlite3
from spyne import Application, rpc, ServiceBase, ComplexModel, Unicode
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication

# Connexion à la base de données SQLite
conn = sqlite3.connect('loan_requests.db')
c = conn.cursor()

# Création de la table si elle n'existe pas déjà
c.execute('''
    CREATE TABLE IF NOT EXISTS loan_requests (
        id INTEGER PRIMARY KEY,
        name TEXT, 
        address TEXT, 
        email TEXT, 
        phone TEXT, 
        loan_amount REAL, 
        monthly_income REAL, 
        monthly_expenses REAL, 
        duration INTEGER, 
        property_description TEXT
    )
''')
conn.commit()

# Prétraitement du texte
def preprocess_text(loan_request):
    loan_request = loan_request.strip()
    loan_request = re.sub(r'\s+', ' ', loan_request)  # Remplacer les espaces multiples par un seul
    return loan_request

# Stockage des informations extraites dans la base de données
def store_extracted_info(info):
    with sqlite3.connect('loan_requests.db') as conn:
        c = conn.cursor()
        c.execute('''
            INSERT INTO loan_requests (name, address, email, phone, loan_amount, 
                monthly_income, monthly_expenses, duration, property_description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (info['Nom'], info['Adresse'], info['Email'], info['Téléphone'], 
              info['Montant du Prêt'], info['Revenu Mensuel'], 
              info['Dépenses Mensuelles'], info['Durée'], info['Description de la Propriété']))
        conn.commit()

# Define a complex type for key-value pairs
class DictionaryItem(ComplexModel):
    key = Unicode
    value = Unicode

class InformationExtractionService(ServiceBase):
    
    @rpc(Unicode, _returns=DictionaryItem)
    def extract_loan_information(ctx, loan_request):
        loan_request = preprocess_text(loan_request)  # Prétraitement du texte
        
        try:
            nom = re.search(r'Nom du Client: (.+)', loan_request).group(1)
        except AttributeError:
            return DictionaryItem(key="error", value="Nom du client manquant")

        try:
            adresse = re.search(r'Adresse: (.+)', loan_request).group(1)
        except AttributeError:
            return DictionaryItem(key="error", value="Adresse manquante")

        try:
            email = re.search(r'Email: (.+)', loan_request).group(1)
        except AttributeError:
            return DictionaryItem(key="error", value="Email manquant")

        try:
            telephone = re.search(r'Numéro de Téléphone: (.+)', loan_request).group(1)
        except AttributeError:
            return DictionaryItem(key="error", value="Numéro de téléphone manquant")

        try:
            montant = int(re.search(r'Montant du Prêt Demandé: (\d+) EUR', loan_request).group(1))
        except AttributeError:
            return DictionaryItem(key="error", value="Montant du prêt manquant")

        try:
            duree = int(re.search(r'Durée du Prêt: (\d+) ans', loan_request).group(1))
        except AttributeError:
            return DictionaryItem(key="error", value="Durée du prêt manquante")

        try:
            description_propriete = re.search(r'Description de la Propriété: (.+)', loan_request).group(1)
        except AttributeError:
            return DictionaryItem(key="error", value="Description de la propriété manquante")

        try:
            revenu_mensuel = int(re.search(r'Revenu Mensuel: (\d+) EUR', loan_request).group(1))
        except AttributeError:
            return DictionaryItem(key="error", value="Revenu mensuel manquant")

        try:
            depenses_mensuelles = int(re.search(r'Dépenses Mensuelles: (\d+) EUR', loan_request).group(1))
        except AttributeError:
            return DictionaryItem(key="error", value="Dépenses mensuelles manquantes")
        
        # Créer un dictionnaire avec les informations extraites
        extracted_info = {
            "Nom": nom,
            "Adresse": adresse,
            "Email": email,
            "Téléphone": telephone,
            "Montant du Prêt": montant,
            "Durée": duree,
            "Description de la Propriété": description_propriete,
            "Revenu Mensuel": revenu_mensuel,
            "Dépenses Mensuelles": depenses_mensuelles
        }

        # Stocker les informations extraites dans la base de données
        store_extracted_info(extracted_info)

        # Retourner les informations extraites
        return DictionaryItem(key="extracted_info", value=str(extracted_info))

# Créer l'application Spyne
application = Application([InformationExtractionService],
                          tns='information.extraction.service',
                          in_protocol=Soap11(validator='lxml'),
                          out_protocol=Soap11())

if __name__ == '__main__':
    wsgi_application = WsgiApplication(application)
    from wsgiref.simple_server import make_server
    server = make_server('0.0.0.0', 8001, wsgi_application)
    print("Information Extraction Service started on http://localhost:8001")
    server.serve_forever()
