from django.core.exceptions import PermissionDenied

def has_role(user, role):
    if user.role != role:
        raise PermissionDenied(f"User must have {role} role")
