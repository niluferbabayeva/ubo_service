import streamlit as st
import requests
import json
import plotly.express as px
import pandas as pd

# ---------------------------------------------------------
# CONFIG
# ---------------------------------------------------------
st.set_page_config(page_title="UBO Vision", layout="wide")

BACKEND_URL = "http://127.0.0.1:8000/analyze_company"

st.title("UBO Vision – Automated Corporate KYC / AML Analysis")

st.markdown("""
Upload a structured company JSON and run a full UBO + AML screening analysis.
""")

st.markdown("---")

# ---------------------------------------------------------
# SMALL HELPER
# ---------------------------------------------------------
def extract_shareholders(entity: dict):
    """
    Flatten only the top-level shareholders from the original JSON
    for a simple ownership pie chart.
    """
    data = []
    for sh in entity.get("shareholders", []):
        if "ownership_percentage" in sh:
            data.append(
                {
                    "name": sh.get("name", "Unknown"),
                    "percentage": sh["ownership_percentage"],
                }
            )
    return data


# ---------------------------------------------------------
# SEARCH BAR
# ---------------------------------------------------------
st.header("1. Company Search")

company_name = st.text_input(
    "Enter the company name (optional, used for display only)…",
    placeholder="e.g., Atlas Robotics Corporation",
)

uploaded_json = st.file_uploader(
    "Upload Company JSON File",
    type=["json"],
)

analyze_btn = st.button("Analyze Company")

# ---------------------------------------------------------
# ANALYSIS LOGIC
# ---------------------------------------------------------
if analyze_btn:

    # 1) Basic validation
    if not uploaded_json:
        st.error("Please upload a JSON file first.")
        st.stop()

    # 2) Parse raw JSON
    try:
        raw_company = json.load(uploaded_json)
    except Exception:
        st.error("Invalid JSON file. Please upload a valid structured JSON.")
        st.stop()

    # 3) Call backend
    try:
        response = requests.post(BACKEND_URL, json=raw_company)
    except Exception as e:
        st.error(f"Backend not reachable: {e}")
        st.stop()

    if response.status_code != 200:
        try:
            err = response.json()
        except Exception:
            err = {"detail": response.text}
        st.error(f"Backend error ({response.status_code}): {err}")
        st.stop()

    result = response.json()

    # Use typed name if provided, otherwise backend company_name
    display_name = company_name or result.get("company_name", "Uploaded company")

    st.success(f"Analysis completed for **{display_name}**")
    st.markdown("---")

    # ---------------------------------------------------------
    # OWNERSHIP PATHS (FROM BACKEND)
    # ---------------------------------------------------------
    st.subheader("Ownership Structure (Paths)")

    paths = result.get("ownership_paths", [])

    if not paths:
        st.info("No ownership paths were detected.")
    else:
        for path in paths:
            st.code(" → ".join(path))

    st.markdown(f"**Ownership Layers:** {result.get('ownership_layers', 'N/A')}")
    st.markdown("---")

    # ---------------------------------------------------------
    # SHAREHOLDER OWNERSHIP PIE (FROM ORIGINAL JSON)
    # ---------------------------------------------------------
    share_data = extract_shareholders(raw_company)
    df_share = pd.DataFrame(share_data)

    if not df_share.empty:
        st.subheader("Shareholder Ownership Breakdown")
        fig_share = px.pie(
            df_share,
            values="percentage",
            names="name",
            title="Shareholder Ownership Breakdown",
            hole=0.45,
        )
        st.plotly_chart(fig_share, use_container_width=True)
        st.markdown("---")

    # ---------------------------------------------------------
    # UBOs
    # ---------------------------------------------------------
    st.subheader("Identified UBOs")

    ubos = result.get("ubos", [])

    if not ubos:
        st.info("No UBOs were identified for this company.")
    else:
        cols = st.columns(len(ubos))
        for idx, u in enumerate(ubos):
            with cols[idx]:
                st.markdown(
                    f"""
                    ### {u['name']}
                    - **PEP:** {"🟡 Yes" if u['pep'] else "No"}
                    - **Sanctioned:** {"🔴 Yes" if u['sanctioned'] else "No"}
                    - **Risk Score:** **{u['risk_score']}**
                    """
                )

    st.markdown("---")

    # ---------------------------------------------------------
    # RISK VISUALIZATIONS
    # ---------------------------------------------------------
    st.subheader("Risk Contribution Overview")

    if ubos:
        # Bar chart: individual UBO risk scores
        names = [u["name"] for u in ubos]
        scores = [u["risk_score"] for u in ubos]

        fig_bar = px.bar(
            x=names,
            y=scores,
            labels={"x": "UBO", "y": "Risk Score"},
            title="Individual UBO Risk Contribution",
        )
        st.plotly_chart(fig_bar, use_container_width=True)

        # Donut chart: PEP / Sanctioned / Clean
        pep_count = len([u for u in ubos if u["pep"]])
        sanc_count = len([u for u in ubos if u["sanctioned"]])
        clean_count = len(ubos) - pep_count - sanc_count

        donut_fig = px.pie(
            names=["PEP", "Sanctioned", "Clean"],
            values=[pep_count, sanc_count, clean_count],
            hole=0.5,
            title="UBO Screening Breakdown",
        )
        st.plotly_chart(donut_fig, use_container_width=True)

    st.markdown("---")

    # ---------------------------------------------------------
    # FINAL RISK RATING + EXPLANATION
    # ---------------------------------------------------------
    st.subheader("Final AML Risk Rating")

    final = result.get("final_risk")

    if isinstance(final, dict):
        level = final.get("level", "Unknown")
        total_score = final.get("final_score", 0)
        ubo_score = final.get("ubo_score", 0)
        company_score = final.get("company_score", 0)

        risk_color = {
            "Low Risk": "🟩",
            "Medium Risk": "🟧",
            "High Risk": "🟥",
        }.get(level, "⬜️")

        st.markdown(f"### {risk_color} **Final AML Risk Rating: {level}**")

        col1, col2, col3 = st.columns(3)
        col1.metric("Final Score", total_score)
        col2.metric("UBO Score", ubo_score)
        col3.metric("Company Score", company_score)

        # Friendly explanation box
        st.markdown("#### How this rating was calculated")

        st.markdown(
            f"""
- **Total risk score:** **{total_score}** points  
- **UBO-related risk:** **{ubo_score}** points  
- **Company-related risk:** **{company_score}** points  

Where:
- UBO score reflects **PEP status** and **sanctions hits** for the identified UBOs.  
- Company score reflects factors like **tax debt**, **ongoing legal cases**, and **ownership complexity** (number of layers).  
            """
        )

        # Band explanation
        if level == "Low Risk":
            st.info("0–3 points → Low Risk: standard onboarding is usually sufficient.")
        elif level == "Medium Risk":
            st.warning(
                "4–7 points → Medium Risk: additional documents / enhanced review recommended."
            )
        elif level == "High Risk":
            st.error(
                "8+ points → High Risk: enhanced due diligence required before onboarding."
            )
    else:
        st.error("Backend did not return a structured final_risk object.")
