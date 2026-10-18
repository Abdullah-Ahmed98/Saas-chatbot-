from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import CurrentUser
from app.models.database import get_db
from app.models.schemas import Tenant

router = APIRouter(prefix="/api/tenant", tags=["tenant"])


class TenantOut(BaseModel):
    id: str
    name: str
    plan: str
    is_active: bool


@router.get("/me", response_model=TenantOut)
async def my_tenant(user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    if user.tenant_id is None:
        raise HTTPException(404, "No tenant")
    t = (await db.execute(select(Tenant).where(Tenant.id == user.tenant_id))).scalar_one()
    return TenantOut(id=str(t.id), name=t.name, plan=t.plan, is_active=t.is_active)
