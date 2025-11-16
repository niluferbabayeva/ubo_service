import csv

def load_screening_list(path):
    db = {}
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            db[row["name"]] = {
                "pep": row["is_pep"] == "1",
                "sanctioned": row["is_sanctioned"] == "1"
            }
    return db


def check_screening(name, db):
    if name in db:
        return db[name]
    return {"pep": False, "sanctioned": False}
