import inspect
import logging
from functools import wraps
from typing import Dict, List, Optional, Any, Callable, Union
from datetime import datetime, timedelta

from google.auth.exceptions import RefreshError
from auth.google_auth import get_authenticated_google_service, GoogleAuthenticationError
from auth.scopes import (
    GMAIL_READONLY_SCOPE, GMAIL_SEND_SCOPE, GMAIL_COMPOSE_SCOPE, GMAIL_MODIFY_SCOPE, GMAIL_LABELS_SCOPE,
    DRIVE_READONLY_SCOPE, DRIVE_FILE_SCOPE,
    DOCS_READONLY_SCOPE, DOCS_WRITE_SCOPE,
    CALENDAR_READONLY_SCOPE, CALENDAR_EVENTS_SCOPE,
    SHEETS_READONLY_SCOPE, SHEETS_WRITE_SCOPE,
    CHAT_READONLY_SCOPE, CHAT_WRITE_SCOPE, CHAT_SPACES_SCOPE,
    FORMS_BODY_SCOPE, FORMS_BODY_READONLY_SCOPE, FORMS_RESPONSES_READONLY_SCOPE,
    SLIDES_SCOPE, SLIDES_READONLY_SCOPE,
    TASKS_SCOPE, TASKS_READONLY_SCOPE,
    CUSTOM_SEARCH_SCOPE
)

# OAuth 2.1 integration is now handled by FastMCP auth
OAUTH21_INTEGRATION_AVAILABLE = True


# REMOVED: _extract_and_verify_bearer_token function. This functionality is now handled by AuthInfoMiddleware.
async def get_authenticated_google_service_oauth21(
    service_name: str,
    version: str,
    tool_name: str,
    user_google_email: str,
    required_scopes: List[str],
    session_id: Optional[str] = None,
    auth_token_email: Optional[str] = None,
    allow_recent_auth: bool = False,
) -> tuple[Any, str]:
    """
    OAuth 2.1 authentication using the session store with security validation.
    """
    from auth.oauth21_session_store import get_oauth21_session_store
    from googleapiclient.discovery import build

    store = get_oauth21_session_store()

    # Use the new validation method to ensure session can only access its own credentials
    credentials = store.get_credentials_with_validation(
        requested_user_email=user_google_email,
        session_id=session_id,
        auth_token_email=auth_token_email,
        allow_recent_auth=allow_recent_auth
    )

    if not credentials:
        from auth.google_auth import GoogleAuthenticationError
        raise GoogleAuthenticationError(
            f"Access denied: Cannot retrieve credentials for {user_google_email}. "
            f"You can only access credentials for your authenticated account."
        )

    # Check scopes
    if not all(scope in credentials.scopes for scope in required_scopes):
        from auth.google_auth import GoogleAuthenticationError
        raise GoogleAuthenticationError(f"OAuth 2.1 credentials lack required scopes. Need: {required_scopes}, Have: {credentials.scopes}")

    # Build service
    service = build(service_name, version, credentials=credentials)
    logger.info(f"[{tool_name}] Authenticated {service_name} for {user_google_email}")

    return service, user_google_email

logger = logging.getLogger(__name__)

# Service configuration mapping
SERVICE_CONFIGS = {
    "gmail": {"service": "gmail", "version": "v1"},
    "drive": {"service": "drive", "version": "v3"},
    "calendar": {"service": "calendar", "version": "v3"},
    "docs": {"service": "docs", "version": "v1"},
    "sheets": {"service": "sheets", "version": "v4"},
    "chat": {"service": "chat", "version": "v1"},
    "forms": {"service": "forms", "version": "v1"},
    "slides": {"service": "slides", "version": "v1"},
    "tasks": {"service": "tasks", "version": "v1"},
    "customsearch": {"service": "customsearch", "version": "v1"}
}


