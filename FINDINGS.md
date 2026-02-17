# Property Revenue Dashboard — Investigation Findings

## 1. Incidents

| # | Reporter | Summary |
|---|----------|---------|
| 1 | Client B (Ocean Rentals) | Sometimes on refresh, revenue numbers look like another company’s; serious privacy concern. |
| 2 | Client A (Sunset Properties) | Dashboard revenue totals don’t match internal records (e.g. March); accuracy concern. |
| 3 | Finance team | Revenue totals occasionally a few cents off. |

---

## 2. Prioritization

| Priority | Focus | Rationale |
|----------|--------|------------|
| P0 | Cross-tenant data / privacy | Wrong or shared data between clients; compliance and trust. |
| P1 | Revenue accuracy (values, precision) | Correctness of totals and rounding. |
| P2 | Clarity (e.g. March vs all-time) | Addressed by P0/P1; document behaviour where needed. |
