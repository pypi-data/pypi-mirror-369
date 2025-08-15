from .jwt_config import (
    JwtConfig, JwtDbConfig, JwtAlgorithm
)
from .jwt_external import (
    provider_register, provider_get_token
)
from .jwt_pomes import (
    jwt_needed, jwt_verify_request,
    jwt_assert_account, jwt_set_account, jwt_remove_account,
    jwt_issue_token, jwt_issue_tokens, jwt_refresh_tokens,
    jwt_get_claims, jwt_validate_token, jwt_revoke_token
)

__all__ = [
    # jwt_constants
    "JwtConfig", "JwtDbConfig", "JwtAlgorithm",
    # jwt_external
    "provider_register", "provider_get_token",
    # jwt_pomes
    "jwt_needed", "jwt_verify_request",
    "jwt_assert_account", "jwt_set_account", "jwt_remove_account",
    "jwt_issue_token", "jwt_issue_tokens", "jwt_refresh_tokens",
    "jwt_get_claims", "jwt_validate_token", "jwt_revoke_token"
]

from importlib.metadata import version
__version__ = version("pypomes_jwt")
__version_info__ = tuple(int(i) for i in __version__.split(".") if i.isdigit())
