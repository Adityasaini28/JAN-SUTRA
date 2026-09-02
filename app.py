from pathlib import Path

import os
import streamlit as st
import pandas as pd
import plotly.express as px

from src.data_generator import generate
from src.data_pipeline import DataCleaningPipeline
from src.analytics import TrendAnalyzer, EvidenceEngine, PriorityScorer
from src.governance import driver_tree, intervention
from src.briefing import build_pdf


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="JAN SUTRA | Governance Decision Intelligence",
    page_icon="🧭",
    layout="wide",
)


# ============================================================
# CONSTANTS
# ============================================================

APP_TITLE = "JAN SUTRA"
APP_SUBTITLE = (
    "Citizen Signal → Evidence → Hypothesis → Field Validation → Governance Action"
)

DATA_DIR = Path("data")
OUTPUT_DIR = Path("outputs")


# ============================================================
# DATA LOADING
# ============================================================

@st.cache_data
def load_project_data():

    raw_feedback, indicators = generate(
        output_dir=str(DATA_DIR),
        n_records=12500,
    )

    valid_districts = indicators["district"].tolist()

    cleaned_feedback, audit = DataCleaningPipeline(
        raw_feedback,
        valid_districts,
    ).run()

    global_priorities = PriorityScorer.score_all(
        cleaned_feedback,
        indicators,
    )

    return (
        cleaned_feedback,
        indicators,
        audit,
        global_priorities,
    )


df, indicators, audit, global_priorities = load_project_data()


# ============================================================
# HEADER
# ============================================================

st.title(APP_TITLE)

st.caption(APP_SUBTITLE)

st.info(
    "Demo note: the underlying dataset is synthetic. "
    "The platform demonstrates a governance-analysis method; "
    "it does not make claims about real citizens, districts, "
    "elections, or public-service performance."
)


# ============================================================
# SIDEBAR — ANALYSIS CONTROLS
# ============================================================

with st.sidebar:

    st.header("Analysis Controls")

    if st.button("Reset analysis"):
        st.session_state.clear()
        st.rerun()

    states = ["All States"] + sorted(
        df["state"].dropna().unique().tolist()
    )

    state = st.selectbox(
        "State",
        states,
    )

    if state == "All States":
        state_df = df.copy()
    else:
        state_df = df[df["state"] == state].copy()

    districts = ["All Districts"] + sorted(
        state_df["district"].dropna().unique().tolist()
    )

    district = st.selectbox(
        "District",
        districts,
    )

    issues = sorted(
        df["issue_category"].dropna().unique().tolist()
    )

    default_issue = (
        "Public Transport"
        if "Public Transport" in issues
        else issues[0]
    )

    issue = st.selectbox(
        "Issue",
        issues,
        index=issues.index(default_issue),
    )

    st.divider()

    st.caption(
        "Use the controls to move from a broad governance signal "
        "to a specific district-level hypothesis."
    )


# ============================================================
# ANALYSIS SCOPE
# ============================================================

scope = df.copy()

if state != "All States":
    scope = scope[scope["state"] == state].copy()

if district != "All Districts":
    scope = scope[scope["district"] == district].copy()

issue_scope = scope[
    scope["issue_category"] == issue
].copy()


# ============================================================
# BASIC DATA VALIDATION
# ============================================================

if issue_scope.empty:

    st.error(
        "There is insufficient data for the selected "
        "state, district and issue combination."
    )

    st.stop()


# ============================================================
# TREND ANALYSIS
# ============================================================

trend_analyzer = TrendAnalyzer(df)

trend = trend_analyzer.metrics(
    issue,
    None if district == "All Districts" else district,
)

trend_series = trend_analyzer.monthly(
    issue,
    None if district == "All Districts" else district,
)


# ============================================================
# DISTRICT / GLOBAL PRIORITY
# ============================================================

if district == "All Districts":

    priority_row = global_priorities[
        global_priorities["issue_category"] == issue
    ]

    if priority_row.empty:
        st.error("Priority score could not be calculated.")
        st.stop()

    priority_row = priority_row.iloc[0]

else:

    district_priorities = PriorityScorer.score_all(
        issue_scope,
        indicators,
    )

    priority_row = district_priorities[
        district_priorities["issue_category"] == issue
    ]

    if priority_row.empty:
        st.error("District priority score could not be calculated.")
        st.stop()

    priority_row = priority_row.iloc[0]


# ============================================================
# SECTION 1 — EXECUTIVE DIAGNOSIS
# ============================================================

