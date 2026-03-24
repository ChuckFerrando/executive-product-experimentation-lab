# AI Product Decision Assistant

## Problem
Product leaders routinely need to choose between competing initiatives under constraints, but those decisions are often framed inconsistently and communicated unevenly.

## Hypothesis
A lightweight decision assistant that combines structured scoring with optional LLM-generated rationale can improve the quality, clarity, and repeatability of product prioritization conversations.

## Concept
This experiment takes two product options and scores them across:
- strategic alignment
- customer impact
- revenue potential
- confidence
- effort
- risk
- time criticality

It then produces:
- weighted scores
- a side-by-side comparison
- a recommendation
- an executive-ready rationale

## Architecture
- Streamlit UI
- deterministic weighted scoring engine
- optional LLM rationale generation
- no database required for v1

## Build
Run locally with Streamlit.

## Result
A usable medium-fidelity prototype for product decision support.

## Lessons Learned
Use structure first, AI second.

## Next Steps
- add more than two options
- save decision sessions
- add scenario templates
- support export to markdown or PDF