# Scope group definitions for easy reference
SCOPE_GROUPS = {
    # Gmail scopes
    "gmail_read": GMAIL_READONLY_SCOPE,
    "gmail_send": GMAIL_SEND_SCOPE,
    "gmail_compose": GMAIL_COMPOSE_SCOPE,
    "gmail_modify": GMAIL_MODIFY_SCOPE,
    "gmail_labels": GMAIL_LABELS_SCOPE,

    # Drive scopes
    "drive_read": DRIVE_READONLY_SCOPE,
    "drive_file": DRIVE_FILE_SCOPE,

    # Docs scopes
    "docs_read": DOCS_READONLY_SCOPE,
    "docs_write": DOCS_WRITE_SCOPE,

    # Calendar scopes
    "calendar_read": CALENDAR_READONLY_SCOPE,
    "calendar_events": CALENDAR_EVENTS_SCOPE,

    # Sheets scopes
    "sheets_read": SHEETS_READONLY_SCOPE,
    "sheets_write": SHEETS_WRITE_SCOPE,

    # Chat scopes
    "chat_read": CHAT_READONLY_SCOPE,
    "chat_write": CHAT_WRITE_SCOPE,
    "chat_spaces": CHAT_SPACES_SCOPE,

    # Forms scopes
    "forms": FORMS_BODY_SCOPE,
    "forms_read": FORMS_BODY_READONLY_SCOPE,
    "forms_responses_read": FORMS_RESPONSES_READONLY_SCOPE,

    # Slides scopes
    "slides": SLIDES_SCOPE,
    "slides_read": SLIDES_READONLY_SCOPE,

    # Tasks scopes
    "tasks": TASKS_SCOPE,
    "tasks_read": TASKS_READONLY_SCOPE,

    # Custom Search scope
    "customsearch": CUSTOM_SEARCH_SCOPE,
}

# Service cache: {cache_key: (service, cached_time, user_email)}
_service_cache: Dict[str, tuple[Any, datetime, str]] = {}
_cache_ttl = timedelta(minutes=30)  # Cache services for 30 minutes


def _get_cache_key(user_email: str, service_name: str, version: str, scopes: List[str]) -> str:
    """Generate a cache key for service instances."""
    sorted_scopes = sorted(scopes)
    return f"{user_email}:{service_name}:{version}:{':'.join(sorted_scopes)}"


def _is_cache_valid(cached_time: datetime) -> bool:
    """Check if cached service is still valid."""
    return datetime.now() - cached_time < _cache_ttl


def _get_cached_service(cache_key: str) -> Optional[tuple[Any, str]]:
    """Retrieve cached service if valid."""
    if cache_key in _service_cache:
        service, cached_time, user_email = _service_cache[cache_key]
        if _is_cache_valid(cached_time):
            logger.debug(f"Using cached service for key: {cache_key}")
            return service, user_email
        else:
            # Remove expired cache entry
            del _service_cache[cache_key]
            logger.debug(f"Removed expired cache entry: {cache_key}")
    return None


def _cache_service(cache_key: str, service: Any, user_email: str) -> None:
    """Cache a service instance."""
    _service_cache[cache_key] = (service, datetime.now(), user_email)
    logger.debug(f"Cached service for key: {cache_key}")


def _resolve_scopes(scopes: Union[str, List[str]]) -> List[str]:
    """Resolve scope names to actual scope URLs."""
    if isinstance(scopes, str):
        if scopes in SCOPE_GROUPS:
            return [SCOPE_GROUPS[scopes]]
        else:
            return [scopes]

    resolved = []
    for scope in scopes:
        if scope in SCOPE_GROUPS:
            resolved.append(SCOPE_GROUPS[scope])
        else:
            resolved.append(scope)
    return resolved


def _handle_token_refresh_error(error: RefreshError, user_email: str, service_name: str) -> str:
    """
    Handle token refresh errors gracefully, particularly expired/revoked tokens.

    Args:
        error: The RefreshError that occurred
        user_email: User's email address
        service_name: Name of the Google service

    Returns:
        A user-friendly error message with instructions for reauthentication
    """
    error_str = str(error)

    if 'invalid_grant' in error_str.lower() or 'expired or revoked' in error_str.lower():
        logger.warning(f"Token expired or revoked for user {user_email} accessing {service_name}")

        # Clear any cached service for this user to force fresh authentication
        clear_service_cache(user_email)

        service_display_name = f"Google {service_name.title()}"

        return (
            f"**Authentication Required: Token Expired/Revoked for {service_display_name}**\n\n"
            f"Your Google authentication token for {user_email} has expired or been revoked. "
            f"This commonly happens when:\n"
            f"- The token has been unused for an extended period\n"
            f"- You've changed your Google account password\n"
            f"- You've revoked access to the application\n\n"
            f"**To resolve this, please:**\n"
            f"1. Run `start_google_auth` with your email ({user_email}) and service_name='{service_display_name}'\n"
            f"2. Complete the authentication flow in your browser\n"
            f"3. Retry your original command\n\n"
            f"The application will automatically use the new credentials once authentication is complete."
        )
    else:
        # Handle other types of refresh errors
        logger.error(f"Unexpected refresh error for user {user_email}: {error}")
        return (
            f"Authentication error occurred for {user_email}. "
            f"Please try running `start_google_auth` with your email and the appropriate service name to reauthenticate."
        )