st.markdown("## 1. Executive Diagnosis")

negative_share = (
    issue_scope["sentiment"].eq("Negative").mean() * 100
)

feedback_volume = len(issue_scope)

avg_satisfaction = (
    issue_scope["satisfaction_score"].mean()
)

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Negative sentiment",
    f"{negative_share:.1f}%",
)

c2.metric(
    "Feedback volume",
    f"{feedback_volume:,}",
)

c3.metric(
    "Priority score",
    f"{float(priority_row['priority_score']):.1f}/100",
)

c4.metric(
    "Avg. satisfaction",
    f"{avg_satisfaction:.2f}/5",
)


scope_label = (
    "All districts"
    if district == "All Districts"
    else district
)

st.info(
    f"**Scope:** {scope_label} | "
    f"**Issue:** {issue} | "
    f"**Trend status:** {trend.get('status', 'Unavailable')} | "
    f"**Evidence standard:** directional, not causal."
)


# ============================================================
# SECTION 2 — WHAT CHANGED?
# ============================================================

st.markdown("## 2. What Changed?")

if trend_series.empty:

    st.warning(
        "Insufficient historical observations to establish a trend."
    )

else:

    fig = px.line(
        trend_series,
        x="month",
        y="negative_pct",
        markers=True,
        labels={
            "negative_pct": "Negative sentiment (%)",
            "month": "Month",
        },
        title=f"{issue} — negative sentiment over time",
    )

    st.plotly_chart(
        fig,
        width="stretch",
    )

    m1, m2, m3, m4 = st.columns(4)

    m1.metric(
        "Current",
        f"{trend.get('current_neg_pct', 0):.1f}%",
    )

    m2.metric(
        "Previous",
        f"{trend.get('previous_neg_pct', 0):.1f}%",
    )

    m3.metric(
        "Movement",
        f"{trend.get('delta_pp', 0):+.1f} pp",
    )

    m4.metric(
        "Z-score",
        f"{trend.get('z_score', 0):.2f}",
    )

    st.caption(
        "The trend detector compares the latest observation "
        "with historical observations. It flags unusual movement; "
        "it does not establish why the movement occurred."
    )


# ============================================================
# SECTION 3 — WHY MIGHT IT BE HAPPENING?
# ============================================================

st.markdown("## 3. Why Might It Be Happening?")

left, right = st.columns(2)


# ------------------------------------------------------------
# MECE TREE
# ------------------------------------------------------------

with left:

    st.subheader("MECE driver tree")

    tree = driver_tree(issue)

    st.markdown(
        f"**Root problem:** {tree['root']}"
    )

    for branch, subdrivers in tree["branches"].items():

        with st.expander(
            branch,
            expanded=True,
        ):

            for subdriver in subdrivers:
                st.write(
                    f"• {subdriver}"
                )

    st.caption(
        "The driver tree is an analyst-designed MECE structure "
        "used to organize investigation. It is not a causal model."
    )


# ------------------------------------------------------------
# EVIDENCE
# ------------------------------------------------------------

with right:

    st.subheader("Evidence & competing hypotheses")

    evidence_engine = EvidenceEngine(
        df,
        indicators,
    )

    evidence = evidence_engine.evaluate(issue)

    if not evidence:

        st.warning(
            "No sufficiently supported evidence is available "
            "for this issue."
        )

    else:

        for item in evidence:

            evidence_type = item.get(
                "evidence_type",
                "Evidence",
            )

            interpretation = item.get(
                "interpretation",
                "",
            )

            status = item.get(
                "status",
                "Unknown",
            )

            st.markdown(
                f"**{evidence_type}**"
            )

            st.write(
                interpretation
            )

            st.caption(
                f"Status: {status}"
            )

            st.divider()


# ============================================================
# SECTION 4 — COMPETING HYPOTHESES
# ============================================================

st.markdown("## 4. Competing Hypotheses")

negative_feedback = issue_scope[
    issue_scope["sentiment"] == "Negative"
].copy()

if negative_feedback.empty:

    st.warning(
        "No negative feedback is available to formulate "
        "operational hypotheses."
    )

