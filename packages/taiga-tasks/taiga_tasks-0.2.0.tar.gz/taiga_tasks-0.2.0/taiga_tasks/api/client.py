"""Taiga API client implementation."""

from rich.console import Console
from taiga import TaigaAPI


console = Console()


class TaigaClient:
    def __init__(self, host, username, password):
        """Initialize Taiga client with credentials."""
        self.host = host
        self.api = self._connect(host, username, password)

    def _connect(self, host, username, password):
        """Connect to Taiga API using credentials."""
        try:
            api = TaigaAPI(host=host)
            api.auth(username=username, password=password)
            return api
        except Exception as e:
            raise ValueError(
                f"Failed to connect to Taiga at {host}. Error: {str(e)}"
            ) from e

    def get_projects(self):
        """Get list of all projects."""
        return self.api.projects.list()

    def get_project_tasks(self, project):
        """Fetch tasks and user stories for a single project."""
        # Get both tasks and user stories
        tasks = self.api.tasks.list(project=project.id, assigned_to=self.api.me().id)
        stories = self.api.user_stories.list(
            project=project.id, assigned_users=[self.api.me().id]
        )

        # Format tasks and stories for consistency
        formatted_items = []

        # Format tasks
        for task in tasks:
            try:
                formatted_items.append(
                    {
                        "ref": task.ref,
                        "subject": task.subject,
                        "status_extra_info": task.status_extra_info,
                        "priority_name": getattr(task, "priority_name", "Normal"),
                        "project_id": project.id,
                        "project_name": project.name,
                        "project_slug": project.slug,
                        "type": "task",
                    }
                )
            except Exception as e:
                console.print(
                    f"[red]Error formatting task {task.subject}: {str(e)}[/red]"
                )
                continue

        # Format user stories
        for story in stories:
            try:
                formatted_items.append(
                    {
                        "ref": story.ref,
                        "subject": story.subject,
                        "status_extra_info": story.status_extra_info,
                        "priority_name": "Normal",  # User stories don't have priority
                        "project_id": project.id,
                        "project_name": project.name,
                        "project_slug": project.slug,
                        "type": "user_story",
                    }
                )
            except Exception as e:
                console.print(
                    f"[red]Error formatting user story {story.subject}: {str(e)}[/red]"
                )
                continue

        return project.name, formatted_items
