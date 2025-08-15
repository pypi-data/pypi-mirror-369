import click

from arm_cli.config import get_active_project_config


def _info(ctx, field):
    """Show information about the active project"""
    config = ctx.obj["config"]

    # Get the active project configuration
    project_config = get_active_project_config(config)
    if not project_config:
        print("No active project configured.")
        return

    # If --field is specified, extract and print only that field
    if field:
        # Convert field name to attribute name (e.g., "project_directory" -> project_directory)
        field = field.lower().replace(" ", "_")

        # Get all public attributes (not starting with _)
        available_attrs = [
            attr
            for attr in dir(project_config)
            if not attr.startswith("_") and not callable(getattr(project_config, attr))
        ]

        if field in available_attrs:
            value = getattr(project_config, field)
            if value:
                print(value)
            else:
                print("", end="")  # Print empty string for empty values
        else:
            print(f"Unknown field: {field}", file=click.get_text_stream("stderr"))
            print(
                f"Available fields: {', '.join(available_attrs)}",
                file=click.get_text_stream("stderr"),
            )
            return
    else:
        # Print all fields as before
        print(f"Active Project: {project_config.name}")
        if project_config.description:
            print(f"Description: {project_config.description}")
        if project_config.project_directory:
            print(f"Project Directory: {project_config.project_directory}")
        if project_config.docker_compose_file:
            print(f"Docker Compose File: {project_config.docker_compose_file}")
        if project_config.data_directory:
            print(f"Data Directory: {project_config.data_directory}")


# Create the command object
info = click.command(name="info")(
    click.option("--field", help="Extract a specific field value")(click.pass_context(_info))
)
