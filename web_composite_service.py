from fastapi import FastAPI, HTTPException
import httpx

app = FastAPI()

# Orchestration service for evaluating loan requests
@app.post("/evaluate_loan/")
async def evaluate_loan(loan_request: dict):
    try:
        # 1. Call the Information Extraction service
        extraction_response = await httpx.post("http://localhost:8001/extract_loan_information/", json=loan_request)
        extracted_info = extraction_response.json().get("extracted_info")
        
        # 2. Call the Solvency Check service
        solvency_data = {
            "nom": extracted_info["nom"],
            "revenu_mensuel": extracted_info["revenu_mensuel"],
            "depenses_mensuelles": extracted_info["depenses_mensuelles"]
        }
        solvency_response = await httpx.post("http://localhost:8002/check_solvency/", json=solvency_data)
        solvency_score = solvency_response.json()["solvency_score"]
        
        # 3. Call the Property Evaluation service
        property_data = {
            "description_propriete": extracted_info["description_propriete"],
            "adresse": extracted_info["adresse"]
        }
        property_response = await httpx.post("http://localhost:8003/evaluate_property/", json=property_data)
        property_value = property_response.json()["property_value"]

        # 4. Call the Approval Decision service
        approval_data = {
            "solvency_score": solvency_score,
            "property_value": property_value,
            "loan_amount": extracted_info["montant"],
            "employment_status": "Stable",  # Hardcoded for now
            "credit_history": "Good"  # Hardcoded for now
        }
        approval_response = await httpx.post("http://localhost:8004/make_decision/", json=approval_data)
        decision = approval_response.json()["decision"]
        
        return {
            "decision": decision,
            "solvency_score": solvency_score,
            "property_value": property_value
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
