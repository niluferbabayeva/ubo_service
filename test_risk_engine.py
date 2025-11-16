from services.risk_engine import score_ubo, score_company, final_risk_score

print("\n=== STEP 4 — RISK ENGINE TEST ===\n")

# Fake UBO flags
ubo_flags = [
    {"pep": True, "sanctioned": False},
    {"pep": False, "sanctioned": False},
    {"pep": False, "sanctioned": True}
]

ubo_scores = [score_ubo(f) for f in ubo_flags]
print("UBO Scores:", ubo_scores)

# Fake company profile
company = {
    "ownership_layers": 3,
    "competitor_risk": "medium",
    "vendor_risk": "low",
    "management_risk": "low",
    "legal_issues": False,
    "tax_debt": False
}

company_score = score_company(company)
print("Company Score:", company_score)

result = final_risk_score(ubo_scores, company_score)
print("\nFINAL RESULT:", result)
