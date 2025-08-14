"""Output formatters for Taiga tasks."""

from rich import box
from rich.console import Console
from rich.table import Table


class TaskFormatter:
    def __init__(self):
        self.console = Console()

    def display_projects(self, projects):
        """Display list of found projects."""
        self.console.print("\nFound projects:", style="cyan")
        projects_names = [project.name for project in projects]
        self.console.print("\n".join(f"  • {name}" for name in projects_names))
        self.console.print()

    def display_project_tasks_table(self, project_name, items):
        """Display tasks for a single project in table format."""
        self.console.print(f"\n[bold blue]Project: {project_name}[/bold blue]")

        table = Table(show_header=True, box=box.ROUNDED)
        table.add_column("Type", style="yellow")
        table.add_column("ID", style="cyan")
        table.add_column("Status", style="magenta")
        table.add_column("Item", style="green")
        table.add_column("URL", style="blue")

        for item in items:
            item_type = "Story" if item["type"] == "user_story" else "Task"
            item_url = f"https://support.abstract-technology.de/project/{item['project_slug']}/{'us' if item['type'] == 'user_story' else 'task'}/{item['ref']}"  # noqa: E501
            table.add_row(
                item_type,
                str(item["ref"]),
                item["status_extra_info"]["name"],
                item["subject"],
                item_url,
            )

        self.console.print(table)

    def display_project_tasks_simple(self, project_name, items):
        """Display tasks for a single project in simple format."""
        self.console.print(f"\n[bold blue]Project: {project_name}[/bold blue]\n")

        for item in items:
            item_type = (
                "[yellow]Story[/yellow]"
                if item["type"] == "user_story"
                else "[yellow]Task[/yellow]"
            )
            item_url = f"https://support.abstract-technology.de/project/{item['project_slug']}/{'us' if item['type'] == 'user_story' else 'task'}/{item['ref']}"  # noqa: E501
            self.console.print(
                f"{item_type} [green]-[/green] {item['subject']} - "
                f"[blue]{item_url}[/blue] - "
                f"[magenta]{item['status_extra_info']['name']}[/magenta]"
            )
