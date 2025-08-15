import os
import subprocess
import sys
from pathlib import Path

import click
from click.core import ParameterSource

from arm_cli.config import (
    get_active_project_config,
    get_config_dir,
    load_project_config,
    save_config,
)


@click.group()
def self():
    """Manage the CLI itself"""
    pass


@self.command()
@click.option(
    "--source",
    default=None,
    type=click.Path(exists=True),
    help="Install from a local source path (defaults to current directory if specified without value)",
)
@click.option("-f", "--force", is_flag=True, help="Skip confirmation prompts")
@click.pass_context
def update(ctx, source, force):
    config = ctx.obj["config"]  # noqa: F841 - config available for future use
    """Update arm-cli from PyPI or source"""
    if source is None and ctx.get_parameter_source("source") == ParameterSource.COMMANDLINE:
        source = "."

    if source:
        print(f"Installing arm-cli from source at {source}...")

        if not force:
            if not click.confirm(
                "Do you want to install arm-cli from source? This will clear pip " "cache."
            ):
                print("Update cancelled.")
                return

        # Clear Python import cache
        print("Clearing Python caches...")
        subprocess.run(["rm", "-rf", os.path.expanduser("~/.cache/pip")])
        subprocess.run(["python", "-c", "import importlib; importlib.invalidate_caches()"])

        # Install from the provided source path
        subprocess.run([sys.executable, "-m", "pip", "install", "-e", source], check=True)
        print(f"arm-cli installed from source at {source} successfully!")
    else:
        print("Updating arm-cli from PyPI...")

        if not force:
            if not click.confirm("Do you want to update arm-cli from PyPI?"):
                print("Update cancelled.")
                return

        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "arm-cli"], check=True)
        print("arm-cli updated successfully!")


@self.command()
@click.option("--project", help="Set the active project config file")
@click.option("--list-projects", is_flag=True, help="List all available project config files")
@click.option("--show-project", is_flag=True, help="Show current project configuration")
@click.pass_context
def config(ctx, project, list_projects, show_project):
    """Manage CLI configuration"""
    config = ctx.obj["config"]

    if list_projects:
        config_dir = get_config_dir()
        print("Available project config files:")
        for config_file in config_dir.glob("*.json"):
            if config_file.name != "config.json":  # Skip the main config file
                active_marker = " (active)" if str(config_file) == config.active_project else ""
                print(f"  {config_file.name}{active_marker}")

                # Try to load and show description
                try:
                    project_config = load_project_config(str(config_file))
                    if project_config.description:
                        print(f"    Description: {project_config.description}")
                except Exception:
                    print(f"    (Could not load config)")
        return

    if show_project:
        project_config = get_active_project_config(config)
        if project_config:
            print(f"Active project: {project_config.name}")
            print(f"Config file: {config.active_project}")
            print(f"Description: {project_config.description or 'No description'}")
            print(f"Docker compose file: {project_config.docker_compose_file or 'Not specified'}")
            print(f"Data directory: {project_config.data_directory or 'Not specified'}")

            if project_config.resources:
                print("Resources:")
                for resource_name, resource_path in project_config.resources.items():
                    print(f"  {resource_name}: {resource_path}")

            if project_config.skills:
                print("Skills:")
                for skill_name, skill_path in project_config.skills.items():
                    print(f"  {skill_name}: {skill_path}")

            if project_config.monitoring:
                print("Monitoring:")
                for service_name, service_url in project_config.monitoring.items():
                    print(f"  {service_name}: {service_url}")
        else:
            print("No active project configuration found.")
        return

    if project is not None:
        # Check if the project file exists
        project_path = Path(project)
        if not project_path.is_absolute():
            project_path = get_config_dir() / project_path

        if not project_path.exists():
            print(f"Error: Project config file '{project}' not found.")
            print("Available project config files:")
            config_dir = get_config_dir()
            for config_file in config_dir.glob("*.json"):
                if config_file.name != "config.json":
                    print(f"  {config_file.name}")
            return

        config.active_project = str(project_path)
        save_config(config)
        print(f"Active project set to: {project}")
    else:
        print(f"Active project: {config.active_project or 'None (will use default)'}")
        print("Use --project to set a new active project")
        print("Use --list-projects to see all available project config files")
        print("Use --show-project to see current project configuration")
