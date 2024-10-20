from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import logging

app = FastAPI()


class PropertyEvaluation(BaseModel):
    description_propriete: str
    adresse: str

@app.post("/evaluate_property/")
async def evaluate_property(property_eval: PropertyEvaluation):
    market_value = get_market_value(property_eval.adresse)
    property_condition = assess_property_condition(property_eval.description_propriete)
    legal_compliance = check_legal_compliance(property_eval.description_propriete)

    if not legal_compliance:
        property_value = market_value * 0.5
    else:
        property_value = market_value + property_condition

    logging.info(f"Evaluated Property Value: {property_value} for {property_eval.adresse}")

    return {"property_value": property_value}

def get_market_value(address):
    market_data = {
        "123 Rue de Paris": 300000,
        "456 Avenue des Champs": 500000,
        "789 Boulevard Saint-Germain": 800000,
    }
    return market_data.get(address, 250000)

def assess_property_condition(description):
    if "jardin" in description.lower():
        return 50000
    elif "appartement" in description.lower():
        return -25000
    elif "maison" in description.lower():
        return 75000
    return 0

def check_legal_compliance(description):
    if "litige" in description.lower() or "non conforme" in description.lower():
        return False
    return True
