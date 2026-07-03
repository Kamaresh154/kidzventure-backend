"""
One-off fix for existing databases: grants the 'inventory.write' permission
to the 'employee' role.

Why this is needed: app/db/bootstrap.py's seed_rbac() only seeds roles and
permissions the FIRST time the app starts against an empty database. Any
database that was already running before this fix will NOT automatically
pick up the new permission -- this script patches it in directly.

Usage (from backend-fixed/):
    python scripts/grant_employee_inventory_write.py
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.rbac import Role, Permission, RolePermission


async def main() -> None:
    async with AsyncSessionLocal() as db:
        role = (await db.execute(select(Role).where(Role.code == "employee"))).scalar_one_or_none()
        if not role:
            print("No 'employee' role found -- nothing to do.")
            return

        perm = (await db.execute(select(Permission).where(Permission.code == "inventory.write"))).scalar_one_or_none()
        if not perm:
            print("Permission 'inventory.write' not found in the permissions table -- check PERM_SEEDS.")
            return

        existing = (
            await db.execute(
                select(RolePermission).where(
                    RolePermission.role_id == role.id,
                    RolePermission.permission_id == perm.id,
                )
            )
        ).scalar_one_or_none()

        if existing:
            print("Employee role already has inventory.write -- nothing to do.")
            return

        db.add(RolePermission(role_id=role.id, permission_id=perm.id))
        await db.commit()
        print("Granted inventory.write to the employee role.")


if __name__ == "__main__":
    asyncio.run(main())
