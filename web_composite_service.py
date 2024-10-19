from spyne import Application, rpc, ServiceBase, Unicode
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
from suds.client import Client

class LoanEvaluationService(ServiceBase):
    
    @rpc(Unicode, _returns=Unicode)
    def evaluate_loan(ctx, loan_request):
        try:
            # Appel du service d'extraction d'informations
            extraction_service_url = "http://localhost:8001/InformationExtractionService?wsdl"
            extraction_client = Client(extraction_service_url)
            extracted_info = eval(extraction_client.service.extract_loan_information(loan_request).value)
            
            # Appel du service de vérification de solvabilité
            solvency_service_url = "http://localhost:8002/SolvencyCheckService?wsdl"
            solvency_client = Client(solvency_service_url)
            solvency_score = solvency_client.service.check_solvency(
                extracted_info['Nom'], extracted_info['Revenu Mensuel'], extracted_info['Dépenses Mensuelles']
            )
            
            # Appel du service d'évaluation de la propriété
            property_service_url = "http://localhost:8003/PropertyEvaluationService?wsdl"
            property_client = Client(property_service_url)
            property_value = property_client.service.evaluate_property(
                extracted_info['Description de la Propriété'], extracted_info['Adresse']
            )
            
            # Appel du service de décision d'approbation
            approval_service_url = "http://localhost:8004/ApprovalDecisionService?wsdl"
            approval_client = Client(approval_service_url)
            decision = approval_client.service.make_decision(
                solvency_score, property_value, extracted_info['Montant du Prêt'], 
                "Stable",  
                "Good"    
            )
            
            return f"Decision: {decision}, Solvency Score: {solvency_score}, Property Value: {property_value}"

        except Exception as e:
            return f"An error occurred during loan evaluation: {e}"

# Créer l'application Spyne
application = Application([LoanEvaluationService],
                          tns='composite.loan_service',
                          in_protocol=Soap11(validator='lxml'),
                          out_protocol=Soap11())

if __name__ == '__main__':
    wsgi_application = WsgiApplication(application)
    from wsgiref.simple_server import make_server
    server = make_server('0.0.0.0', 8000, wsgi_application)
    print("Composite Loan Evaluation Service started on http://localhost:8000")
    server.serve_forever()
