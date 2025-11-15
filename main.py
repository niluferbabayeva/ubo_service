from __future__ import annotations
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import json
import os

app = FastAPI(
    title="KYC/AML UBO & Risk Engine API",
    description="Prototype backend for RegTech & Cybersecurity hackathon challenge",
    version="1.0.0",
)

# ============================================================
# 1) MOCK UNIFIED RISK DATABASE (PEP / SANCTIONS / ETC.)
# ============================================================

UNIFIED_RISK_DB = [
    {
        "name": "Li Wei",
        "dob": "1975-09-13",
        "nationality": "Chinese",
        "risk_types": ["PEP"],
        "sources": ["Mock_Global_PEP_List"],
    },
    {
        "name": "Maria Ivanova",
        "dob": "1988-03-10",
        "nationality": "Russian",
        "risk_types": ["Sanction"],
        "sources": ["Mock_EU_Sanctions_List"],
    },
    {
        "name": "Damir Beketov",
        "dob": "1969-11-30",
        "nationality": "Kazakh",
        "risk_types": ["PEP", "Sanction"],
        "sources": ["Mock_UN_List", "Mock_Global_PEP_List"],
    },
    {
        "name": "Giannis Christodoulou",
            "dob": "1971-09-01",
        "nationality": "Cypriot",
        "risk_types": ["AdverseMedia"],
        "sources": ["Mock_Corruption_Reports"],
    },
    {
        "name": "Unknown Client 42",
        "dob": "Unknown",
        "nationality": "Unknown",
        "risk_types": ["HighRiskJurisdiction"],
        "sources": ["Mock_FATF_List"],
    },
    {
        "name": "Aleksey Morozov",
        "dob": "1982-05-14",
        "nationality": "Russian",
        "risk_types": ["Sanction"],
        "sources": ["Mock_OFAC_List"],
    },
    {
        "name": "Jonathan Reed",
        "dob": "1968-07-29",
        "nationality": "American",
        "risk_types": ["PEP"],
        "sources": ["Mock_US_PEP_List"],
    },
]

RISK_DB_NAME_INDEX = {(p["name"].lower(), p["dob"]): p for p in UNIFIED_RISK_DB}

# ============================================================
# 2) DATA MODELS (Pydantic)
# ============================================================


class Shareholder(BaseModel):
    name: str
    type: str  # "company" or "individual"
    ownership_percentage: float = Field(..., ge=0, le=100)
    country: Optional[str] = None
    registration_number: Optional[str] = None
    nationality: Optional[str] = None
    dob: Optional[str] = None  # YYYY-MM-DD or "Unknown"
    sub_entity: Optional["Company"] = None  # recursive


class Company(BaseModel):
    company_name: str
    registration_number: str
    jurisdiction: Optional[str] = None
    industry: Optional[str] = None
    business_address: Optional[str] = None
    # use default_factory to avoid shared mutable default
    shareholders: List[Shareholder] = Field(default_factory=list)


Shareholder.update_forward_refs()


class AnalyzeCompanyRequest(BaseModel):
    company_name: str


class UBOOutput(BaseModel):
    name: str
    dob: Optional[str] = None
    nationality: Optional[str] = None
    ultimate_ownership_percentage: float
    risk_flags: Dict[str, int]


class OwnershipTreeNode(BaseModel):
    name: str
    type: str
    ownership_percentage: float
    children: List["OwnershipTreeNode"] = Field(default_factory=list)


OwnershipTreeNode.update_forward_refs()


class ScreeningOutput(BaseModel):
    pep: int
    sanction: int
    adverse_media: int
    high_risk_jurisdiction: int
    final_risk_level: str


class AnalyzeCompanyResponse(BaseModel):
    company_name: str
    registration_number: str
    jurisdiction: Optional[str]
    ubos: List[UBOOutput]
    ownership_tree: OwnershipTreeNode
    screening: ScreeningOutput


class UploadCompanyRequest(Company):
    """For simplicity, we reuse Company structure for uploaded data."""
    pass


class UploadCompanyResponse(BaseModel):
    message: str
    company_name: str
    registration_number: str


# ============================================================
# 3) MOCK COMPANY DATABASE + SIMPLE PERSISTENCE
# ============================================================

COMPANY_DB_FILE = "companies_db.json"


