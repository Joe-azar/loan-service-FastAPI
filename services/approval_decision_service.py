from spyne import Application, rpc, ServiceBase, Float, Unicode
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
import sqlite3

# Connexion à la base de données pour suivre les performances des prêts
conn = sqlite3.connect('loan_approval.db')
c = conn.cursor()

# Créer la table pour le suivi des performances
c.execute('''
    CREATE TABLE IF NOT EXISTS loan_performance (
        id INTEGER PRIMARY KEY,
        solvency_score REAL,
        property_value REAL,
        loan_amount REAL,
        decision TEXT
    )
''')
conn.commit()

class ApprovalDecisionService(ServiceBase):
    
    @rpc(Float, Float, Float, Unicode, Unicode, _returns=Unicode)
    def make_decision(ctx, solvency_score, property_value, loan_amount, employment_status, credit_history):
        # Analyse des risques en fonction du score de solvabilité et de la valeur de la propriété
        risk_factor = analyze_risk(solvency_score, employment_status, credit_history)
        financial_policies = check_financial_policies(solvency_score, loan_amount, property_value)
        
        if risk_factor and financial_policies:
            decision = "Loan Approved"
        else:
            decision = "Loan Rejected - " + ("Risk too high" if not risk_factor else "Does not meet financial policies")

        # Stocker la décision dans la base de données pour suivi des performances
        store_loan_decision(solvency_score, property_value, loan_amount, decision)

        return decision

def analyze_risk(solvency_score, employment_status, credit_history):
    """
    Simuler l'analyse des risques en fonction de l'emploi et de l'historique de crédit.
    """
    if employment_status == "Stable" and credit_history == "Good" and solvency_score > 1000:
        return True
    return False

def check_financial_policies(solvency_score, loan_amount, property_value):
    """
    Vérifie si les politiques financières de l'institution sont respectées.
    """
    minimum_solvency_threshold = 800
    max_loan_to_value_ratio = 0.8  # Le prêt ne peut pas dépasser 80% de la valeur de la propriété
    loan_to_value_ratio = loan_amount / property_value

    if solvency_score >= minimum_solvency_threshold and loan_to_value_ratio <= max_loan_to_value_ratio:
        return True
    return False

def store_loan_decision(solvency_score, property_value, loan_amount, decision):
    """
    Stocker la décision du prêt dans une base de données pour suivi.
    """
    c.execute('''
        INSERT INTO loan_performance (solvency_score, property_value, loan_amount, decision)
        VALUES (?, ?, ?, ?)
    ''', (solvency_score, property_value, loan_amount, decision))
    conn.commit()

# Créer l'application Spyne
application = Application([ApprovalDecisionService],
                          tns='approval_decision_service',
                          in_protocol=Soap11(validator='lxml'),
                          out_protocol=Soap11())

if __name__ == '__main__':
    wsgi_application = WsgiApplication(application)
    from wsgiref.simple_server import make_server
    server = make_server('0.0.0.0', 8004, wsgi_application)
    print("Approval Decision Service started on http://localhost:8004")
    server.serve_forever()
