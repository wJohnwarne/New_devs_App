from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List
from app.services.cache import get_revenue_summary
from app.core.auth import authenticate_request as get_current_user

router = APIRouter()


def _round_revenue(value: str | float) -> float:
    """Round revenue to 2 decimal places using Decimal to avoid float precision issues."""
    d = Decimal(str(value)).quantize(Decimal("0.01"))
    return float(d)


@router.get("/dashboard/summary")
async def get_dashboard_summary(
    property_id: str,
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    
    tenant_id = getattr(current_user, "tenant_id", "default_tenant") or "default_tenant"
    
    revenue_data = await get_revenue_summary(property_id, tenant_id)
    
    total_revenue = _round_revenue(revenue_data['total'])
    
    return {
        "property_id": revenue_data['property_id'],
        "total_revenue": total_revenue,
        "currency": revenue_data['currency'],
        "reservations_count": revenue_data['count']
    }


@router.get("/dashboard/properties")
async def get_dashboard_properties(
    current_user: dict = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """Return current tenant's properties for the revenue dashboard dropdown."""
    tenant_id = getattr(current_user, "tenant_id", "default_tenant") or "default_tenant"
    from app.services.dashboard_properties import get_tenant_properties
    return await get_tenant_properties(tenant_id)
