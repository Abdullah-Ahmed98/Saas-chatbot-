from typing import Annotated, List

import uuid
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import require_admin, get_db
from app.models.schemas import Tenant, User

router = APIRouter(prefix="/api", tags=["admin"])


class TenantOut(BaseModel):
    id: uuid.UUID
    name: str
    plan: str
    is_active: bool


class UserOut(BaseModel):
    id: uuid.UUID
    email: str
    full_name: str
    tenant_id: uuid.UUID | None
    is_admin: bool
    is_active: bool


@router.get("/admin/tenants", response_model=List[TenantOut])
async def list_tenants(admin: Annotated[User, Depends(require_admin)], db: Annotated[AsyncSession, Depends(get_db)]):
    rows = (await db.execute(select(Tenant).order_by(Tenant.created_at.desc()).limit(200))).scalars().all()
    return [TenantOut(id=t.id, name=t.name, plan=t.plan, is_active=t.is_active) for t in rows]


@router.get("/admin/users", response_model=List[UserOut])
async def list_users(admin: Annotated[User, Depends(require_admin)], db: Annotated[AsyncSession, Depends(get_db)]):
    rows = (await db.execute(select(User).order_by(User.created_at.desc()).limit(200))).scalars().all()
    return [
        UserOut(id=u.id, email=u.email, full_name=u.full_name, tenant_id=u.tenant_id, is_admin=u.is_admin, is_active=u.is_active)
        for u in rows
    ]


@router.post("/admin/users/{user_id}/admin")
async def make_admin(
    user_id: uuid.UUID,
    admin: Annotated[User, Depends(require_admin)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    target = (await db.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
    if target is None:
        raise HTTPException(404, "User not found")
    target.is_admin = True
    await db.commit()
    return {"ok": True}
