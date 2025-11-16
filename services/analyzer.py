# services/analyzer.py

from services.normalizer import normalize_company
from services.ubo_finder import find_ubos
from services.screening import check_screening
from services.risk_engine import score_ubo, score_company, final_risk_score

def analyze(raw_company, screening_db):
    """
    Main analysis pipeline.
    """

    # 1) Normalize
    company = normalize_company(raw_company)

    # 2) UBO discovery
    ubos, paths, layers = find_ubos(company)

    # 3) Screen + score each UBO
    ubo_details = []
    ubo_scores = []

    for u in ubos:
        flags = check_screening(u, screening_db)
        score = score_ubo(flags)
        ubo_scores.append(score)

        ubo_details.append({
            "name": u,
            "pep": flags["pep"],
            "sanctioned": flags["sanctioned"],
            "risk_score": score
        })

    # 4) Company-level scoring
    company_score = score_company(company)

    # 5) Final risk
    final_risk = final_risk_score(ubo_scores, company_score)

    return {
        "company_name": company["name"],
        "ubos": ubo_details,
        "company_score": company_score,
        "final_risk": final_risk,
        "ownership_paths": paths,
        "ownership_layers": layers
    }
