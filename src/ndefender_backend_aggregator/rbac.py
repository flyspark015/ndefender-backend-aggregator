"""Role-based access control."""

from __future__ import annotations

from fastapi import Header, HTTPException, status

from .config import get_config


def get_role(x_role: str | None = Header(default=None)) -> str:
    config = get_config()
    role = (x_role or "viewer").lower()
    if role not in config.rbac.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unknown role",
        )
    return role


def require_permission(permission: str):
    def _check(role: str = Header(default="viewer", alias="X-Role")) -> None:
        config = get_config()
        if not config.auth.rbac_enabled:
            return
        role_name = role.lower()
        role_config = config.rbac.roles.get(role_name)
        if not role_config:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Unknown role",
            )
        if permission not in role_config.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )

    return _check
