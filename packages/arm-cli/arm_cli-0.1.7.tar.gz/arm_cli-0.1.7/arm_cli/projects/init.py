import sys
from pathlib import Path
from typing import Optional

import click

from arm_cli.config import (
    add_project_to_list,
    copy_default_project_config,
    load_project_config,
    save_config,
)


def _init(ctx, project_path: str, name: Optional[str] = None):
    """Initialize a new project from an existing directory"""
    config = ctx.obj["config"]

    project_path_obj = Path(project_path).resolve()

    if name is None:
        name = project_path_obj.name

    # Check if project config already exists
    project_config_file = project_path_obj / "project_config.json"

    if project_config_file.exists():
        print(f"Project config already exists at {project_config_file}")
        print("Loading existing project configuration...")
        project_config = load_project_config(str(project_config_file))
    else:
        # Copy default config and customize it
        try:
            default_config_path = copy_default_project_config()
            with open(default_config_path, "r") as f:
                import json

                default_data = json.load(f)

            # Update with project-specific information
            default_data["name"] = name
            default_data["project_directory"] = str(project_path_obj)

            # Save the new project config
            with open(project_config_file, "w") as f:
                json.dump(default_data, f, indent=2)

            project_config = load_project_config(str(project_config_file))
            print(f"Created new project configuration at {project_config_file}")

        except Exception as e:
            print(f"Error creating project configuration: {e}")
            sys.exit(1)

    # Add to available projects and set as active
    add_project_to_list(config, str(project_config_file), project_config.name)
    save_config(config)

    print(f"Project '{project_config.name}' initialized and set as active")
    print(f"Project directory: {project_config.project_directory}")


# Create the command object
init = click.command(name="init")(
    click.argument("project_path", type=click.Path(exists=True, file_okay=False, dir_okay=True))(
        click.option("--name", help="Name for the project (defaults to directory name)")(
            click.pass_context(_init)
        )
    )
)
