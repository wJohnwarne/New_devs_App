"""
Tenant-scoped properties list for the revenue dashboard dropdown.
Tries DB first; on failure or misconfiguration returns a static list per tenant.
"""
from typing import Any, Dict, List

# Fallback lists aligned with seed data and precision-demo (each tenant's properties only)
_FALLBACK_PROPERTIES: Dict[str, List[Dict[str, str]]] = {
    "tenant-a": [
        {"id": "prop-001", "name": "Beach House Alpha"},
        {"id": "prop-002", "name": "City Apartment Downtown"},
        {"id": "prop-003", "name": "Country Villa Estate"},
        {"id": "prop-precision-demo", "name": "Precision Demo"},
    ],
    "tenant-b": [
        {"id": "prop-001", "name": "Mountain Lodge Beta"},
        {"id": "prop-004", "name": "Lakeside Cottage"},
        {"id": "prop-005", "name": "Urban Loft Modern"},
        {"id": "prop-precision-demo", "name": "Precision Demo"},
    ],
}


async def get_tenant_properties(tenant_id: str) -> List[Dict[str, Any]]:
    """
    Return list of { id, name } for the current tenant's properties.
    Uses Supabase when available; otherwise returns tenant-scoped fallback.
    """
    try:
        from app.database import supabase
        response = supabase.service.table("properties").select("id, name").eq(
            "tenant_id", tenant_id
        ).execute()
        if response.data and len(response.data) > 0:
            return [
                {"id": row.get("id", ""), "name": row.get("name") or row.get("id") or ""}
                for row in response.data
            ]
    except Exception:
        pass
    return _FALLBACK_PROPERTIES.get(tenant_id, [])
