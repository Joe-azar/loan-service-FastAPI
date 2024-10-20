from fastapi import FastAPI
from pydantic import BaseModel
import random  # Ajout de l'importation du module random
import logging

app = FastAPI()


class SolvencyCheck(BaseModel):
    nom: str
    revenu_mensuel: float
    depenses_mensuelles: float

@app.post("/check_solvency/")
async def check_solvency(sol_check: SolvencyCheck):
    credit_score = get_credit_score(sol_check.nom)
    solvency_score = (sol_check.revenu_mensuel - sol_check.depenses_mensuelles) + credit_score * 0.1

    logging.info(f"Solvency Score: {solvency_score} for {sol_check.nom}")

    return {"solvency_score": solvency_score}

def get_credit_score(name):
    credit_data = {
        "John Doe": 750,
        "Jane Smith": 650,
        "Alice Johnson": 800,
        "Bob Brown": 550
    }
    return credit_data.get(name, random.randint(600, 800))  # Utilisation de random
