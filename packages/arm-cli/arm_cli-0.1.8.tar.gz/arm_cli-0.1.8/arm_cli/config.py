import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional

import appdirs
from pydantic import BaseModel


class ProjectConfig(BaseModel):
    """Configuration schema for individual projects."""

    name: str
    description: Optional[str] = None
    project_directory: Optional[str] = None
    docker_compose_file: Optional[str] = None
    data_directory: Optional[str] = None


class AvailableProject(BaseModel):
    """Schema for available project entry."""

    name: str
    path: str


class Config(BaseModel):
    """Configuration schema for the CLI."""

    active_project: str = ""
    available_projects: List[AvailableProject] = []


def get_config_dir() -> Path:
    """Get the configuration directory for the CLI."""
    config_dir = Path(appdirs.user_config_dir("arm-cli"))
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_config_file() -> Path:
    """Get the path to the configuration file."""
    return get_config_dir() / "config.json"


def get_default_project_config_path() -> Path:
    """Get the path to the default project configuration in the repository."""
    # First try to find it relative to the current file (development)
    current_file = Path(__file__)
    dev_path = current_file.parent.parent / "resources" / "default_project_config.json"

    if dev_path.exists():
        return dev_path

    # If not found in development, try to find it in the installed package
    try:
        import arm_cli

        package_dir = Path(arm_cli.__file__).parent
        # When installed, the resources directory is at the root level of the package
        installed_path = package_dir.parent / "resources" / "default_project_config.json"

        if installed_path.exists():
            return installed_path
    except ImportError:
        pass

    # Fallback: try to find it in the current working directory
    cwd_path = Path.cwd() / "resources" / "default_project_config.json"
    if cwd_path.exists():
        return cwd_path

    raise FileNotFoundError("Could not find default_project_config.json in any expected location")


def copy_default_project_config() -> Path:
    """Copy the default project config from repository to user config directory."""
    config_dir = get_config_dir()
    default_config_path = get_default_project_config_path()
    user_config_path = config_dir / "default_project_config.json"

    if not default_config_path.exists():
        raise FileNotFoundError(f"Default project config not found at {default_config_path}")

    shutil.copy2(default_config_path, user_config_path)
    return user_config_path


def load_project_config(project_path: str) -> ProjectConfig:
    """Load a project configuration from file."""
    config_path = Path(project_path)

    # If it's a relative path, make it relative to the config directory
    if not config_path.is_absolute():
        config_path = get_config_dir() / config_path

    if not config_path.exists():
        raise FileNotFoundError(f"Project config not found at {config_path}")

    with open(config_path, "r") as f:
        data = json.load(f)
    return ProjectConfig(**data)


def add_project_to_list(config: Config, project_path: str, project_name: str) -> None:
    """Add a project to the available projects list and set as active."""
    # Remove existing entry if it exists
    config.available_projects = [p for p in config.available_projects if p.path != project_path]

    # Add new entry
    project_entry = AvailableProject(name=project_name, path=project_path)
    config.available_projects.append(project_entry)

    # Set as active project
    config.active_project = project_path


def get_available_projects(config: Config) -> List[AvailableProject]:
    """Get the list of available projects."""
    # If no projects are available, ensure the default project is added
    if not config.available_projects:
        try:
            default_path = copy_default_project_config()
            default_project_config = load_project_config(str(default_path))
            add_project_to_list(config, str(default_path), default_project_config.name)
        except Exception as e:
            print(f"Error setting up default project: {e}")

    return config.available_projects


def activate_project(config: Config, project_identifier: str) -> Optional[ProjectConfig]:
    """Activate a project by path or name."""
    # First try to find by exact path
    for project in config.available_projects:
        if project.path == project_identifier:
            config.active_project = project.path
            save_config(config)
            return load_project_config(project.path)

    # Try to find by name
    for project in config.available_projects:
        if project.name.lower() == project_identifier.lower():
            config.active_project = project.path
            save_config(config)
            return load_project_config(project.path)

    return None


def remove_project_from_list(config: Config, project_identifier: str) -> bool:
    """Remove a project from the available projects list by path or name."""
    # First try to find by exact path
    for project in config.available_projects:
        if project.path == project_identifier:
            # If this is the active project, clear the active project
            if config.active_project == project.path:
                config.active_project = ""
            config.available_projects.remove(project)
            return True

    # Try to find by name
    for project in config.available_projects:
        if project.name.lower() == project_identifier.lower():
            # If this is the active project, clear the active project
            if config.active_project == project.path:
                config.active_project = ""
            config.available_projects.remove(project)
            return True

    return False


def load_config() -> Config:
    """Load configuration from file, creating default if it doesn't exist."""
    config_file = get_config_file()

    if not config_file.exists():
        # Create default config
        default_config = Config()
        save_config(default_config)
        return default_config

    try:
        with open(config_file, "r") as f:
            data = json.load(f)
        return Config(**data)
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        # If config is corrupted, create a new one
        print(f"Warning: Config file corrupted, creating new default config: {e}")
        default_config = Config()
        save_config(default_config)
        return default_config


def save_config(config: Config) -> None:
    """Save configuration to file."""
    config_file = get_config_file()

    # Ensure directory exists
    config_file.parent.mkdir(parents=True, exist_ok=True)

    with open(config_file, "w") as f:
        json.dump(config.model_dump(), f, indent=2)


def get_active_project_config(config: Config) -> Optional[ProjectConfig]:
    """Get the active project configuration."""
    if not config.active_project:
        # No active project set, copy default and set it
        try:
            default_path = copy_default_project_config()
            config.active_project = str(default_path)

            # Also add the default project to available projects if not already there
            default_project_config = load_project_config(str(default_path))
            add_project_to_list(config, str(default_path), default_project_config.name)

            return default_project_config
        except Exception as e:
            print(f"Error setting up default project config: {e}")
            return None

    try:
        return load_project_config(config.active_project)
    except FileNotFoundError:
        print(f"Active project config not found at {config.active_project}")
        return None
    except IsADirectoryError:
        print(f"Active project config path is a directory: {config.active_project}")
        return None


def print_no_projects_message() -> None:
    """Print the standard message when no projects are available."""
    print("No projects available. Use 'arm-cli projects init <path>' to add a project.")


def print_available_projects(config: Config) -> None:
    """Print the list of available projects."""
    available_projects = get_available_projects(config)
    if available_projects:
        print("Available projects:")
        for i, proj in enumerate(available_projects, 1):
            print(f"  {i}. {proj.name} ({proj.path})")
    else:
        print_no_projects_message()
