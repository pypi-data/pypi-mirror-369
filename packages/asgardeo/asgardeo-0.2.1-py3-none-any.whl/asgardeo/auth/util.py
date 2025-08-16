import base64
import hashlib
import os
import secrets
from typing import Any, Dict, Tuple
from urllib.parse import urlencode


def generate_pkce_pair() -> Tuple[str, str]:
    """
    Generate PKCE code verifier and code challenge pair
    Returns:
        Tuple of (code_verifier, code_challenge)
    """
    # Generate code verifier (43-128 characters)
    code_verifier = (
        base64.urlsafe_b64encode(secrets.token_bytes(32)).decode("utf-8").rstrip("=")
    )

    # Generate code challenge (SHA256 hash of verifier)
    code_challenge = (
        base64.urlsafe_b64encode(hashlib.sha256(code_verifier.encode("utf-8")).digest())
        .decode("utf-8")
        .rstrip("=")
    )

    return code_verifier, code_challenge

def generate_state() -> str:
    """Generate a secure random state parameter."""
    return base64.urlsafe_b64encode(os.urandom(16)).decode('utf-8').rstrip('=')


def build_authorization_url(base_url: str, params: Dict[str, Any]) -> str:
    """Build authorization URL with parameters."""
    return f"{base_url}?{urlencode(params)}"
