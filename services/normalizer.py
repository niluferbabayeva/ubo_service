def normalize_company(raw):
    """Unifies key names from partner APIs into one standard structure."""
    return {
        "name": raw.get("company_name") or raw.get("name"),
        "voen": raw.get("voen"),
        "tax_debt": raw.get("tax_debt", False),
        "legal_cases": raw.get("legal_cases", []),
        "vendors": raw.get("vendors", []),
        "shareholders": normalize_shareholders(raw.get("shareholders", [])),
    }


def normalize_shareholders(sh_list):
    normalized = []
    for sh in sh_list:
        normalized.append({
            "name": sh.get("name"),
            "type": sh.get("type"),     # "individual" or "company"
            "percentage": sh.get("percentage"),
            "country": sh.get("country"),
            "sub_entity": sh.get("sub_entity")  # may be None or a nested company object
        })
    return normalized
