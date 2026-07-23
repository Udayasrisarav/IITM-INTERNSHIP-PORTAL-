from functools import wraps
from flask import request, jsonify, g
import jwt
from utils.jwt_handler import decode_token
from models import User, RoleMapping, Module, Role

def jwt_required_custom(f):
    """Decorator to require and validate JWT Bearer token."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", None)
        if not auth_header:
            return jsonify({"error": "Authorization header missing", "code": "UNAUTHORIZED"}), 401
        
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return jsonify({"error": "Invalid Authorization header format. Expected 'Bearer <token>'", "code": "UNAUTHORIZED"}), 401
        
        token = parts[1]
        try:
            payload = decode_token(token)
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Access token has expired", "code": "TOKEN_EXPIRED"}), 401
        except jwt.InvalidTokenError as e:
            return jsonify({"error": f"Invalid access token: {str(e)}", "code": "INVALID_TOKEN"}), 401

        user_id = payload.get("user_id")
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User associated with token not found", "code": "USER_NOT_FOUND"}), 401
        
        if not user.is_active:
            return jsonify({"error": "User account is inactive", "code": "USER_INACTIVE"}), 403

        g.current_user = user
        return f(*args, **kwargs)
    return decorated


def role_required(*allowed_roles):
    """Decorator to restrict route access to specific roles."""
    def decorator(f):
        @wraps(f)
        @jwt_required_custom
        def decorated(*args, **kwargs):
            user = getattr(g, "current_user", None)
            if not user or not user.role_mapping or not user.role_mapping.role:
                return jsonify({"error": "User role is not assigned or invalid", "code": "ROLE_MISSING"}), 403

            current_role = user.role_mapping.role.role_name
            if current_role not in allowed_roles:
                return jsonify({
                    "error": f"Access denied. Role '{current_role}' is not authorized.",
                    "allowed_roles": list(allowed_roles),
                    "code": "FORBIDDEN"
                }), 403

            return f(*args, **kwargs)
        return decorated
    return decorator


def permission_required(module_identifier: str, action: str):
    """
    Decorator to restrict route access by RBAC module permission.
    action must be one of: 'can_read', 'can_update', 'can_delete'
    """
    def decorator(f):
        @wraps(f)
        @jwt_required_custom
        def decorated(*args, **kwargs):
            if action not in ["can_read", "can_update", "can_delete"]:
                return jsonify({"error": f"Invalid permission action '{action}'", "code": "INVALID_ACTION"}), 500

            user = getattr(g, "current_user", None)
            if not user or not user.role_mapping:
                return jsonify({"error": "User role mapping missing", "code": "ROLE_MAPPING_MISSING"}), 403

            mapping = user.role_mapping
            module = mapping.module
            if not module:
                return jsonify({"error": "Module mapping missing", "code": "MODULE_MISSING"}), 403

            # Match module by code, name, or module_id
            module_matched = (
                module.module_name.upper() == module_identifier.upper() or
                (module.module_id and module.module_id.upper() == module_identifier.upper())
            )

            if not module_matched:
                return jsonify({
                    "error": f"Access denied for module '{module_identifier}'.",
                    "code": "MODULE_FORBIDDEN"
                }), 403

            has_permission = getattr(mapping, action, False)
            if not has_permission:
                return jsonify({
                    "error": f"Permission '{action}' denied for module '{module_identifier}'.",
                    "code": "PERMISSION_DENIED"
                }), 403

            return f(*args, **kwargs)
        return decorated
    return decorator
