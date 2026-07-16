# Care Transition Efficiency & Placement Outcome Analytics

> A process efficiency analysis of the U.S. HHS Unaccompanied Alien Children (UAC) Program — modelling the care-to-placement pipeline using 720 days of daily government-reported operational data (January 2023 – December 2025).

[![Streamlit App](https://img.shields.io/badge/Live%20Dashboard-Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://placement-outcome-analytics.streamlit.app/)
[![ResearchGate](https://img.shields.io/badge/Research%20Paper-ResearchGate-00CCBB?logo=researchgate&logoColor=white)](https://www.researchgate.net/publication/409285427_Care_Transition_Efficiency_Placement_Outcome_Analytics)
[![DOI](https://img.shields.io/badge/DOI-10.13140%2FRG.2.2.16874.48323-blue)](https://doi.org/10.13140/RG.2.2.16874.48323)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## Overview

Most public reporting on the UAC program focuses on headcount — how many children are in custody at any given moment. This project reframes that question: **not how many children are in the system, but how quickly and consistently they move through it.**

The UAC care process is modelled as a three-stage pipeline:

```
CBP Custody  ──transfer──▶  HHS Shelter Care  ──discharge──▶  Sponsor Placement
```

Four Key Performance Indicators are derived from this model and tracked across time to identify bottlenecks, measure placement efficiency, and detect the operational impact of a structural break identified in February 2025.

> **Scope:** This project analyses operational and logistical efficiency only. It does not evaluate immigration policy, enforcement strategies, or the legal merits of any administrative action.

---

## Key Findings

| Finding | Pre-Feb 2025 | Post-Feb 2025 | Change |
|---|---|---|---|
| Transfer Efficiency Ratio | 0.810 | 0.414 | −48.9% |
| Discharge Effectiveness Index | 0.031 | 0.007 | −78.1% |
| Pipeline Throughput Rate | 1.428 | 0.849 | −40.6% |
| Implied avg. stay in HHS care | 30–42 days | 150–300 days | +600–900% |
| Bottleneck day frequency | 13.9% | 26.3% | +89% |

**The system became smaller and slower simultaneously.** Daily apprehensions fell 93.6% but daily discharges fell 93.2%, while the HHS care population dropped only 70.1% — meaning children already in care were not placed at proportionate rates. The 72-day HHS legal guideline for care duration has been breached every recorded month since February 2025, peaking at 301 implied days in April 2025.

---

## Live Dashboard

**[→ Open the Streamlit dashboard](https://placement-outcome-analytics.streamlit.app/)**

The dashboard is structured across five pages:

| Page | Contents |
|---|---|
| **Pipeline Overview** | Raw time series for all five operational columns; stage-by-stage flow summary |
| **KPI Analysis** | Interactive KPI selector with 30-day rolling average; user-defined threshold alerts |
| **Pre vs. Post 2025** | Side-by-side efficiency comparison; volume change table |
| **Bottleneck Detection** | Monthly bottleneck frequency chart; pre/post bottleneck paradox metrics |
| **Placement Wait** | Monthly implied stay duration against the 72-day HHS guideline |

The sidebar provides a global date range filter and adjustable alert thresholds for the Discharge Effectiveness Index and Pipeline Throughput Rate. Alert banners update in real time.

---

## Research Paper

The full analysis is published on ResearchGate:

**Care Transition Efficiency & Placement Outcome Analytics**
Himanshu Rai · July 2026
DOI: [10.13140/RG.2.2.16874.48323](https://doi.org/10.13140/RG.2.2.16874.48323)

The paper covers: dataset description and cleaning, pipeline modelling methodology, all four KPI derivations, weekday operational patterns, pre/post structural break comparison, monthly discharge trend analysis, bottleneck detection, implied stay duration, discussion, and six policy recommendations.

---

## Repository Structure

```
placement-outcome-analytics/
│
├── app.py                                      # Streamlit dashboard (multi-page)
├── theme.py                                    # Light/dark theme system, CSS builder, Plotly themer
├── config.toml                                 # Streamlit theme configuration
├── requirements.txt                            # Python dependencies
│
├── HHS_Unaccompanied_Alien_Children_Program.csv   # Source dataset (720 reporting days)
├── HHS_UAC_Care_Transition_Analytics.pptx         # Presentation deck
└── US_Department_of_Health_and_Human_Services_seal.svg.webp   # HHS seal (dashboard header)
```

---

## KPI Definitions

All four KPIs are derived columns computed from the raw dataset. Division-by-zero cases (CBP custody = 0 or HHS care = 0) are treated as undefined (`NaN`).

```python
# KPI 1 — Transfer Efficiency Ratio (TER)
# How fast CBP moves children to HHS relative to those waiting
transfer_efficiency = cbp_transferred / cbp_in_custody

# KPI 2 — Discharge Effectiveness Index (DEI)
# Fraction of HHS care population placed with a sponsor each day
discharge_effectiveness = hhs_discharged / hhs_in_care

# KPI 3 — Backlog Accumulation Rate (BAR)
# Net children added to the system daily (negative = clearing)
backlog_accumulation = cbp_apprehended - hhs_discharged

# KPI 4 — Pipeline Throughput Rate (PTR)
# Total exits vs. total entries across the full pipeline
pipeline_throughput = (cbp_transferred + hhs_discharged) / (cbp_apprehended + cbp_in_custody)

# Derived — Implied Average Stay (days)
# Inverse of DEI; estimates how long a child waits in HHS care
implied_stay_days = 1 / discharge_effectiveness   # capped at 500 for monthly aggregation
```

A day is flagged as a **bottleneck day** when `BAR > 0` AND `PTR < 1.0` simultaneously.

---

## Running Locally

**Requirements:** Python 3.9+

```bash
# 1. Clone the repository
git clone https://github.com/Himanshu-Rai06/placement-outcome-analytics.git
cd placement-outcome-analytics

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the dashboard
streamlit run app.py
```

The app opens at `http://localhost:8501`. The CSV must be in the same directory as `app.py`.

---

## Dataset

- **Source:** U.S. Department of Health and Human Services, Office of Refugee Resettlement — UAC Program daily operational reports
- **Date range:** January 12, 2023 – December 21, 2025
- **Raw rows:** 1,170 (450 empty trailing rows removed)
- **Clean rows:** 720 reporting days
- **Columns:** Date, CBP apprehended, CBP in custody, CBP transferred, HHS in care, HHS discharged

The dataset was provided as part of a data science internship program. The data is publicly reported by the U.S. government.

---

## Dependencies

```
streamlit
pandas
numpy
plotly
```

See `requirements.txt` for pinned versions.

---

## Author

**Himanshu Rai**
Second-year undergraduate, Data Science
Data Science Intern · July 2026

[GitHub](https://github.com/Himanshu-Rai06) · [ResearchGate](https://www.researchgate.net/publication/409285427_Care_Transition_Efficiency_Placement_Outcome_Analytics)

---

## Citation

If you reference this work, please cite the published paper:

```bibtex
@misc{rai2026uac,
  author    = {Rai, Himanshu},
  title     = {Care Transition Efficiency \& Placement Outcome Analytics},
  year      = {2026},
  month     = {July},
  doi       = {10.13140/RG.2.2.16874.48323},
  url       = {https://www.researchgate.net/publication/409285427}
}
```

---

*This project analyses operational efficiency of the HHS UAC care pipeline. It does not evaluate immigration policy, enforcement, or the legal merits of any administrative decision.*
