from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional


# ---------------------------
#       DATA MODELS
# ---------------------------
class Shareholder(BaseModel):
    name: str
    type: str  # "individual" or "company"
    ownership: float
    country: Optional[str] = None


class CompanyInput(BaseModel):
    company_name: str
    country: str
    shareholders: List[Shareholder] = []


# ---------------------------
#         FASTAPI APP
# ---------------------------
app = FastAPI(
    title="UBO Finder API",
    description="Automated UBO discovery + ownership mapping + risk analysis skeleton",
    version="0.1.0"
)


# ---------------------------
#         ENDPOINTS
# ---------------------------
@app.get("/health")
def health_check():
    return {"status": "ok", "message": "UBO Finder backend is running"}


@app.post("/analyze")
def analyze_company(payload: CompanyInput):
    """
    Bu endpoint hələlik placeholder cavab qaytarır.
    Sonra buraya:
    - ownership tree qurma
    - UBO discovery
    - sanction/PEP check
    - risk scoring
    mərhələləri əlavə olunacaq.
    """

    return {
        "received_input": payload.dict(),
        "ubos": [],               # UBO-lar burada olacaq
        "risk_level": "pending",  # "low" / "medium" / "high" olacaq
        "reasons": [],            # Risk səbəbləri (sanction, PEP, high-risk country...)
        "ownership_tree": {}      # Ownership ağacı
    }
