from enum import Enum


class MeteorEnum(str, Enum):
    def __str__(self) -> str:
        return str.__str__(self)


class Visibility(MeteorEnum):
    open = "Open"
    restricted = "Restricted"


# class SearchTypes(ApiEnum):
#     definition = "Definition"
#     document = "Document"
#     incident = "Incident"
#     incident_priority = "IncidentPriority"
#     incident_type = "IncidentType"
#     individual_contact = "IndividualContact"
#     plugin = "Plugin"
#     query = "Query"
#     search_filter = "SearchFilter"
#     case = "Case"
#     service = "Service"
#     source = "Source"
#     tag = "Tag"
#     task = "Task"
#     team_contact = "TeamContact"
#     term = "Term"


class UserRoles(MeteorEnum):
    owner = "Owner"
    manager = "Manager"
    admin = "Admin"
    member = "Member"
