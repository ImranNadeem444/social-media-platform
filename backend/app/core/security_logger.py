import json
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from fastapi import Request

from app.models.audit_log import AuditLog


def _get_client_ip(request: Request | None) -> str | None:
    """Extract client IP from request."""
    if not request:
        return None

    # Check X-Forwarded-For header (proxy/load balancer)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    # Fallback to direct connection
    if request.client:
        return request.client.host

    return None


def _create_audit_log(
    user_id: int | None,
    action: str,
    status: str,
    details: dict | None,
    error_message: str | None,
    ip_address: str | None,
    db: Session,
) -> AuditLog:
    """Create and save an audit log entry."""
    log = AuditLog(
        user_id=user_id,
        action=action,
        status=status,
        details=json.dumps(details) if details else None,
        error_message=error_message,
        ip_address=ip_address,
    )

    db.add(log)
    db.commit()

    return log


def log_login_success(
    user_id: int,
    email: str,
    request: Request | None,
    db: Session,
) -> None:
    """Log successful login."""
    _create_audit_log(
        user_id=user_id,
        action="login",
        status="success",
        details={"email": email},
        error_message=None,
        ip_address=_get_client_ip(request),
        db=db,
    )


def log_login_failure(
    email: str,
    reason: str,
    request: Request | None,
    db: Session,
) -> None:
    """Log failed login attempt."""
    _create_audit_log(
        user_id=None,
        action="login",
        status="failure",
        details={"email": email},
        error_message=reason,
        ip_address=_get_client_ip(request),
        db=db,
    )


def log_registration(
    user_id: int,
    email: str,
    request: Request | None,
    db: Session,
) -> None:
    """Log new user registration."""
    _create_audit_log(
        user_id=user_id,
        action="registration",
        status="success",
        details={"email": email},
        error_message=None,
        ip_address=_get_client_ip(request),
        db=db,
    )


def log_oauth_start(
    user_id: int,
    platform: str,
    request: Request | None,
    db: Session,
) -> None:
    """Log OAuth authorization flow start."""
    _create_audit_log(
        user_id=user_id,
        action="oauth_start",
        status="pending",
        details={"platform": platform},
        error_message=None,
        ip_address=_get_client_ip(request),
        db=db,
    )


def log_oauth_success(
    user_id: int,
    platform: str,
    account_name: str | None,
    request: Request | None,
    db: Session,
) -> None:
    """Log successful OAuth connection."""
    _create_audit_log(
        user_id=user_id,
        action="oauth_success",
        status="success",
        details={"platform": platform, "account_name": account_name},
        error_message=None,
        ip_address=_get_client_ip(request),
        db=db,
    )


def log_oauth_failure(
    user_id: int | None,
    platform: str,
    error_reason: str,
    request: Request | None,
    db: Session,
) -> None:
    """Log failed OAuth connection."""
    _create_audit_log(
        user_id=user_id,
        action="oauth_failure",
        status="failure",
        details={"platform": platform},
        error_message=error_reason,
        ip_address=_get_client_ip(request),
        db=db,
    )


def log_account_disconnect(
    user_id: int,
    account_id: int,
    platform: str,
    account_name: str | None,
    request: Request | None,
    db: Session,
) -> None:
    """Log social account disconnection."""
    _create_audit_log(
        user_id=user_id,
        action="account_disconnect",
        status="success",
        details={
            "social_account_id": account_id,
            "platform": platform,
            "account_name": account_name,
        },
        error_message=None,
        ip_address=_get_client_ip(request),
        db=db,
    )


def log_post_created(
    user_id: int,
    target_platform: str,
    targets_count: int,
    post_status: str,
    request: Request | None,
    db: Session,
) -> None:
    """Log post creation."""
    _create_audit_log(
        user_id=user_id,
        action="post_created",
        status="success",
        details={
            "target_platform": target_platform,
            "targets_count": targets_count,
            "post_status": post_status,
        },
        error_message=None,
        ip_address=_get_client_ip(request),
        db=db,
    )


def log_post_failure(
    user_id: int,
    error_reason: str,
    request: Request | None,
    db: Session,
) -> None:
    """Log post creation failure."""
    _create_audit_log(
        user_id=user_id,
        action="post_created",
        status="failure",
        details=None,
        error_message=error_reason,
        ip_address=_get_client_ip(request),
        db=db,
    )


def log_unauthorized_access(
    resource: str,
    request: Request | None,
    db: Session,
) -> None:
    """Log unauthorized access attempt."""
    _create_audit_log(
        user_id=None,
        action="unauthorized_access",
        status="failure",
        details={"resource": resource},
        error_message="Access denied",
        ip_address=_get_client_ip(request),
        db=db,
    )
