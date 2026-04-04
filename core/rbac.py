from fastapi import Depends, HTTPException
from core.security import get_current_user


def require_roles(allowed_roles: list[str]):
    """
    Dependency factory.  Usage:
        Depends(require_roles(["admin", "analyst"]))
    """
    def checker(user: dict = Depends(get_current_user)):
        if user.get("role") not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail=f"Access denied. Required roles: {allowed_roles}"
            )
        return user
    return checker