from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from database import db

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

@app.post("/extract_loan_information/")
async def extract_loan_information(loan_request: LoanRequest):
    # Stocker les informations extraites dans MongoDB
    loan_data = loan_request.dict()
    try:
        result = await db["loan_requests"].insert_one(loan_data)
        return {"loan_request_id": str(result.inserted_id), "extracted_info": loan_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
