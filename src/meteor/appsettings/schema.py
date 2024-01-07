from meteor.models import MeteorBase


class AppSetting(MeteorBase):
    key: str
    value: str
    description: str
    type: str
