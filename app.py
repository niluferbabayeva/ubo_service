import json
import requests
import streamlit as st

# ----------------------------
# CONFIG
# ----------------------------
API_ANALYZE_URL = "http://127.0.0.1:8000/analyze_company"
API_UPLOAD_URL = "http://127.0.0.1:8000/upload_company"

st.set_page_config(
    page_title="UBO Risk Scanner",
    page_icon="🧭",
    layout="centered",
)

# ----------------------------
# GLOBAL STYLING (Premium White)
# ----------------------------
st.markdown(
    """
<style>
/* Page background */
body {
    background: radial-gradient(circle at top, #f3f6ff 0%, #ffffff 55%, #ffffff 100%);
}

/* Center content and limit width */
.block-container {
    max-width: 950px;
    margin: 0 auto;
    padding-top: 2rem;
    padding-bottom: 3rem;
    font-family: "Inter", system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

/* Main heading area */
.main-header {
    text-align: center;
    margin-bottom: 2.5rem;
}
.main-header h1 {
    font-weight: 700;
    letter-spacing: 0.04em;
    margin-bottom: 0.5rem;
}
.main-header p {
    color: #4b5563;
    font-size: 0.98rem;
}

/* Top search card */
.search-card {
    background: #ffffff;
    padding: 1.3rem 1.5rem;
    border-radius: 18px;
    box-shadow: 0 10px 30px rgba(15, 23, 42, 0.12);
    margin-bottom: 1.5rem;
}

/* Upload button wrapper (right side) */
.upload-wrap {
    text-align: right;
    margin-bottom: 0.8rem;
}
.upload-label {
    font-size: 0.85rem;
    color: #6b7280;
    margin-bottom: 0.25rem;
}

/* Section titles */
.section-title {
    font-size: 1.25rem;
    font-weight: 650;
    margin-top: 1.5rem;
    margin-bottom: 0.4rem;
}
.section-rule {
    height: 3px;
    border-radius: 999px;
    background: linear-gradient(90deg, #2563eb, #a855f7);
    margin-bottom: 0.9rem;
}

/* Card containers */
.ubo-card, .generic-card {
    background: #ffffff;
    border-radius: 16px;
    padding: 1.1rem 1.3rem;
    box-shadow: 0 4px 16px rgba(15, 23, 42, 0.08);
    margin-bottom: 0.9rem;
}

/* Ownership tree card */
.tree-card {
    background: #ffffff;
    border-radius: 16px;
    padding: 1rem 1.2rem;
    box-shadow: 0 4px 16px rgba(15, 23, 42, 0.08);
    margin-bottom: 1.3rem;
}

/* Ownership tree lines */
.tree-line {
    font-size: 0.95rem;
    margin: 0.15rem 0;
}

/* Risk badge */
.risk-badge {
    display: inline-flex;
    align-items: center;
    padding: 0.25rem 0.7rem;
    border-radius: 999px;
    font-size: 0.9rem;
    font-weight: 600;
}
.risk-low {
    background: #ecfdf3;
    color: #15803d;
}
.risk-medium {
    background: #fef9c3;
    color: #854d0e;
}
.risk-high {
    background: #fee2e2;
    color: #b91c1c;
}
</style>
""",
    unsafe_allow_html=True,
)

# ----------------------------
# HEADER
# ----------------------------
st.markdown(
    """
<div class="main-header">
  <h1>UBO RISK SCANNER</h1>
  <p>Search company owners, analyze UBO structures, and generate AML risk insights automatically.</p>
</div>
""",
    unsafe_allow_html=True,
)

# ----------------------------
# UPLOAD FILES (JSON -> /upload_company)
# ----------------------------
with st.container():
    st.markdown('<div class="upload-wrap">', unsafe_allow_html=True)
    st.markdown('<div class="upload-label">Upload new company JSON</div>', unsafe_allow_html=True)
   # Upload JSON (right aligned)
    upload_col1, upload_col2 = st.columns([5, 2])
    with upload_col2:
        st.markdown('<div class="upload-label">Upload new company JSON</div>', unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            type=["json"],
            label="Choose file",
            label_visibility="collapsed",
    )

    st.markdown("</div>", unsafe_allow_html=True)

if uploaded_file is not None:
    try:
        payload = json.load(uploaded_file)
        res = requests.post(API_UPLOAD_URL, json=payload)
        if res.status_code == 200:
            rj = res.json()
            st.success(f"✅ {rj.get('message','Company uploaded successfully.')}")
        else:
            st.error(f"❌ Upload failed (status {res.status_code}).")
    except Exception as e:
        st.error(f"Invalid JSON file: {e}")

# ----------------------------
# SEARCH CARD (single REAL input!)
# ----------------------------
# st.markdown('<div class="search-card">', unsafe_allow_html=True)
search_cols = st.columns([4, 1])

