from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from database import db
from bson import ObjectId
import logging

app = FastAPI()

logging.basicConfig(filename="approval_service.log", level=logging.INFO, format='%(asctime)s - %(message)s')

# Fonction pour convertir les ObjectId en chaînes de caractères
def convert_object_id(data):
    if isinstance(data, ObjectId):
        return str(data)
    if isinstance(data, dict):
        return {key: convert_object_id(value) for key, value in data.items()}
    if isinstance(data, list):
        return [convert_object_id(item) for item in data]
    return data

class LoanApprovalRequest(BaseModel):
    solvency_score: float
    property_value: float
    loan_amount: float
    employment_status: str
    credit_history: str

@app.post("/make_decision/")
async def make_decision(loan_data: LoanApprovalRequest):
    risk_factor = analyze_risk(loan_data.solvency_score, loan_data.employment_status, loan_data.credit_history)
    financial_policies = check_financial_policies(loan_data.solvency_score, loan_data.loan_amount, loan_data.property_value)

    if risk_factor and financial_policies:
        decision = "Loan Approved"
    else:
        decision = "Loan Rejected - " + ("Risk too high" if not risk_factor else "Does not meet financial policies")

    try:
        # Convertir l'objet Pydantic en dictionnaire pour l'insérer dans MongoDB
        loan_data_dict = loan_data.dict()
        loan_data_dict["decision"] = decision  # Ajouter la décision au dictionnaire
        
        # Enregistrer dans la collection "loan_performance"
        result = await db["loan_performance"].insert_one(loan_data_dict)
        loan_data_dict["_id"] = result.inserted_id
        loan_data_dict = convert_object_id(loan_data_dict)  # Convertir les ObjectId en chaînes de caractères

        logging.info(f"Loan performance recorded: {loan_data_dict}")
        return {"decision": decision, "loan_performance_id": loan_data_dict["_id"]}
    except Exception as e:
        logging.error(f"Error storing loan decision: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def analyze_risk(solvency_score, employment_status, credit_history):
    return employment_status == "Stable" and credit_history == "Good" and solvency_score > 1000

def check_financial_policies(solvency_score, loan_amount, property_value):
    minimum_solvency_threshold = 800
    max_loan_to_value_ratio = 0.8
    loan_to_value_ratio = loan_amount / property_value
    return solvency_score >= minimum_solvency_threshold and loan_to_value_ratio <= max_loan_to_value_ratio
