from spyne import Application, rpc, ServiceBase, Unicode, Float
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication

class PropertyEvaluationService(ServiceBase):
    
    @rpc(Unicode, Unicode, _returns=Float)
    def evaluate_property(ctx, property_description, address):
        # Simulate property value evaluation based on address and description
        market_value = get_market_value(address)
        property_condition = assess_property_condition(property_description)
        legal_compliance = check_legal_compliance(property_description, address)
        
        if not legal_compliance:
            # Si la propriété n'est pas conforme, la valeur est fortement réduite
            property_value = market_value * 0.5
        else:
            # Ajustement de la valeur de la propriété en fonction de son état
            property_value = market_value + property_condition
        
        return property_value

# Simuler la récupération des données du marché immobilier
def get_market_value(address):
    # Simuler une base de données immobilière par région ou adresse
    market_data = {
        "123 Rue de Paris": 300000,
        "456 Avenue des Champs": 500000,
        "789 Boulevard Saint-Germain": 800000,
    }
    # Si l'adresse est dans la base, retourner la valeur; sinon, une valeur par défaut
    return market_data.get(address, 250000)

# Simuler une inspection de la condition de la propriété en fonction de la description
def assess_property_condition(property_description):
    if "jardin" in property_description.lower():
        return 50000  # Le jardin ajoute de la valeur
    elif "appartement" in property_description.lower():
        return -25000  # Les appartements peuvent valoir un peu moins
    elif "maison" in property_description.lower():
        return 75000  # Une maison a généralement plus de valeur
    else:
        return 0  # Aucun ajustement si l'information n'est pas disponible

# Simuler une vérification de conformité légale
def check_legal_compliance(property_description, address):
    # Simuler des règles de conformité légale : par exemple, certaines adresses ou descriptions peuvent avoir des problèmes légaux
    if "litige" in property_description.lower() or "non conforme" in property_description.lower():
        return False  # Propriété non conforme
    return True  # Par défaut, conforme

# Créer l'application Spyne
application = Application([PropertyEvaluationService],
                          tns='property_evaluation_service',
                          in_protocol=Soap11(validator='lxml'),
                          out_protocol=Soap11())

if __name__ == '__main__':
    wsgi_application = WsgiApplication(application)
    from wsgiref.simple_server import make_server
    server = make_server('0.0.0.0', 8003, wsgi_application)
    print("Property Evaluation Service started on http://localhost:8003")
    server.serve_forever()
