from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from database import db

app = FastAPI()

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
        result = await db["loan_performance"].insert_one(loan_data.dict())
        return {"decision": decision, "loan_performance_id": str(result.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def analyze_risk(solvency_score, employment_status, credit_history):
    if employment_status == "Stable" and credit_history == "Good" and solvency_score > 1000:
        return True
    return False

def check_financial_policies(solvency_score, loan_amount, property_value):
    minimum_solvency_threshold = 800
    max_loan_to_value_ratio = 0.8
    loan_to_value_ratio = loan_amount / property_value
    return solvency_score >= minimum_solvency_threshold and loan_to_value_ratio <= max_loan_to_value_ratio
