"""Access Control — RBAC for Jake's agent and skill execution.

Defines roles, permissions, and a controller that checks whether
a given agent/caller is authorized to perform an action.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class Permission(str, Enum):
    # Read operations
    READ_BRAIN = "read:brain"
    READ_MEMORY = "read:memory"
    READ_EMAILS = "read:emails"
    READ_CALENDAR = "read:calendar"
    READ_GOALS = "read:goals"
    READ_TASKS = "read:tasks"
    READ_PIPELINE = "read:pipeline"

    # Write operations
    WRITE_BRAIN = "write:brain"
    WRITE_MEMORY = "write:memory"
    WRITE_TASKS = "write:tasks"
    WRITE_GOALS = "write:goals"
    WRITE_PIPELINE = "write:pipeline"

    # Execute operations
    EXEC_EMPLOYEE = "exec:employee"
    EXEC_PIPELINE = "exec:pipeline"
    EXEC_RESEARCH = "exec:research"
    EXEC_CONTENT = "exec:content"
    EXEC_SEND_MESSAGE = "exec:send_message"  # Telegram/email send

    # Admin operations
    ADMIN_VAULT = "admin:vault"
    ADMIN_AUDIT = "admin:audit"
    ADMIN_SECURITY = "admin:security"
    ADMIN_EVOLVE = "admin:evolve"


class Role(str, Enum):
    OPERATOR = "operator"        # Mike — full access
    AGENT = "agent"              # Autonomous agents — read + write brain, exec pipeline
    EMPLOYEE = "employee"        # AI employees — exec, write tasks, read all
    VIEWER = "viewer"            # Read-only (dashboard, external)
    RESTRICTED = "restricted"   # No access to sensitive ops


_ROLE_PERMISSIONS: dict[Role, set[Permission]] = {
    Role.OPERATOR: set(Permission),  # all permissions

    Role.AGENT: {
        Permission.READ_BRAIN, Permission.READ_MEMORY, Permission.READ_GOALS,
        Permission.READ_TASKS, Permission.READ_PIPELINE,
        Permission.WRITE_BRAIN, Permission.WRITE_MEMORY,
        Permission.WRITE_TASKS, Permission.WRITE_PIPELINE,
        Permission.EXEC_PIPELINE, Permission.EXEC_RESEARCH, Permission.EXEC_CONTENT,
    },

    Role.EMPLOYEE: {
        Permission.READ_BRAIN, Permission.READ_MEMORY, Permission.READ_GOALS,
        Permission.READ_TASKS, Permission.READ_EMAILS, Permission.READ_CALENDAR,
        Permission.WRITE_BRAIN, Permission.WRITE_MEMORY,
        Permission.WRITE_TASKS, Permission.WRITE_GOALS,
        Permission.EXEC_EMPLOYEE, Permission.EXEC_PIPELINE,
        Permission.EXEC_RESEARCH, Permission.EXEC_CONTENT,
        Permission.EXEC_SEND_MESSAGE,
    },

    Role.VIEWER: {
        Permission.READ_BRAIN, Permission.READ_MEMORY, Permission.READ_GOALS,
        Permission.READ_TASKS, Permission.READ_PIPELINE,
    },

    Role.RESTRICTED: set(),
}

# Named actors and their default roles
_ACTOR_ROLES: dict[str, Role] = {
    "jake": Role.OPERATOR,
    "mike": Role.OPERATOR,
    "operator": Role.OPERATOR,
    "oracle_sentinel": Role.EMPLOYEE,
    "inbox_zero": Role.EMPLOYEE,
    "meeting_prep": Role.EMPLOYEE,
    "research_agent": Role.AGENT,
    "content_creator": Role.EMPLOYEE,
    "family_coordinator": Role.EMPLOYEE,
    "pipeline_runner": Role.AGENT,
    "self_improvement": Role.AGENT,
    "research_daemon": Role.AGENT,
    "collective": Role.AGENT,
    "dashboard": Role.VIEWER,
}


@dataclass
class AccessController:
    """Check permissions for actors performing operations."""

    actor_roles: dict[str, Role] = field(default_factory=lambda: dict(_ACTOR_ROLES))
    role_permissions: dict[Role, set[Permission]] = field(
        default_factory=lambda: dict(_ROLE_PERMISSIONS)
    )

    def get_role(self, actor: str) -> Role:
        return self.actor_roles.get(actor.lower(), Role.RESTRICTED)

    def has_permission(self, actor: str, permission: Permission) -> bool:
        role = self.get_role(actor)
        return permission in self.role_permissions.get(role, set())

    def require_permission(self, actor: str, permission: Permission) -> None:
        if not self.has_permission(actor, permission):
            role = self.get_role(actor)
            raise PermissionError(
                f"Actor '{actor}' (role={role.value}) lacks permission '{permission.value}'"
            )

    def get_permissions(self, actor: str) -> set[Permission]:
        role = self.get_role(actor)
        return self.role_permissions.get(role, set())

    def register_actor(self, actor: str, role: Role) -> None:
        self.actor_roles[actor.lower()] = role


access_controller = AccessController()