with search_cols[0]:
    company_name = st.text_input(
        label="Enter company name...",
        value="",
        placeholder="Enter company name...",
    )

with search_cols[1]:
    analyze_clicked = st.button("Analyze", use_container_width=True)

st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------
# ANALYZE FLOW
# ----------------------------
if analyze_clicked:

    if not company_name.strip():
        st.warning("Please enter a company name.")
    else:
        with st.spinner("Analyzing company structure and AML risk..."):
            try:
                resp = requests.post(API_ANALYZE_URL, json={"company_name": company_name})
            except Exception as e:
                st.error(f"Could not reach backend: {e}")
                st.stop()

        if resp.status_code == 404:
            # Company not in DB
            st.error(
                "⚠️ No results found for this company name. "
                "Please upload the necessary documents using the JSON uploader above."
            )
            st.stop()
        elif resp.status_code != 200:
            st.error(f"Unexpected error (status {resp.status_code}).")
            st.json(resp.json())
            st.stop()

        data = resp.json()
        st.success(f"Analysis complete for **{data['company_name']}**")

        ubos = data.get("ubos", [])
        tree = data.get("ownership_tree")
        screening = data.get("screening", {})

        # ============================
        # 1) UBO SECTION
        # ============================
        st.markdown('<div class="section-title">Ultimate Beneficial Owners (UBOs)</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-rule"></div>', unsafe_allow_html=True)

        if not ubos:
            st.info("No UBOs identified above the threshold (25%).")
        else:
            for u in ubos:
                st.markdown(
                    f"""
<div class="ubo-card">
  <div style="font-size:1.05rem; font-weight:600; margin-bottom:0.3rem;">{u['name']}</div>
  <div style="color:#4b5563; font-size:0.95rem;">
    <div><b>Nationality:</b> {u.get('nationality','-')}</div>
    <div><b>Date of Birth:</b> {u.get('dob','-')}</div>
    <div><b>Ultimate Ownership:</b> {u['ultimate_ownership_percentage']}%</div>
    <div style="margin-top:0.4rem;"><b>Risk Flags:</b></div>
    <ul style="margin-top:0.2rem; margin-bottom:0;">
      <li>PEP: {u['risk_flags'].get('pep',0)}</li>
      <li>Sanction: {u['risk_flags'].get('sanction',0)}</li>
      <li>Adverse Media: {u['risk_flags'].get('adverse_media',0)}</li>
      <li>High Risk Jurisdiction: {u['risk_flags'].get('high_risk_jurisdiction',0)}</li>
    </ul>
  </div>
</div>
""",
                    unsafe_allow_html=True,
                )

        # ============================
        # 2) OWNERSHIP TREE
        # ============================
        st.markdown('<div class="section-title">Ownership Structure Tree</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-rule" style="background:linear-gradient(90deg,#a855f7,#6366f1);"></div>', unsafe_allow_html=True)

        def render_tree(node: dict, level: int = 0):
            indent_px = 18 * level
            icon = "🏢" if node.get("type") == "company" else "👤"
            name = node.get("name", "-")
            pct = node.get("ownership_percentage", 0)
            st.markdown(
                f"""
<div class="tree-line" style="margin-left:{indent_px}px;">
  {icon} <b>{name}</b> <span style="color:#6b7280;">({pct:.1f}%)</span>
</div>
""",
                unsafe_allow_html=True,
            )
            for child in node.get("children", []):
                render_tree(child, level + 1)

        if tree:
            st.markdown('<div class="tree-card">', unsafe_allow_html=True)
            render_tree(tree, level=0)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No ownership structure available for this company.")

        # ============================
        # 3) AML SCREENING RESULT
        # ============================
        st.markdown('<div class="section-title">AML Screening Result</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-rule" style="background:linear-gradient(90deg,#22c55e,#16a34a);"></div>', unsafe_allow_html=True)

        pep = screening.get("pep", 0)
        sanction = screening.get("sanction", 0)
        adverse = screening.get("adverse_media", 0)
        high_j = screening.get("high_risk_jurisdiction", 0)
        final = screening.get("final_risk_level", "Unknown")

        # Decide badge color
        risk_class = "risk-low"
        if str(final).lower() == "high":
            risk_class = "risk-high"
        elif str(final).lower() == "medium":
            risk_class = "risk-medium"

        st.markdown(
            f"""
<div class="generic-card">
  <div style="font-size:0.98rem; color:#4b5563;">
    <div><b>PEP:</b> {pep}</div>
    <div><b>Sanction:</b> {sanction}</div>
    <div><b>Adverse Media:</b> {adverse}</div>
    <div><b>High Risk Jurisdiction:</b> {high_j}</div>
  </div>
  <div style="margin-top:0.7rem;">
    <span class="risk-badge {risk_class}">
      Final Risk Level: {final}
    </span>
  </div>
</div>
""",
            unsafe_allow_html=True,
        )
