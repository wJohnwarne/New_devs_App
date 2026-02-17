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
| P2 | Clarity / Client A "March" mismatch | Cause unclear (wrong data vs comparing March to all-time). Document dashboard as all-time; P0/P1 fixes may resolve. |

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

**Implementation notes**  
Deploy backend endpoint first; frontend can follow. Add frontend fallback (e.g. show current list or "Unable to load properties") if the properties API fails. Consider caching the property list per tenant (e.g. 5–10 min).

---

### Bug 2: Revenue summary wrong and not tenant-isolated

**Reproduction**
1. Start app (`docker-compose up --build`). Optionally clear revenue cache: `docker compose exec redis redis-cli DEL revenue:prop-001`.
2. Log in as Client A (Sunset). Open Dashboard, select Beach House Alpha (prop-001). Note API response (e.g. `total_revenue`, `reservations_count`).
3. Log out. Log in as Client B (Ocean). Open Dashboard, select first property (prop-001). Note API response.

**Expected (from DB/seed)**  
Sunset, prop-001: total **2250.00** USD, **4** reservations.  
Ocean, prop-001: total **0.00** USD, **0** reservations.

**Observed**  
Both tenants get the same response for prop-001 (e.g. `total_revenue: 1000.0`, `reservations_count: 3`). Clearing the cache does not fix it: the same wrong data reappears because the fallback path is also not tenant-scoped.

**Technical issue**  
- **Cache:** In `backend/app/services/cache.py` the cache key is `revenue:{property_id}` and does not include `tenant_id`, so cached data can be returned to the wrong tenant.  
- **Mock fallback:** In `backend/app/services/reservations.py`, when the DB is unavailable the fallback uses mock data keyed only by `property_id`, so both tenants receive the same mock (e.g. 1000.00 / 3) for prop-001.  
Auth correctly sets `tenant_id` from the token; the DB query correctly filters by `tenant_id`; the cache and fallback do not.

**Resolution**  
- Include `tenant_id` in the revenue cache key (e.g. `revenue:{tenant_id}:{property_id}`).  
- Make the mock fallback tenant-scoped (e.g. key by `(tenant_id, property_id)` or return 0.00/0 when the tenant has no mock for that property).

**Implementation notes**  
Old cache keys `revenue:{property_id}` become unused; they expire after TTL (5 min). Optionally run a one-off cleanup (e.g. `redis-cli KEYS "revenue:*"` then `DEL`) to free memory. Fix is backward-compatible and zero-downtime; no API or client change required. Mock fallback is only used when DB is unavailable; no migration needed.

---

### Bug 3: Revenue totals occasionally a few cents off (precision)

**Reproduction**
1. Log in as any client. Open Dashboard and select **Precision Demo** (prop-precision-demo). This uses mock total `2.675`, which exposes float rounding.
2. Note the `total_revenue` shown (API and UI). Compare to expected: 2.675 should round to **2.68** (or 2.67 depending on rounding mode).
3. Alternatively, once DB is available: compare API total for a property with fractional-cent amounts (e.g. prop-001 tenant-a: 333.333 + 333.333 + 333.334) to `SELECT SUM(total_amount)` in the DB.

**Expected**  
API total matches the DB (or mock) sum when rounded to 2 decimal places. No spurious cent differences.

**Observed**  
API can return a value that rounds to the wrong cent (e.g. 2.67 instead of 2.68 for 2.675) due to floating-point rounding. Finance reports "totals slightly off by a few cents."

**Technical issue**  
In `backend/app/api/v1/dashboard.py`, revenue is converted with `float(revenue_data['total'])`. Float cannot represent many decimals exactly, so rounding to 2 decimals can be wrong by a cent. The DB stores `NUMERIC(10,3)`; the service returns a float.

**Resolution**  
Keep amounts as `Decimal` in the backend; round to 2 decimal places (e.g. `Decimal.quantize(Decimal('0.01'))`) only when formatting the response; then convert that rounded value for JSON so the API returns a number that matches the source when rounded to cents.

**Implementation notes**  
Change is limited to the dashboard response path; no cache or client contract change. Backward-compatible. Mock entry `prop-precision-demo` (total `2.675`) added for reproduction when DB is unavailable.
