from spyne import Application, rpc, ServiceBase, Float, Unicode
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
import random

class SolvencyCheckService(ServiceBase):
    
    @rpc(Unicode, Float, Float, _returns=Float)
    def check_solvency(ctx, name, monthly_income, monthly_expenses):
        # Simuler la récupération des données de bureau de crédit
        credit_score = get_credit_score(name)
        
        # Simple solvency check: revenu - dépenses + impact du score de crédit
        solvency_score = (monthly_income - monthly_expenses) + credit_score * 0.1
        return solvency_score

def get_credit_score(name):
    """
    Simule l'intégration avec un bureau de crédit.
    Renvoie un score de crédit fictif basé sur le nom du client.
    """
    # Simuler une base de données de bureaux de crédit
    credit_data = {
        "John Doe": 750,
        "Jane Smith": 650,
        "Alice Johnson": 800,
        "Bob Brown": 550
    }
    
    # Si le client existe dans la base, renvoyer le score; sinon, générer un score aléatoire
    return credit_data.get(name, random.randint(600, 800))

# Créer l'application Spyne
application = Application([SolvencyCheckService],
                          tns='solvency_check_service',
                          in_protocol=Soap11(validator='lxml'),
                          out_protocol=Soap11())

if __name__ == '__main__':
    wsgi_application = WsgiApplication(application)
    from wsgiref.simple_server import make_server
    server = make_server('0.0.0.0', 8002, wsgi_application)
    print("Solvency Check Service started on http://localhost:8002")
    server.serve_forever()
