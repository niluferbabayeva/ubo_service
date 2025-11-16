# -------------------------------
# UBO RISK SCORING
# -------------------------------

def score_ubo(flags):
    """
    flags = {"pep": bool, "sanctioned": bool}
    Returns risk score 0–5
    """
    score = 0

    if flags["sanctioned"]:
        score += 5  # highest risk
    if flags["pep"]:
        score += 3

    return score


# -------------------------------
# COMPANY RISK SCORING
# -------------------------------

def score_company(company):
    """
    company dict already normalized.
    Uses risk factors like:
    - ownership layers
    - competitor risk
    - vendor risk
    - management experience
    - tax debt
    - legal issues
    """
    score = 0

    # 1. Ownership layers
    layers = company.get("ownership_layers", 1)
    if layers >= 4:
        score += 3
    elif layers == 3:
        score += 2
    elif layers == 2:
        score += 1

    # 2. Competitor risk
    competitor = company.get("competitor_risk", "low")
    if competitor == "high":
        score += 3
    elif competitor == "medium":
        score += 2

    # 3. Vendor/Supply risk
    supply = company.get("vendor_risk", "low")
    if supply == "high":
        score += 3
    elif supply == "medium":
        score += 1

    # 4. Management experience risk
    mgmt = company.get("management_risk", "low")
    if mgmt == "high":
        score += 3
    elif mgmt == "medium":
        score += 1

    # 5. Legal activity
    legal = company.get("legal_issues", False)
    if legal:
        score += 2

    # 6. Tax debt
    tax = company.get("tax_debt", False)
    if tax:
        score += 2

    return score


# -------------------------------
# FINAL RISK SCORE
# -------------------------------

def final_risk_score(ubo_scores, company_score):
    """
    ubo_scores = list of integers
    company_score = integer
    """
    if not ubo_scores:
        highest_ubo = 0
    else:
        highest_ubo = max(ubo_scores)

    final = highest_ubo + company_score

    if final >= 7:
        level = "High Risk"
    elif final >= 4:
        level = "Medium Risk"
    else:
        level = "Low Risk"

    return {
        "final_score": final,
        "level": level,
        "ubo_score": highest_ubo,
        "company_score": company_score
    }
