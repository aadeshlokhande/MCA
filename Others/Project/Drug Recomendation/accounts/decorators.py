from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from audit.models import log_audit_event, AuditLog


def role_required(allowed_roles):
    """
    Decorator to restrict view access to specific user roles.
    allowed_roles: list or tuple of User.Role values (e.g. ['PATIENT', 'DOCTOR', 'ADMIN'])
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.warning(request, "Please log in to access this page.")
                return redirect('accounts:login')

            user_role = getattr(request.user, 'role', None)
            is_admin_user = request.user.is_superuser or user_role == 'ADMIN'

            if user_role in allowed_roles or (is_admin_user and 'ADMIN' in allowed_roles):
                return view_func(request, *args, **kwargs)

            # Log unauthorized access attempt for security audit
            log_audit_event(
                request,
                AuditLog.Action.ACCESS_DENIED,
                details=f"User {request.user.username} (Role: {user_role}) attempted restricted access to {request.path}"
            )
            messages.error(request, "Access restricted. You do not have permission to view this resource.")
            return redirect('accounts:role_redirect')

        return _wrapped_view
    return decorator


def patient_required(view_func):
    return role_required(['PATIENT'])(view_func)


def doctor_required(view_func):
    return role_required(['DOCTOR'])(view_func)


def admin_required(view_func):
    return role_required(['ADMIN'])(view_func)


def doctor_or_admin_required(view_func):
    return role_required(['DOCTOR', 'ADMIN'])(view_func)
