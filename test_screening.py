from services.screening import load_screening_list, check_screening

# 1. Load screening CSV
db = load_screening_list("data/sanctions_pep_mock.csv")

# 2. Test names
names = ["Marcus Schneider", "Sophia Martinez", "Emily Roberts", "Random Person"]

print("\n=== STEP 3 TEST RESULTS ===\n")

for n in names:
    flags = check_screening(n, db)
    print(f"{n:<18} →  PEP={flags['pep']}  |  Sanctioned={flags['sanctioned']}")
