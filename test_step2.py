import json
from services.ubo_finder import find_ubos

# Load test company JSON
with open("data/sample_company.json", "r") as f:
    company = json.load(f)

ubos, paths, layers = find_ubos(company)

print("\n=== STEP 2 TEST RESULTS ===\n")

print("UBOs Found:")
print(ubos)

print("\nOwnership Paths:")
for p in paths:
    print(" -> ".join(p))

print(f"\nTotal Ownership Layers: {layers}")
