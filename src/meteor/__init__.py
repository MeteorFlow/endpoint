import os
import os.path

# import traceback
from subprocess import check_output

try:
    VERSION = __import__("pkg_resources").get_distribution("meteor").version
except Exception:
    VERSION = "unknown"

# fix is in the works see: https://github.com/mpdavis/python-jose/pull/207
import warnings

warnings.filterwarnings("ignore", message="int_from_bytes is deprecated")

# sometimes we pull version info before meteor is totally installed
# try:
#     from meteor.organization.models import Organization  # noqa lgtm[py/unused-import]
#     from meteor.project.models import Project  # noqa lgtm[py/unused-import]
#     from meteor.route.models import Recommendation  # noqa lgtm[py/unused-import]
#     from meteor.conference.models import Conference  # noqa lgtm[py/unused-import]
#     from meteor.conversation.models import Conversation  # noqa lgtm[py/unused-import]
#     from meteor.definition.models import Definition  # noqa lgtm[py/unused-import]
#     from meteor.document.models import Document  # noqa lgtm[py/unused-import]
#     from meteor.event.models import Event  # noqa lgtm[py/unused-import]
#     from meteor.incident.models import Incident  # noqa lgtm[py/unused-import]
#     from meteor.monitor.models import Monitor  # noqa lgtm[py/unused-import]
#     from meteor.feedback.incident.models import Feedback  # noqa lgtm[py/unused-import]
#     from meteor.feedback.service.models import ServiceFeedback  # noqa lgtm[py/unused-import]
#     from meteor.group.models import Group  # noqa lgtm[py/unused-import]
#     from meteor.incident_cost.models import IncidentCost  # noqa lgtm[py/unused-import]
#     from meteor.incident_cost_type.models import IncidentCostType  # noqa lgtm[py/unused-import]
#     from meteor.incident_role.models import IncidentRole  # noqa lgtm[py/unused-import]
#     from meteor.incident.priority.models import IncidentPriority  # noqa lgtm[py/unused-import]
#     from meteor.incident.severity.models import IncidentSeverity  # noqa lgtm[py/unused-import]
#     from meteor.incident.type.models import IncidentType  # noqa lgtm[py/unused-import]
#     from meteor.individual.models import IndividualContact  # noqa lgtm[py/unused-import]
#     from meteor.notification.models import Notification  # noqa lgtm[py/unused-import]
#     from meteor.participant.models import Participant  # noqa lgtm[py/unused-import]
#     from meteor.participant_role.models import ParticipantRole  # noqa lgtm[py/unused-import]
#     from meteor.plugin.models import Plugin  # noqa lgtm[py/unused-import]
#     from meteor.report.models import Report  # noqa lgtm[py/unused-import]
#     from meteor.service.models import Service  # noqa lgtm[py/unused-import]
#     from meteor.storage.models import Storage  # noqa lgtm[py/unused-import]
#     from meteor.tag.models import Tag  # noqa lgtm[py/unused-import]
#     from meteor.tag_type.models import TagType  # noqa lgtm[py/unused-import]
#     from meteor.task.models import Task  # noqa lgtm[py/unused-import]
#     from meteor.team.models import TeamContact  # noqa lgtm[py/unused-import]
#     from meteor.term.models import Term  # noqa lgtm[py/unused-import]
#     from meteor.ticket.models import Ticket  # noqa lgtm[py/unused-import]
#     from meteor.workflow.models import Workflow  # noqa lgtm[py/unused-import]
#     from meteor.data.source.status.models import SourceStatus  # noqa lgtm[py/unused-import]
#     from meteor.data.source.transport.models import SourceTransport  # noqa lgtm[py/unused-import]
#     from meteor.data.source.type.models import SourceType  # noqa lgtm[py/unused-import]
#     from meteor.data.alert.models import Alert  # noqa lgtm[py/unused-import]
#     from meteor.data.query.models import Query  # noqa lgtm[py/unused-import]
#     from meteor.data.source.models import Source  # noqa lgtm[py/unused-import]
#     from meteor.search_filter.models import SearchFilter  # noqa lgtm[py/unused-impot]
#     from meteor.case.models import Case  # noqa lgtm[py/unused-impot]
#     from meteor.case.priority.models import CasePriority  # noqa lgtm[py/unused-import]
#     from meteor.case.severity.models import CaseSeverity  # noqa lgtm[py/unused-import]
#     from meteor.case.type.models import CaseType  # noqa lgtm[py/unused-import]
#     from meteor.signal.models import Signal  # noqa lgtm[py/unused-import]
# except Exception:
#     traceback.print_exc()


def _get_git_revision(path):
    if not os.path.exists(os.path.join(path, ".git")):
        return None
    try:
        revision = check_output(["git", "rev-parse", "HEAD"], cwd=path, env=os.environ)
    except Exception:
        # binary didn't exist, wasn't on path, etc
        return None
    return revision.decode("utf-8").strip()


def get_revision():
    """
    :returns: Revision number of this branch/checkout, if available. None if
        no revision number can be determined.
    """
    if "METEOR_BUILD" in os.environ:
        return os.environ["METEOR_BUILD"]
    package_dir = os.path.dirname(__file__)
    checkout_dir = os.path.normpath(os.path.join(package_dir, os.pardir, os.pardir))
    path = os.path.join(checkout_dir)
    if os.path.exists(path):
        return _get_git_revision(path)
    return None


def get_version():
    if __build__:
        return f"{__version__}.{__build__}"
    return __version__


def is_docker():
    # One of these environment variables are guaranteed to exist
    # from our official docker images.
    # METEOR_VERSION is from a tagged release, and METEOR_BUILD is from a
    # a git based image.
    return "METEOR_VERSION" in os.environ or "METEOR_BUILD" in os.environ


__version__ = VERSION
__build__ = get_revision()
