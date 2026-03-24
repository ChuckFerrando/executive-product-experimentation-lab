import os
import sys
from pathlib import Path
from typing import Dict

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from shared.llm_client import generate_text  # noqa: E402

load_dotenv()

st.set_page_config(page_title="AI Product Decision Assistant", layout="wide")

WEIGHTS = {
    "strategic_alignment": 0.22,
    "customer_impact": 0.22,
    "revenue_potential": 0.15,
    "confidence": 0.12,
    "effort": -0.12,  # lower effort is better
    "risk": -0.10,    # lower risk is better
    "time_criticality": 0.11,
}


def normalize_score(value: int) -> int:
    return max(1, min(5, int(value)))


def score_option(option: Dict[str, int]) -> float:
    total = 0.0
    for key, weight in WEIGHTS.items():
        total += normalize_score(option[key]) * weight
    return round(total, 2)


def winner_label(score_a: float, score_b: float) -> str:
    if score_a > score_b:
        return "Option A"
    if score_b > score_a:
        return "Option B"
    return "Tie"


def build_summary_table(option_a: Dict[str, int], option_b: Dict[str, int]) -> pd.DataFrame:
    rows = []
    for metric in WEIGHTS.keys():
        rows.append(
            {
                "Metric": metric.replace("_", " ").title(),
                "Option A": option_a[metric],
                "Option B": option_b[metric],
                "Weight": WEIGHTS[metric],
            }
        )
    return pd.DataFrame(rows)


def fallback_recommendation(
    context: str,
    name_a: str,
    name_b: str,
    score_a: float,
    score_b: float,
) -> str:
    winner = name_a if score_a >= score_b else name_b
    loser = name_b if winner == name_a else name_a
    return f"""
## Recommendation

Prioritize **{winner}**.

## Why this option wins

Based on the weighted score, {winner} currently outperforms {loser} in the decision model used for this prototype.
The recommendation reflects the current balance of strategic alignment, customer impact, confidence, and timing relative to effort and risk.

## Key tradeoffs

- The leading option is stronger overall, but the trailing option may still be attractive if assumptions change.
- This recommendation should be revisited if confidence drops, effort increases materially, or the business context shifts.

## What would change the recommendation

- New evidence that materially changes customer impact
- Updated effort estimates
- Higher or lower delivery risk
- A shift in strategic priority

## Suggested next step

Validate the two highest-uncertainty assumptions before making the final commitment.

### Context used

{context if context else "No additional context provided."}
""".strip()


def make_option_input(prefix: str, default_name: str, default_summary: str) -> Dict[str, int]:
    st.subheader(default_name)
    st.text_input("Option name", value=default_name, key=f"{prefix}_name")
    st.text_area("Summary", value=default_summary, key=f"{prefix}_summary", height=100)

    return {
        "strategic_alignment": st.slider("Strategic alignment", 1, 5, 4, key=f"{prefix}_strategic_alignment"),
        "customer_impact": st.slider("Customer impact", 1, 5, 4, key=f"{prefix}_customer_impact"),
        "revenue_potential": st.slider("Revenue potential", 1, 5, 3, key=f"{prefix}_revenue_potential"),
        "confidence": st.slider("Confidence", 1, 5, 3, key=f"{prefix}_confidence"),
        "effort": st.slider("Effort (higher = more effort)", 1, 5, 3, key=f"{prefix}_effort"),
        "risk": st.slider("Risk (higher = more risk)", 1, 5, 3, key=f"{prefix}_risk"),
        "time_criticality": st.slider("Time criticality", 1, 5, 3, key=f"{prefix}_time_criticality"),
    }


st.title("AI Product Decision Assistant")
st.caption("A medium-fidelity prototype for structured product prioritization.")

context = st.text_area(
    "Decision context",
    value="We have limited capacity this quarter and need to choose one initiative to prioritize.",
    height=120,
)

left, right = st.columns(2)
with left:
    metrics_a = make_option_input("a", "Option A", "Improve onboarding conversion with guided setup.")
with right:
    metrics_b = make_option_input("b", "Option B", "Launch admin analytics dashboard for enterprise accounts.")

name_a = st.session_state["a_name"]
summary_a = st.session_state["a_summary"]
name_b = st.session_state["b_name"]
summary_b = st.session_state["b_summary"]

score_a = score_option(metrics_a)
score_b = score_option(metrics_b)

st.markdown("## Comparison")
col1, col2, col3 = st.columns(3)
col1.metric(name_a, score_a)
col2.metric(name_b, score_b)
col3.metric("Recommended", winner_label(score_a, score_b))

table_df = build_summary_table(metrics_a, metrics_b)
st.dataframe(table_df, use_container_width=True)

score_summary = f"{name_a}: {score_a} | {name_b}: {score_b}"

if st.button("Generate recommendation", type="primary"):
    developer_prompt = """
You are an executive product decision copilot.
Return a concise recommendation with sections:
1. Recommendation
2. Why this option wins
3. Key tradeoffs
4. What would change the recommendation
5. Suggested next step
""".strip()

    user_prompt = f"""
Compare the following two product options and provide an executive recommendation.

Context:
{context}

Option A:
{name_a}
Summary: {summary_a}
Metrics: {metrics_a}

Option B:
{name_b}
Summary: {summary_b}
Metrics: {metrics_b}

Weighted score summary:
{score_summary}
""".strip()

    llm_text = generate_text(developer_prompt=developer_prompt, user_prompt=user_prompt)

    st.markdown("## Recommendation")
    if llm_text:
        st.markdown(llm_text)
    else:
        st.markdown(
            fallback_recommendation(
                context=context,
                name_a=name_a,
                name_b=name_b,
                score_a=score_a,
                score_b=score_b,
            )
        )
        st.info("Running in fallback mode. Add OPENAI_API_KEY to enable model-generated rationale.")