def load_companies_from_file() -> List[Dict[str, Any]]:
    if os.path.exists(COMPANY_DB_FILE):
        with open(COMPANY_DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    # If file doesn't exist yet, initialize with your two mock companies
    return [
        {
            "company_name": "Atlas Robotics Corporation",
            "registration_number": "US-5592001",
            "jurisdiction": "USA",
            "industry": "Robotics",
            "business_address": "Silicon Valley, California, USA",
            "shareholders": [
                {
                    "name": "Pacific Venture Group Ltd",
                    "type": "company",
                    "ownership_percentage": 55,
                    "country": "USA",
                    "registration_number": "US-1189221",
                    "sub_entity": {
                        "company_name": "Pacific Venture Group Ltd",
                        "registration_number": "US-1189221",
                        "jurisdiction": "USA",
                        "industry": "Investment",
                        "business_address": "Boston, MA",
                        "shareholders": [
                            {
                                "name": "Northern Equity Holdings GmbH",
                                "type": "company",
                                "ownership_percentage": 80,
                                "country": "Germany",
                                "registration_number": "DE-7721930",
                                "sub_entity": {
                                    "company_name": "Northern Equity Holdings GmbH",
                                    "registration_number": "DE-7721930",
                                    "jurisdiction": "Germany",
                                    "industry": "Holding",
                                    "business_address": "Berlin, Germany",
                                    "shareholders": [
                                        {
                                            "name": "Marcus Schneider",
                                            "type": "individual",
                                            "ownership_percentage": 100,
                                            "country": "Germany",
                                            "nationality": "German",
                                            "dob": "1979-03-02",
                                            "sub_entity": {},
                                        }
                                    ],
                                },
                            },
                            {
                                "name": "TechAngels LLC",
                                "type": "company",
                                "ownership_percentage": 20,
                                "country": "USA",
                                "registration_number": "US-9322112",
                                "sub_entity": {
                                    "company_name": "TechAngels LLC",
                                    "registration_number": "US-9322112",
                                    "jurisdiction": "USA",
                                    "industry": "Angel Investment",
                                    "business_address": "New York, USA",
                                    "shareholders": [
                                        {
                                            "name": "Sophia Martinez",
                                            "type": "individual",
                                            "ownership_percentage": 100,
                                            "country": "USA",
                                            "nationality": "American",
                                            "dob": "1990-08-17",
                                            "sub_entity": {},
                                        }
                                    ],
                                },
                            },
                        ],
                    },
                },
                {
                    "name": "FutureTech Innovators Inc",
                    "type": "company",
                    "ownership_percentage": 45,
                    "country": "Canada",
                    "registration_number": "CA-7720012",
                    "sub_entity": {
                        "company_name": "FutureTech Innovators Inc",
                        "registration_number": "CA-7720012",
                        "jurisdiction": "Canada",
                        "industry": "Technology",
                        "business_address": "Toronto, Canada",
                        "shareholders": [
                            {
                                "name": "Emily Roberts",
                                "type": "individual",
                                "ownership_percentage": 100,
                                "country": "Canada",
                                "nationality": "Canadian",
                                "dob": "1984-11-05",
                                "sub_entity": {},
                            }
                        ],
                    },
                },
            ],
        },
        {
            "company_name": "SilverTech Solutions Ltd",
            "registration_number": "UK-3289001",
            "jurisdiction": "United Kingdom",
            "industry": "Software Development",
            "business_address": "London, UK",
            "shareholders": [
                {
                    "name": "Emily Carter",
                    "type": "individual",
                    "ownership_percentage": 100,
                    "country": "United Kingdom",
                    "nationality": "British",
                    "dob": "1990-07-11",
                    "sub_entity": {},
                }
            ],
        },
    ]


def save_companies_to_file(companies: List[Dict[str, Any]]) -> None:
    with open(COMPANY_DB_FILE, "w", encoding="utf-8") as f:
        json.dump(companies, f, indent=2, ensure_ascii=False)


COMPANIES_DB: List[Dict[str, Any]] = load_companies_from_file()


def find_company_by_name(name: str) -> Optional[Dict[str, Any]]:
    for c in COMPANIES_DB:
        if c["company_name"].lower() == name.lower():
            return c
    return None


# ============================================================
# 3.5) CLEANER FOR INVALID SUB_ENTITIES
# ============================================================

def clean_sub_entities(data: Any) -> Any:
    """
    Recursively:
      - converts sub_entity: {} -> None
      - cleans nested shareholders / sub-entities
    so that Pydantic can parse into Company models without errors.
    """
    if isinstance(data, dict):
        # If this looks like a company (has shareholders), clean its shareholders
        if "shareholders" in data:
            data["shareholders"] = [
                clean_sub_entities(sh) for sh in data.get("shareholders", [])
            ]
        # Fix invalid or empty sub_entity
        if "sub_entity" in data:
            if not data["sub_entity"]:  # {} or None or empty
                data["sub_entity"] = None
            else:
                data["sub_entity"] = clean_sub_entities(data["sub_entity"])
    return data


# ============================================================
# 4) UBO DISCOVERY (RECURSIVE, 25% THRESHOLD)
# ============================================================

def compute_ubo_percentages(company: Company) -> List[Dict[str, Any]]:
    """
    Traverse the ownership tree and compute ultimate ownership % for individuals.
    UBO rule: individuals with >= 25% ultimate ownership.
    """

    ubos: Dict[str, Dict[str, Any]] = {}

    def traverse_shareholders(
        shareholders: List[Shareholder], parent_percentage: float
    ) -> None:
        for sh in shareholders:
            effective_pct = parent_percentage * sh.ownership_percentage / 100.0

            if sh.type.lower() == "individual":
                key = (sh.name, sh.dob)
                if key not in ubos:
                    ubos[key] = {
                        "name": sh.name,
                        "dob": sh.dob,
                        "nationality": sh.nationality,
                        "percentage": 0.0,
                    }
                ubos[key]["percentage"] += effective_pct

            elif sh.type.lower() == "company" and sh.sub_entity:
                # Recurse into the sub-entity shareholders
                if sh.sub_entity.shareholders:
                    traverse_shareholders(sh.sub_entity.shareholders, effective_pct)

            # If company has no sub_entity or empty -> no further info, stop there.

    traverse_shareholders(company.shareholders, parent_percentage=100.0)

    # Filter by 25% threshold (UBO definition)
    ubo_list: List[Dict[str, Any]] = []
    for (_, _), data in ubos.items():
        if data["percentage"] >= 25.0:
            ubo_list.append(data)

    return ubo_list


# ============================================================
# 5) OWNERSHIP TREE BUILDER (FOR FRONTEND)
# ============================================================

def build_ownership_tree(company: Company) -> OwnershipTreeNode:
    def build_node_from_company(
        comp: Company, ownership_pct: float = 100.0
    ) -> OwnershipTreeNode:
        node_children: List[OwnershipTreeNode] = []

        for sh in comp.shareholders:
            if sh.type.lower() == "individual":
                node_children.append(
                    OwnershipTreeNode(
                        name=sh.name,
                        type=sh.type,
                        ownership_percentage=sh.ownership_percentage,
                        children=[],
                    )
                )
            elif sh.type.lower() == "company" and sh.sub_entity:
                # Represent shareholder company as node, then go deeper
                child_company = sh.sub_entity
                child_node = build_node_from_company(
                    child_company,
                    ownership_pct=sh.ownership_percentage,
                )
                # Rename top-level name to shareholder name so it matches
                child_node.name = sh.name
                child_node.type = "company"
                child_node.ownership_percentage = sh.ownership_percentage
                node_children.append(child_node)
            else:
                # company but no extra info
                node_children.append(
                    OwnershipTreeNode(
                        name=sh.name,
                        type=sh.type,
                        ownership_percentage=sh.ownership_percentage,
                        children=[],
                    )
                )

        return OwnershipTreeNode(
            name=comp.company_name,
            type="company",
            ownership_percentage=ownership_pct,
            children=node_children,
        )

    return build_node_from_company(company)


# ============================================================
# 6) RISK SCREENING ENGINE
# ============================================================

def lookup_risk_profile(name: str, dob: Optional[str]) -> Dict[str, int]:
    """
    Look up a person in the unified risk database by (name, dob).
    Returns binary flags (0/1) for each risk type.
    """
    pep = sanction = adverse_media = high_risk_jurisdiction = 0

    key_exact = (name.lower(), dob) if dob else None
    profile = RISK_DB_NAME_INDEX.get(key_exact) if key_exact else None

    if profile:
        risk_types = profile.get("risk_types", [])
        if "PEP" in risk_types:
            pep = 1
        if "Sanction" in risk_types:
            sanction = 1
        if "AdverseMedia" in risk_types:
            adverse_media = 1
        if "HighRiskJurisdiction" in risk_types:
            high_risk_jurisdiction = 1

    return {
        "pep": pep,
        "sanction": sanction,
        "adverse_media": adverse_media,
        "high_risk_jurisdiction": high_risk_jurisdiction,
    }


def compute_final_risk_level(
    pep: int, sanction: int, adverse_media: int, high_risk_jurisdiction: int
) -> str:
    """
    Simple explainable rules:
      - Any sanction -> High
      - Any PEP or HighRiskJurisdiction -> Medium/High
      - Any adverse media -> Medium
      - Otherwise -> Low
    """
    if sanction == 1:
        return "High"
    if pep == 1 or high_risk_jurisdiction == 1:
        return "Medium"
    if adverse_media == 1:
        return "Medium"
    return "Low"


def compute_company_screening(ubos: List[UBOOutput]) -> ScreeningOutput:
    """Aggregate UBO risk into company-level risk."""
    pep = sanction = adverse_media = high_risk_jurisdiction = 0

    for ubo in ubos:
        pep = max(pep, ubo.risk_flags.get("pep", 0))
        sanction = max(sanction, ubo.risk_flags.get("sanction", 0))
        adverse_media = max(adverse_media, ubo.risk_flags.get("adverse_media", 0))
        high_risk_jurisdiction = max(
            high_risk_jurisdiction, ubo.risk_flags.get("high_risk_jurisdiction", 0)
        )

    final_level = compute_final_risk_level(
        pep, sanction, adverse_media, high_risk_jurisdiction
    )

    return ScreeningOutput(
        pep=pep,
        sanction=sanction,
        adverse_media=adverse_media,
        high_risk_jurisdiction=high_risk_jurisdiction,
        final_risk_level=final_level,
    )


# ============================================================
# 7) API ENDPOINTS
# ============================================================

@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/analyze_company", response_model=AnalyzeCompanyResponse)
def analyze_company(payload: AnalyzeCompanyRequest):
    """
    Main endpoint for the UI:
    1. Takes company_name.
    2. Looks up the company in DB.
    3. If not found -> 404 with message to upload docs.
    4. If found -> UBO discovery, risk screening, ownership tree.
    """

    raw_company = find_company_by_name(payload.company_name)
    if not raw_company:
        # This is what your UI will show as warning.
        raise HTTPException(
            status_code=404,
            detail="This company is not in the database. Please upload the necessary documents.",
        )

    # Clean invalid sub_entity={} etc. before parsing into Pydantic model
    cleaned = clean_sub_entities(raw_company)
    company = Company(**cleaned)

    # 1) UBO computation
    ubo_raw_list = compute_ubo_percentages(company)

    ubos_output: List[UBOOutput] = []
    for u in ubo_raw_list:
        risk_flags = lookup_risk_profile(u["name"], u["dob"])
        ubos_output.append(
            UBOOutput(
                name=u["name"],
                dob=u["dob"],
                nationality=u["nationality"],
                ultimate_ownership_percentage=round(u["percentage"], 2),
                risk_flags=risk_flags,
            )
        )

    # 2) Company-level screening
    screening = compute_company_screening(ubos_output)

    # 3) Ownership tree for frontend
    ownership_tree = build_ownership_tree(company)

    return AnalyzeCompanyResponse(
        company_name=company.company_name,
        registration_number=company.registration_number,
        jurisdiction=company.jurisdiction,
        ubos=ubos_output,
        ownership_tree=ownership_tree,
        screening=screening,
    )


@app.post("/upload_company", response_model=UploadCompanyResponse)
def upload_company(company: UploadCompanyRequest):
    """
    Endpoint for when the user uploads new documents.
    In real life: PDF -> OCR -> JSON -> call this endpoint with the JSON.
    For now: we assume frontend sends JSON in the same structure as Company.
    """

    # Check if company already exists by name (prototype assumption)
    existing = find_company_by_name(company.company_name)
    if existing:
        # Simple overwrite logic (you can change to versioning if you want)
        for i, c in enumerate(COMPANIES_DB):
            if c["company_name"].lower() == company.company_name.lower():
                COMPANIES_DB[i] = company.dict()
                save_companies_to_file(COMPANIES_DB)
                return UploadCompanyResponse(
                    message="Company updated successfully.",
                    company_name=company.company_name,
                    registration_number=company.registration_number,
                )

    # If new, append
    COMPANIES_DB.append(company.dict())
    save_companies_to_file(COMPANIES_DB)

    return UploadCompanyResponse(
        message="Company created successfully.",
        company_name=company.company_name,
        registration_number=company.registration_number,
    )
