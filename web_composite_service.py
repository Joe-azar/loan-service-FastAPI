from fastapi import FastAPI, HTTPException
import httpx
import logging
from bson import ObjectId

app = FastAPI()


# Fonction pour convertir les ObjectId de MongoDB en chaînes de caractères
def convert_object_id(data):
    if isinstance(data, ObjectId):
        return str(data)
    if isinstance(data, dict):
        return {key: convert_object_id(value) for key, value in data.items()}
    if isinstance(data, list):
        return [convert_object_id(item) for item in data]
    return data

@app.post("/evaluate_loan/")
async def evaluate_loan(loan_request: dict):
    try:
        # 1. Appel au service d'extraction d'informations
        async with httpx.AsyncClient() as client:
            extraction_response = await client.post("http://localhost:8001/extract_loan_information/", json=loan_request)
            extracted_info = extraction_response.json().get("extracted_info")
        
        # Vérifier que les informations sont correctement extraites
        if not extracted_info:
            raise HTTPException(status_code=500, detail="Échec de l'extraction des informations")

        # 2. Appel au service de vérification de solvabilité
        solvency_data = {
            "nom": extracted_info["nom"],
            "revenu_mensuel": extracted_info["revenu_mensuel"],
            "depenses_mensuelles": extracted_info["depenses_mensuelles"]
        }
        async with httpx.AsyncClient() as client:
            solvency_response = await client.post("http://localhost:8002/check_solvency/", json=solvency_data)
            solvency_score = solvency_response.json().get("solvency_score")
        
        # 3. Appel au service d'évaluation de la propriété
        property_data = {
            "description_propriete": extracted_info["description_propriete"],
            "adresse": extracted_info["adresse"]
        }
        async with httpx.AsyncClient() as client:
            property_response = await client.post("http://localhost:8003/evaluate_property/", json=property_data)
            property_value = property_response.json().get("property_value")

        # 4. Appel au service de décision d'approbation
        approval_data = {
            "solvency_score": solvency_score,
            "property_value": property_value,
            "loan_amount": extracted_info["montant"],
            "employment_status": "Stable",
            "credit_history": "Good"
        }
        async with httpx.AsyncClient() as client:
            approval_response = await client.post("http://localhost:8004/make_decision/", json=approval_data)
            decision = approval_response.json().get("decision")

        # Retourner la décision finale avec les scores
        return {
            "decision": decision,
            "solvency_score": solvency_score,
            "property_value": property_value
        }

    except httpx.RequestError as e:
        logging.error(f"Erreur réseau: {e}")
        raise HTTPException(status_code=502, detail=f"Erreur réseau: {str(e)}")
    except Exception as e:
        logging.error(f"Erreur interne: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur interne: {str(e)}")
