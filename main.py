from fastapi import FastAPI
from services.analyzer import analyze
from services.screening import load_screening_list

app = FastAPI()

screening_db = load_screening_list("data/sanctions_pep_mock.csv")

@app.post("/analyze_company")
def analyze_company(raw_company: dict):
    return analyze(raw_company, screening_db)