def require_google_service(
    service_type: str,
    scopes: Union[str, List[str]],
    version: Optional[str] = None,
    cache_enabled: bool = True
):
    """
    Decorator that automatically handles Google service authentication and injection.

    Args:
        service_type: Type of Google service ("gmail", "drive", "calendar", etc.)
        scopes: Required scopes (can be scope group names or actual URLs)
        version: Service version (defaults to standard version for service type)
        cache_enabled: Whether to use service caching (default: True)

    Usage:
        @require_google_service("gmail", "gmail_read")
        async def search_messages(service, user_google_email: str, query: str):
            # service parameter is automatically injected
            # Original authentication logic is handled automatically
    """
    def decorator(func: Callable) -> Callable:
        # Inspect the original function signature
        original_sig = inspect.signature(func)
        params = list(original_sig.parameters.values())

        # The decorated function must have 'service' as its first parameter.
        if not params or params[0].name != 'service':
            raise TypeError(
                f"Function '{func.__name__}' decorated with @require_google_service "
                "must have 'service' as its first parameter."
            )

        # Create a new signature for the wrapper that excludes the 'service' parameter.
        # This is the signature that FastMCP will see.
        wrapper_sig = original_sig.replace(parameters=params[1:])

        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Note: `args` and `kwargs` are now the arguments for the *wrapper*,
            # which does not include 'service'.

            # Extract user_google_email from the arguments passed to the wrapper
            bound_args = wrapper_sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            user_google_email = bound_args.arguments.get('user_google_email')

            if not user_google_email:
                # This should ideally not be reached if 'user_google_email' is a required parameter
                # in the function signature, but it's a good safeguard.
                raise Exception("'user_google_email' parameter is required but was not found.")

            # Get service configuration from the decorator's arguments
            if service_type not in SERVICE_CONFIGS:
                raise Exception(f"Unknown service type: {service_type}")

            config = SERVICE_CONFIGS[service_type]
            service_name = config["service"]
            service_version = version or config["version"]

            # Resolve scopes
            resolved_scopes = _resolve_scopes(scopes)

            # --- Service Caching and Authentication Logic (largely unchanged) ---
            service = None
            actual_user_email = user_google_email

            if cache_enabled:
                cache_key = _get_cache_key(user_google_email, service_name, service_version, resolved_scopes)
                cached_result = _get_cached_service(cache_key)
                if cached_result:
                    service, actual_user_email = cached_result

            if service is None:
                try:
                    tool_name = func.__name__

                    # SIMPLIFIED: Just get the authenticated user from the context
                    # The AuthInfoMiddleware has already done all the authentication checks
                    authenticated_user = None
                    auth_method = None
                    mcp_session_id = None

                    try:
                        from fastmcp.server.dependencies import get_context
                        ctx = get_context()
                        if ctx:
                            # Get the authenticated user email set by AuthInfoMiddleware
                            authenticated_user = ctx.get_state("authenticated_user_email")
                            auth_method = ctx.get_state("authenticated_via")

                            # Get session ID for logging
                            if hasattr(ctx, 'session_id'):
                                mcp_session_id = ctx.session_id
                                # Set FastMCP session ID in context variable for propagation
                                from core.context import set_fastmcp_session_id
                                set_fastmcp_session_id(mcp_session_id)

                            logger.debug(f"[{tool_name}] Auth from middleware: {authenticated_user} via {auth_method}")
                    except Exception as e:
                        logger.debug(f"[{tool_name}] Could not get FastMCP context: {e}")

                    # Log authentication status
                    logger.debug(f"[{tool_name}] Auth: {authenticated_user or 'none'} via {auth_method or 'none'} (session: {mcp_session_id[:8] if mcp_session_id else 'none'})")

                    from auth.oauth_config import is_oauth21_enabled, get_oauth_config

                    use_oauth21 = False

                    if is_oauth21_enabled():
                        # When OAuth 2.1 is enabled globally, ALWAYS use OAuth 2.1 for authenticated users.
                        if authenticated_user:
                            use_oauth21 = True
                            logger.info(f"[{tool_name}] OAuth 2.1 mode: Using OAuth 2.1 for authenticated user '{authenticated_user}'")
                        else:
                            # Only use version detection for unauthenticated requests
                            config = get_oauth_config()
                            request_params = {}
                            if mcp_session_id:
                                request_params["session_id"] = mcp_session_id

                            oauth_version = config.detect_oauth_version(request_params)
                            use_oauth21 = (oauth_version == "oauth21")
                            logger.info(f"[{tool_name}] OAuth version detected: {oauth_version}, will use OAuth 2.1: {use_oauth21}")

                    # Override user_google_email with authenticated user when using OAuth 2.1
                    if use_oauth21 and authenticated_user:
                        if bound_args.arguments.get('user_google_email') != authenticated_user:
                            original_email = bound_args.arguments.get('user_google_email')
                            logger.info(f"[{tool_name}] OAuth 2.1: Overriding user_google_email from '{original_email}' to authenticated user '{authenticated_user}'")
                            bound_args.arguments['user_google_email'] = authenticated_user
                            user_google_email = authenticated_user

                            # Update in kwargs if the parameter exists there
                            if 'user_google_email' in kwargs:
                                kwargs['user_google_email'] = authenticated_user

                            # Update in args if user_google_email is passed positionally
                            wrapper_params = list(wrapper_sig.parameters.keys())
                            if 'user_google_email' in wrapper_params:
                                user_email_index = wrapper_params.index('user_google_email')
                                if user_email_index < len(args):
                                    args_list = list(args)
                                    args_list[user_email_index] = authenticated_user
                                    args = tuple(args_list)

                    if use_oauth21:
                        logger.debug(f"[{tool_name}] Using OAuth 2.1 flow")
                        # The downstream get_authenticated_google_service_oauth21 will handle token validation
                        service, actual_user_email = await get_authenticated_google_service_oauth21(
                            service_name=service_name,
                            version=service_version,
                            tool_name=tool_name,
                            user_google_email=user_google_email,
                            required_scopes=resolved_scopes,
                            session_id=mcp_session_id,
                            auth_token_email=authenticated_user,
                            allow_recent_auth=False,
                        )
                    else:
                        # Use legacy OAuth 2.0 authentication
                        logger.debug(f"[{tool_name}] Using legacy OAuth 2.0 flow")
                        service, actual_user_email = await get_authenticated_google_service(
                            service_name=service_name,
                            version=service_version,
                            tool_name=tool_name,
                            user_google_email=user_google_email,
                            required_scopes=resolved_scopes,
                            session_id=mcp_session_id,
                        )

                    if cache_enabled:
                        cache_key = _get_cache_key(user_google_email, service_name, service_version, resolved_scopes)
                        _cache_service(cache_key, service, actual_user_email)
                except GoogleAuthenticationError as e:
                    logger.error(
                        f"[{tool_name}] GoogleAuthenticationError during authentication. "
                        f"Method={auth_method or 'none'}, User={authenticated_user or 'none'}, "
                        f"Service={service_name} v{service_version}, MCPSessionID={mcp_session_id or 'none'}: {e}"
                    )
                    # Re-raise the original error without wrapping it
                    raise

            try:
                # Prepend the fetched service object to the original arguments
                return await func(service, *args, **kwargs)
            except RefreshError as e:
                error_message = _handle_token_refresh_error(e, actual_user_email, service_name)
                raise Exception(error_message)

        # Set the wrapper's signature to the one without 'service'
        wrapper.__signature__ = wrapper_sig
        return wrapper
    return decorator


