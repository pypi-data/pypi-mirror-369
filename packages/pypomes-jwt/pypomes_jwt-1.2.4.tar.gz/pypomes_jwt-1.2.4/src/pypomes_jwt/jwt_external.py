import requests
import sys
from base64 import b64encode
from datetime import datetime
from logging import Logger
from pypomes_core import TZ_LOCAL, Mimetype, exc_format
from requests import Response
from typing import Any

# structure:
# {
#    <provider-id>: {
#      "url": <access-url>,
#      "grant-type": <type-of-grant-to-request>,
#      "user": <basic-auth-user>,
#      "pwd": <basic-auth-pwd>,
#      "token": <auth-token>,
#      "expiration": <timestamp>
#    }
# }
_provider_registry: dict[str, dict[str, Any]] = {}


def provider_register(provider_id: str,
                      access_url: str,
                      grant_type: str,
                      auth_user: str,
                      auth_pwd: str,
                      client_id: str = None,
                      use_header: bool = None) -> None:
    """
    Register an external token provider.

    :param provider_id: the provider's identification
    :param grant_type: the type of grant to request (typically, 'client_credentials' or 'password')
    :param access_url: the url to request tokens with
    :param auth_user: the basic authorization user
    :param auth_pwd: the basic authorization password
    :param client_id: optional client id to add to the request body
    :param use_header: use HTTP header on the request
    """
    global _provider_registry  # noqa: PLW0602
    _provider_registry[provider_id] = {
        "url": access_url,
        "grant_type": grant_type,
        "user": auth_user,
        "pwd": auth_pwd,
        "client_id": client_id,
        "use_header": use_header,
        "token": None,
        "expiration": datetime.now(tz=TZ_LOCAL).timestamp()
    }


def provider_get_token(errors: list[str] | None,
                       provider_id: str,
                       logger: Logger = None) -> str | None:
    """
    Obtain an authentication token from the external provider *provider_id*.

    :param errors: incidental error messages
    :param provider_id: the provider's identification
    :param logger: optional logger
    """
    # initialize the return variable
    result: str | None = None

    global _provider_registry  # noqa: PLW0602
    err_msg: str | None = None
    provider: dict[str, Any] = _provider_registry.get(provider_id)
    if provider:
        now: float = datetime.now(tz=TZ_LOCAL).timestamp()
        if now > provider.get("expiration"):
            data: dict[str, str] = {"grant_type": provider.get("grant-type")}
            headers: dict[str, str] = {"Content-Type": Mimetype.URLENCODED}
            user: str = provider.get("user")
            pwd: str = provider.get("pwd")
            if provider.get("use_header"):
                enc_bytes: bytes = b64encode(f"{user}:{pwd}".encode())
                headers["Authorization"] = f"Basic {enc_bytes.decode()}"
            else:
                data["username"] = user
                data["password"] = pwd
                if provider.get("client_id"):
                    data["client_id"] = provider.get("client_id")
            url: str = provider.get("url")
            try:
                # typical return on a token request:
                # {
                #   "expires_in": <number-of-seconds>,
                #   "token_type": "bearer",
                #   "access_token": <the-token>
                # }
                response: Response = requests.post(url=url,
                                                   data=data,
                                                   headers=headers,
                                                   timeout=None)
                if response.status_code < 200 or response.status_code >= 300:
                    # request resulted in error, report the problem
                    err_msg = (f"POST '{url}': failed, "
                               f"status {response.status_code}, reason '{response.reason}'")
                else:
                    reply: dict[str, Any] = response.json()
                    provider["token"] = reply.get("access_token")
                    provider["expiration"] = now + int(reply.get("expires_in"))
                    if logger:
                        logger.debug(msg=f"POST '{url}': status "
                                         f"{response.status_code}, reason '{response.reason}')")
            except Exception as e:
                # the operation raised an exception
                err_msg = exc_format(exc=e,
                                     exc_info=sys.exc_info())
                err_msg = f"POST '{url}': error, '{err_msg}'"
    else:
        err_msg: str = f"Provider '{provider_id}' not registered"

    if err_msg:
        if isinstance(errors, list):
            errors.append(err_msg)
        if logger:
            logger.error(msg=err_msg)
    else:
        result = provider.get("token")

    return result


