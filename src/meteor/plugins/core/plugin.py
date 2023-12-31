"""
.. module: meteor.plugins.meteor_core.plugin
    :platform: Unix
    :copyright: (c) 2024 by MeteorFlow, see AUTHORS for more
    :license: Apache, see LICENSE for more details.
"""
import base64
import json
import logging

import requests
from fastapi import HTTPException
from fastapi.security.utils import get_authorization_scheme_param
from jose import JWTError, jwt
from jose.exceptions import JWKError
from starlette.requests import Request
from starlette.status import HTTP_401_UNAUTHORIZED

from meteor.config import (
    METEOR_AUTHENTICATION_PROVIDER_HEADER_NAME,
    METEOR_AUTHENTICATION_PROVIDER_PKCE_JWKS,
    METEOR_JWT_AUDIENCE,
    METEOR_JWT_EMAIL_OVERRIDE,
    METEOR_JWT_SECRET,
    METEOR_PKCE_DONT_VERIFY_AT_HASH,
)
from meteor.database.core import Base

from meteor.plugins import core as meteor_plugin
from meteor.plugins.bases import (
    AuthenticationProviderPlugin,
)


log = logging.getLogger(__name__)


class BasicAuthProviderPlugin(AuthenticationProviderPlugin):
    title = "Meteor Plugin - Basic Authentication Provider"
    slug = "meteor-auth-provider-basic"
    description = "Generic basic authentication provider."
    version = meteor_plugin.__version__

    author = "MeteorFlow"
    author_url = "https://github.com/meteorflow/meteor.git"

    def get_current_user(self, request: Request, **kwargs):
        authorization: str = request.headers.get("Authorization")
        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            log.exception(
                f"Malformed authorization header. Scheme: {scheme} Param: {param} Authorization: {authorization}"
            )
            return

        token = authorization.split()[1]

        try:
            data = jwt.decode(token, METEOR_JWT_SECRET)
        except (JWKError, JWTError):
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail=[{"msg": "Could not validate credentials"}],
            ) from None
        return data["email"]


class PKCEAuthProviderPlugin(AuthenticationProviderPlugin):
    title = "Meteor Plugin - PKCE Authentication Provider"
    slug = "meteor-auth-provider-pkce"
    description = "Generic PCKE authentication provider."
    version = meteor_plugin.__version__

    author = "MeteorFlow"
    author_url = "https://github.com/meteorflow/meteor.git"

    def get_current_user(self, request: Request, **kwargs):
        credentials_exception = HTTPException(
            status_code=HTTP_401_UNAUTHORIZED, detail=[{"msg": "Could not validate credentials"}]
        )

        authorization: str = request.headers.get("Authorization", request.headers.get("authorization"))
        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            raise credentials_exception

        token = authorization.split()[1]

        # Parse out the Key information. Add padding just in case
        key_info = json.loads(base64.b64decode(token.split(".")[0] + "=========").decode("utf-8"))

        # Grab all possible keys to account for key rotation and find the right key
        keys = requests.get(METEOR_AUTHENTICATION_PROVIDER_PKCE_JWKS).json()["keys"]
        for potential_key in keys:
            if potential_key["kid"] == key_info["kid"]:
                key = potential_key

        try:
            jwt_opts = {}
            if METEOR_PKCE_DONT_VERIFY_AT_HASH:
                jwt_opts = {"verify_at_hash": False}
            # If METEOR_JWT_AUDIENCE is defined, the we must include audience in the decode
            if METEOR_JWT_AUDIENCE:
                data = jwt.decode(token, key, audience=METEOR_JWT_AUDIENCE, options=jwt_opts)
            else:
                data = jwt.decode(token, key, options=jwt_opts)
        except JWTError as err:
            log.debug("JWT Decode error: {}".format(err))
            raise credentials_exception from err

        # Support overriding where email is returned in the id token
        if METEOR_JWT_EMAIL_OVERRIDE:
            return data[METEOR_JWT_EMAIL_OVERRIDE]
        else:
            return data["email"]


class HeaderAuthProviderPlugin(AuthenticationProviderPlugin):
    title = "Meteor Plugin - HTTP Header Authentication Provider"
    slug = "meteor-auth-provider-header"
    description = "Authenticate users based on HTTP request header."
    version = meteor_plugin.__version__

    author = "Filippo Giunchedi"
    author_url = "https://github.com/filippog"

    def get_current_user(self, request: Request, **kwargs):
        value: str = request.headers.get(METEOR_AUTHENTICATION_PROVIDER_HEADER_NAME)
        if not value:
            log.error(f"Unable to authenticate. Header {METEOR_AUTHENTICATION_PROVIDER_HEADER_NAME} not found.")
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)
        return value
