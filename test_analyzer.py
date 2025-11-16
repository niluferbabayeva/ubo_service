import json
from services.analyzer import analyze_company
from services.screening import load_screening_list

# 1. Load screening DB
screening_db = load_screening_list("data/sanctions_pep_mock.csv")

# 2. Load sample company JSON
with open("data/sample_company.json", "r", encoding="utf-8") as f:
    sample_company = json.load(f)

# 3. Run full analysis
result = analyze_company(sample_company, screening_db)

# 4. Pretty print result
print(json.dumps(result, indent=2, ensure_ascii=False))
