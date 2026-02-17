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

---

## 3. Bugs

### Bug 1: Property dropdown not tenant-scoped

**Reproduction**
- Log in as Client A (Sunset). Open Dashboard. Note property dropdown (names and count).
- Log in as Client B (Ocean). Open Dashboard. Note property dropdown.

**Expected (from DB)**  
Sunset: 3 properties — Beach House Alpha (prop-001), City Apartment Downtown (prop-002), Country Villa Estate (prop-003).  
Ocean: 3 properties — Mountain Lodge Beta (prop-001), Lakeside Cottage (prop-004), Urban Loft Modern (prop-005).

**Observed**  
Both tenants see the same 5 options. Ocean sees "Beach House Alpha" (Sunset's name) instead of "Mountain Lodge Beta" for prop-001, and sees the other tenant's properties.

**Technical issue**  
Dashboard uses a single hardcoded `PROPERTIES` array in `frontend/src/components/Dashboard.tsx`; list and names are not tenant-scoped.

**Resolution**  
Add a backend endpoint that returns the current tenant's properties (id, name) from the `properties` table; Dashboard fetches this and builds the dropdown from the response.
