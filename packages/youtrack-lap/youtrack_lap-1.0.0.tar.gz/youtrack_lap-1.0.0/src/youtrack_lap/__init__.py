"""YouTrack REST Client - A limited client library for accessing YouTrack REST API."""

from .connection import Connection
from .issueCollection import IssueCollection
from .issueResource import IssueResource
from .projectCollection import ProjectsCollection
from .projectResource import ProjectsResource

__version__ = "1.0.0"
__all__ = ["Connection", "IssueCollection", "IssueResource", "ProjectsCollection", "ProjectsResource"]