def require_multiple_services(service_configs: List[Dict[str, Any]]):
    """
    Decorator for functions that need multiple Google services.

    Args:
        service_configs: List of service configurations, each containing:
            - service_type: Type of service
            - scopes: Required scopes
            - param_name: Name to inject service as (e.g., 'drive_service', 'docs_service')
            - version: Optional version override

    Usage:
        @require_multiple_services([
            {"service_type": "drive", "scopes": "drive_read", "param_name": "drive_service"},
            {"service_type": "docs", "scopes": "docs_read", "param_name": "docs_service"}
        ])
        async def get_doc_with_metadata(drive_service, docs_service, user_google_email: str, doc_id: str):
            # Both services are automatically injected
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract user_google_email
            sig = inspect.signature(func)
            param_names = list(sig.parameters.keys())

            user_google_email = None
            if 'user_google_email' in kwargs:
                user_google_email = kwargs['user_google_email']
            else:
                try:
                    user_email_index = param_names.index('user_google_email')
                    if user_email_index < len(args):
                        user_google_email = args[user_email_index]
                except ValueError:
                    pass

            if not user_google_email:
                raise Exception("user_google_email parameter is required but not found")

            # Authenticate all services
            for config in service_configs:
                service_type = config["service_type"]
                scopes = config["scopes"]
                param_name = config["param_name"]
                version = config.get("version")

                if service_type not in SERVICE_CONFIGS:
                    raise Exception(f"Unknown service type: {service_type}")

                service_config = SERVICE_CONFIGS[service_type]
                service_name = service_config["service"]
                service_version = version or service_config["version"]
                resolved_scopes = _resolve_scopes(scopes)

                try:
                    tool_name = func.__name__

                    authenticated_user = None
                    mcp_session_id = None

                    try:
                        from fastmcp.server.dependencies import get_context
                        ctx = get_context()
                        if ctx:
                            authenticated_user = ctx.get_state("authenticated_user_email")
                            if hasattr(ctx, 'session_id'):
                                mcp_session_id = ctx.session_id
                    except Exception as e:
                        logger.debug(f"[{tool_name}] Could not get FastMCP context: {e}")

                    from auth.oauth_config import is_oauth21_enabled

                    use_oauth21 = False
                    if is_oauth21_enabled():
                        # When OAuth 2.1 is enabled globally, ALWAYS use OAuth 2.1 for authenticated users
                        if authenticated_user:
                            use_oauth21 = True
                        else:
                            # Only use version detection for unauthenticated requests (rare case)
                            use_oauth21 = False

                    # Override user_google_email with authenticated user when using OAuth 2.1
                    if use_oauth21 and authenticated_user:
                        if user_google_email != authenticated_user:
                            logger.info(f"[{tool_name}] OAuth 2.1: Overriding user_google_email from '{user_google_email}' to authenticated user '{authenticated_user}' for service '{service_type}'")
                            user_google_email = authenticated_user

                            # Update in kwargs if present
                            if 'user_google_email' in kwargs:
                                kwargs['user_google_email'] = authenticated_user

                            # Update in args if user_google_email is passed positionally
                            try:
                                user_email_index = param_names.index('user_google_email')
                                if user_email_index < len(args):
                                    # Convert args to list, update, convert back to tuple
                                    args_list = list(args)
                                    args_list[user_email_index] = authenticated_user
                                    args = tuple(args_list)
                            except ValueError:
                                pass  # user_google_email not in positional parameters

                    if use_oauth21:
                        logger.debug(f"[{tool_name}] Attempting OAuth 2.1 authentication flow for {service_type}.")
                        service, _ = await get_authenticated_google_service_oauth21(
                            service_name=service_name,
                            version=service_version,
                            tool_name=tool_name,
                            user_google_email=user_google_email,
                            required_scopes=resolved_scopes,
                            session_id=mcp_session_id,
                            auth_token_email=authenticated_user,
                            allow_recent_auth=False,
                        )
                    else:
                        # If OAuth 2.1 is not enabled, always use the legacy authentication method.
                        logger.debug(f"[{tool_name}] Using legacy authentication flow for {service_type} (OAuth 2.1 disabled).")
                        service, _ = await get_authenticated_google_service(
                            service_name=service_name,
                            version=service_version,
                            tool_name=tool_name,
                            user_google_email=user_google_email,
                            required_scopes=resolved_scopes,
                            session_id=mcp_session_id,
                        )

                    # Inject service with specified parameter name
                    kwargs[param_name] = service

                except GoogleAuthenticationError as e:
                    logger.error(
                        f"[{tool_name}] GoogleAuthenticationError for service '{service_type}' (user: {user_google_email}): {e}"
                    )
                    # Re-raise the original error without wrapping it
                    raise

            # Call the original function with refresh error handling
            try:
                return await func(*args, **kwargs)
            except RefreshError as e:
                # Handle token refresh errors gracefully
                error_message = _handle_token_refresh_error(e, user_google_email, "Multiple Services")
                raise Exception(error_message)

        return wrapper
    return decorator


def clear_service_cache(user_email: Optional[str] = None) -> int:
    """
    Clear service cache entries.

    Args:
        user_email: If provided, only clear cache for this user. If None, clear all.

    Returns:
        Number of cache entries cleared.
    """
    global _service_cache

    if user_email is None:
        count = len(_service_cache)
        _service_cache.clear()
        logger.info(f"Cleared all {count} service cache entries")
        return count

    keys_to_remove = [key for key in _service_cache.keys() if key.startswith(f"{user_email}:")]
    for key in keys_to_remove:
        del _service_cache[key]

    logger.info(f"Cleared {len(keys_to_remove)} service cache entries for user {user_email}")
    return len(keys_to_remove)


def get_cache_stats() -> Dict[str, Any]:
    """Get service cache statistics."""
    valid_entries = 0
    expired_entries = 0

    for _, (_, cached_time, _) in _service_cache.items():
        if _is_cache_valid(cached_time):
            valid_entries += 1
        else:
            expired_entries += 1

    return {
        "total_entries": len(_service_cache),
        "valid_entries": valid_entries,
        "expired_entries": expired_entries,
        "cache_ttl_minutes": _cache_ttl.total_seconds() / 60
    }