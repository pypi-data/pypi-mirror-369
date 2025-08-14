from doogat.core.domain.entities.project.project import ProjectZettel
from buvis.pybase.adapters.jira.domain.jira_issue_dto import JiraIssueDTO


class ProjectZettelJiraIssueDTOAssembler:
    def __init__(self, defaults: dict = None):
        self.defaults = defaults or {}

    def to_dto(self, source: ProjectZettel) -> JiraIssueDTO:
        if not self.defaults.get("project"):
            raise ValueError("Default project is required")
        else:
            project = self.defaults["project"]

        if not self.defaults.get("region"):
            raise ValueError("Default region is required")
        else:
            region = self.defaults["region"]

        if not self.defaults.get("user"):
            raise ValueError("Default user is required")
        else:
            user = self.defaults["user"]

        if not self.defaults.get("team"):
            raise ValueError("Default team is required")
        else:
            team = self.defaults["team"]

        if source.deliverable == "enhancement":
            issue_type = self.defaults["enhancements"]["issue_type"]
            feature = self.defaults["enhancements"]["feature"]
            labels = self.defaults["enhancements"]["labels"].split(",")
            priority = self.defaults["enhancements"]["priority"]
        else:
            issue_type = self.defaults["bugs"]["issue_type"]
            feature = self.defaults["bugs"]["feature"]
            labels = self.defaults["bugs"]["labels"].split(",")
            priority = self.defaults["bugs"]["priority"]

        description = "No description provided"

        for section in source._data.sections:
            title, content = section
            if title == "## Description":
                description = content.strip()

        ticket_references = _get_ticket_references(source)

        if ticket_references != "":
            description += f"\n\n{ticket_references}"

        title = source.title

        if "pex" in source.tags:
            title = f"PEX: {title}"

        return JiraIssueDTO(
            project=project,
            title=title,
            description=description,
            issue_type=issue_type,
            labels=labels,
            priority=priority,
            ticket=source.ticket,
            feature=feature,
            assignee=user,
            reporter=user,
            team=team,
            region=region,
        )


def _get_ticket_references(source):
    ref_text = ""

    if hasattr(source, "ticket") and source.ticket is not None:
        ref_text = f"This solves SR {source.ticket}."

    if hasattr(source, "ticket_related") and source.ticket_related is not None:
        ticket_list = sorted(source.ticket_related.split(" "))

        if len(ticket_list) > 1:
            if len(ticket_list) == 2:
                ticket_list_str = " and ".join(ticket_list)
            else:
                ticket_list_str = (
                    ", ".join(ticket_list[:-1]) + ", and " + ticket_list[-1]
                )
                ref_text += f" Related SRs: {ticket_list_str}."
        else:
            ref_text += f" Related SR: {source.ticket_related}."

    return ref_text
