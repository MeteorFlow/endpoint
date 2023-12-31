import base64
import logging
import os
from urllib import parse

from starlette.config import Config

log = logging.getLogger(__name__)

config = Config(".env")

LOG_LEVEL = config("LOG_LEVEL", default=logging.WARNING)

SECRET_PROVIDER = config("SECRET_PROVIDER", default=None)
# if SECRET_PROVIDER == "metatron-secret":
#     import metatron.decrypt

#     class Secret:
#         """
#         Holds a string value that should not be revealed in tracebacks etc.
#         You should cast the value to `str` at the point it is required.
#         """

#         def __init__(self, value: str):
#             self._value = value
#             self._decrypted_value = (
#                 metatron.decrypt.MetatronDecryptor()
#                 .decryptBytes(base64.b64decode(self._value))
#                 .decode("utf-8")
#             )

#         def __repr__(self) -> str:
#             class_name = self.__class__.__name__
#             return f"{class_name}('**********')"

#         def __str__(self) -> str:
#             return self._decrypted_value

if SECRET_PROVIDER == "kms-secret":
    import boto3

    class Secret:
        """
        Holds a string value that should not be revealed in tracebacks etc.
        You should cast the value to `str` at the point it is required.
        """

        def __init__(self, value: str):
            self._value = value
            self._decrypted_value = (
                boto3.client("kms").decrypt(CiphertextBlob=base64.b64decode(value))["Plaintext"].decode("utf-8")
            )

        def __repr__(self) -> str:
            class_name = self.__class__.__name__
            return f"{class_name}('**********')"

        def __str__(self) -> str:
            return self._decrypted_value

else:
    from starlette.datastructures import Secret

# database
DATABASE_HOSTNAME = config("DATABASE_HOSTNAME")
DATABASE_CREDENTIALS = config("DATABASE_CREDENTIALS", cast=Secret)
# this will support special chars for credentials
_DATABASE_CREDENTIAL_USER, _DATABASE_CREDENTIAL_PASSWORD = str(DATABASE_CREDENTIALS).split(":")
_QUOTED_DATABASE_PASSWORD = parse.quote(str(_DATABASE_CREDENTIAL_PASSWORD))
DATABASE_NAME = config("DATABASE_NAME", default="meteor")
DATABASE_PORT = config("DATABASE_PORT", default="5432")
DATABASE_ENGINE_POOL_SIZE = config("DATABASE_ENGINE_POOL_SIZE", cast=int, default=20)
DATABASE_ENGINE_MAX_OVERFLOW = config("DATABASE_ENGINE_MAX_OVERFLOW", cast=int, default=0)
# Deal with DB disconnects
# https://docs.sqlalchemy.org/en/20/core/pooling.html#pool-disconnects
DATABASE_ENGINE_POOL_PING = config("DATABASE_ENGINE_POOL_PING", default=False)
SQLALCHEMY_DATABASE_URI = f"postgresql+psycopg2://{_DATABASE_CREDENTIAL_USER}:{_QUOTED_DATABASE_PASSWORD}@{DATABASE_HOSTNAME}:{DATABASE_PORT}/{DATABASE_NAME}"

ALEMBIC_CORE_REVISION_PATH = config(
    "ALEMBIC_CORE_REVISION_PATH",
    default=f"{os.path.dirname(os.path.realpath(__file__))}/database/revisions/core",
)
ALEMBIC_TENANT_REVISION_PATH = config(
    "ALEMBIC_TENANT_REVISION_PATH",
    default=f"{os.path.dirname(os.path.realpath(__file__))}/database/revisions/tenant",
)
ALEMBIC_INI_PATH = config(
    "ALEMBIC_INI_PATH",
    default=f"{os.path.dirname(os.path.realpath(__file__))}/alembic.ini",
)
ALEMBIC_MULTI_TENANT_MIGRATION_PATH = config(
    "ALEMBIC_MULTI_TENANT_MIGRATION_PATH",
    default=f"{os.path.dirname(os.path.realpath(__file__))}/database/revisions/multi-tenant-migration.sql",
)

# jwt
METEOR_JWT_SECRET = config("METEOR_JWT_SECRET", default=None)
METEOR_JWT_ALG = config("METEOR_JWT_ALG", default="HS256")
METEOR_JWT_EXP = config("METEOR_JWT_EXP", cast=int, default=86400)  # Seconds

METEOR_JWT_AUDIENCE = config("METEOR_JWT_AUDIENCE", default=None)
METEOR_JWT_EMAIL_OVERRIDE = config("METEOR_JWT_EMAIL_OVERRIDE", default=None)

METEOR_AUTHENTICATION_PROVIDER_SLUG = config(
    "METEOR_AUTHENTICATION_PROVIDER_SLUG", default="meteor-auth-provider-basic"
)

if METEOR_AUTHENTICATION_PROVIDER_SLUG == "meteor-auth-provider-pkce":
    if not METEOR_JWT_AUDIENCE:
        log.warn("No JWT Audience specified. This is required for IdPs like Okta")
    if not METEOR_JWT_EMAIL_OVERRIDE:
        log.warn("No JWT Email Override specified. 'email' is expected in the idtoken.")

if METEOR_AUTHENTICATION_PROVIDER_SLUG == "meteor-auth-provider-basic":
    if not METEOR_JWT_SECRET:
        log.warn("No JWT secret specified, this is required if you are using basic authentication.")

METEOR_AUTHENTICATION_PROVIDER_HEADER_NAME = config(
    "METEOR_AUTHENTICATION_PROVIDER_HEADER_NAME", default="remote-user"
)

METEOR_AUTHENTICATION_PROVIDER_PKCE_JWKS = config(
    "METEOR_AUTHENTICATION_PROVIDER_PKCE_JWKS", default=None
)

METEOR_PKCE_DONT_VERIFY_AT_HASH = config("METEOR_PKCE_DONT_VERIFY_AT_HASH", default=False)

METEOR_AUTHENTICATION_DEFAULT_USER = config("METEOR_AUTHENTICATION_DEFAULT_USER", default="meteor@example.com")
