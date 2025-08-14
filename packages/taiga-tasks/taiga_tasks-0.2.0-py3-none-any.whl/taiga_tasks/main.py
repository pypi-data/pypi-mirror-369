#!/usr/bin/env python3
"""Main entry point for Taiga Tasks CLI."""

import sys

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from taiga_tasks.api.client import TaigaClient
from taiga_tasks.cli.commands import handle_list, handle_login, parse_arguments
from taiga_tasks.config import settings
from taiga_tasks.display.formatters import TaskFormatter


def main():
    """Entry point for the CLI."""
    try:
        # Parse command line arguments
        args = parse_arguments()

        # Handle login command
        if args.command == "login":
            handle_login(args)
            return

        # Handle tasks listing (default behavior)
        if not args.command:
            if not handle_list(args):
                return

            # Load configuration
            config = settings.load_config()

            # Initialize Taiga client
            client = TaigaClient(
                host=config["host"],
                username=config["username"],
                password=config["password"],
            )

            # Initialize task formatter
            formatter = TaskFormatter()
            console = Console()

            # First, get and display projects
            projects = client.get_projects()
            formatter.display_projects(projects)

            # Then fetch and display tasks for each project
            tasks_by_project = {}

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
                transient=True,
            ) as progress:
                task_id = progress.add_task("Checking projects...", total=None)

                for project in projects:
                    # Update progress to show current project
                    progress.update(task_id, description=f"Checking {project.name}...")

                    project_name, items = client.get_project_tasks(project)

                    if items:  # Only add and display projects that have items
                        # Stop the progress display temporarily
                        progress.stop()

                        tasks_by_project[project_name] = items
                        # Display items for this project
                        if args.output == "table":
                            formatter.display_project_tasks_table(project_name, items)
                        else:
                            formatter.display_project_tasks_simple(project_name, items)

                        # Resume the progress display
                        progress.start()

    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
