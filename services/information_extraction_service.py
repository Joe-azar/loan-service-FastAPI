from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from database import db
import logging
from bson import ObjectId

app = FastAPI()


class LoanRequest(BaseModel):
    nom: str
    adresse: str
    email: str
    telephone: str
    montant: float
    revenu_mensuel: float
    depenses_mensuelles: float
    duree: int
    description_propriete: str

def clean_data(data):
    if isinstance(data, str):
        return data.strip().capitalize()
    return data  # Retourner directement les données non textuelles (comme les float)



def convert_object_id(data):
    """Convertir les ObjectId en chaînes de caractères."""
    if isinstance(data, ObjectId):
        return str(data)
    if isinstance(data, dict):
        return {key: convert_object_id(value) for key, value in data.items()}
    if isinstance(data, list):
        return [convert_object_id(item) for item in data]
    return data

@app.post("/extract_loan_information/")
async def extract_loan_information(loan_request: LoanRequest):
    loan_data = loan_request.dict()
    loan_data = {key: clean_data(value) for key, value in loan_data.items()}

    try:
        result = await db["loan_requests"].insert_one(loan_data)
        loan_data["_id"] = result.inserted_id
        loan_data = convert_object_id(loan_data)  # Convertir les ObjectId en chaînes de caractères
        return {"loan_request_id": loan_data["_id"], "extracted_info": loan_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