else:

    top_drivers = (
        negative_feedback["service_type"]
        .value_counts(normalize=True)
        .mul(100)
        .head(3)
    )

    hypotheses = []

    for driver_name, share in top_drivers.items():

        hypotheses.append(
            {
                "Hypothesis": (
                    f"Dissatisfaction is concentrated around "
                    f"{driver_name}."
                ),
                "Signal": f"{share:.1f}% of negative feedback",
                "Next test": (
                    "Verify the operational condition using "
                    "administrative records and targeted field checks."
                ),
            }
        )

    hypothesis_df = pd.DataFrame(hypotheses)

    st.dataframe(
        hypothesis_df,
        width="stretch",
        hide_index=True,
    )

    st.caption(
        "These are hypotheses generated from observed complaint "
        "concentration. They require external operational validation."
    )


# ============================================================
# SECTION 5 — PRIORITY DECOMPOSITION
# ============================================================

st.markdown("## 5. Governance Priority Decomposition")

component_names = {
    "prevalence": "Complaint prevalence",
    "negative_sentiment": "Negative sentiment",
    "trend": "Recent movement",
    "exposure": "Population exposure",
    "evidence": "Evidence strength",
}

component_rows = []

for key, label in component_names.items():

    value = float(priority_row[key])

    component_rows.append(
        {
            "Component": label,
            "Score": round(value, 1),
        }
    )

component_rows.append(
    {
        "Component": "Final priority",
        "Score": round(
            float(priority_row["priority_score"]),
            1,
        ),
    }
)

priority_display = pd.DataFrame(
    component_rows
)

priority_display["Score"] = pd.to_numeric(
    priority_display["Score"],
    errors="coerce",
).astype(float)

st.dataframe(
    priority_display,
    width="stretch",
    hide_index=True,
)

st.caption(
    "The priority score is a transparent decision aid, not a "
    "forecast of electoral or political outcomes."
)


# ============================================================
# SECTION 6 — ACTION PLAN
# ============================================================

st.markdown(
    "## 6. Action Plan — Validate Before Execution"
)

action = intervention(issue)

a1, a2, a3 = st.columns(3)

with a1:

    st.subheader("Lever")

    st.write(
        action["lever"]
    )

with a2:

    st.subheader("Proposed action")

    st.write(
        action["action"]
    )

with a3:

    st.subheader("Accountable owner")

    st.write(
        action["owner"]
    )

st.warning(
    f"**Validation data:** {action['validation_data']}\n\n"
    f"**Success metric:** {action['success_metric']}"
)


# ============================================================
# SECTION 7 — FIELD VERIFICATION
# ============================================================

st.markdown(
    "## 7. Field Verification Plan"
)

field_plan = [
    "Sample locations contributing disproportionately to the signal.",
    "Verify the reported service condition on the ground.",
    "Cross-check citizen reports against administrative records.",
    "Look explicitly for contradictory evidence.",
    "Document the evidence required before intervention.",
]

for step in field_plan:

    st.write(
        f"☐ {step}"
    )

st.info(
    "Decision rule: if field evidence contradicts the leading "
    "hypothesis, revise the hypothesis rather than forcing the "
    "data to support the proposed intervention."
)


# ============================================================
# SECTION 8 — DATA QUALITY
# ============================================================

st.markdown(
    "## 8. Data Quality Audit"
)

audit_rows = []

for metric, value in audit.items():

    audit_rows.append(
        {
            "Metric": metric.replace("_", " ").title(),
            "Value": value,
        }
    )

audit_df = pd.DataFrame(
    audit_rows
)

st.dataframe(
    audit_df,
    width="stretch",
    hide_index=True,
)


# ============================================================
# SECTION 9 — EXECUTIVE BRIEF
# ============================================================

st.markdown(
    "## 9. Executive Brief"
)

if st.button(
    "Generate Executive Brief",
    type="primary",
):

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    safe_district = (
        district
        .replace(" ", "_")
        .replace("/", "_")
    )

    safe_issue = (
        issue
        .replace(" ", "_")
        .replace("/", "_")
    )

    pdf_path = (
        OUTPUT_DIR
        / f"JAN_SUTRA_{safe_district}_{safe_issue}.pdf"
    )

    build_pdf(
        str(pdf_path),
        district,
        issue,
        trend,
        evidence,
        float(priority_row["priority_score"]),
        action,
    )

    if pdf_path.exists():

        with open(
            pdf_path,
            "rb",
        ) as file:

            st.download_button(
                label="Download Executive Brief",
                data=file.read(),
                file_name=pdf_path.name,
                mime="application/pdf",
            )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "JAN SUTRA | Synthetic-data governance decision-intelligence prototype | "
    "Correlation ≠ causation | Field validation required"
)