from pydantic.errors import PydanticUserError


class MeteorException(Exception):
    pass


class MeteorPluginException(MeteorException):
    pass


class NotFoundError(PydanticUserError):
    code = "not_found"
    msg_template = "{msg}"


class FieldNotFoundError(PydanticUserError):
    code = "not_found.field"
    msg_template = "{msg}"


class ModelNotFoundError(PydanticUserError):
    code = "not_found.model"
    msg_template = "{msg}"


class ExistsError(PydanticUserError):
    code = "exists"
    msg_template = "{msg}"


class InvalidConfigurationError(PydanticUserError):
    code = "invalid.configuration"
    msg_template = "{msg}"


class InvalidFilterError(PydanticUserError):
    code = "invalid.filter"
    msg_template = "{msg}"


class InvalidUsernameError(PydanticUserError):
    code = "invalid.username"
    msg_template = "{msg}"


class InvalidPasswordError(PydanticUserError):
    code = "invalid.password"
    msg_template = "{msg}"
