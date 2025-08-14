import os
import glob
import tomli
from typing import Dict, Any
from pydantic import BaseModel
from colorama import Fore, Style

class Project(BaseModel):
    name: str
    path: str
    scripts: Dict[str, str]
    deployment: dict[str, Any]

_projects: Dict[str, Project] | None = None

def find_python_projects() -> Dict[str, Project]:
    """
    Finds all pyproject.toml files under the monorepo root directory
    and creates a dictionary mapping project names to their paths and scripts.
    
    Returns:
        A dictionary mapping project names to tuples containing:
        - The directory path
        - A dictionary of script names to their entry points
    """
    global _projects

    if _projects is not None:
        return _projects

    base_dir = os.getenv("MONOREPO_ROOT", os.getcwd())

    # Find all pyproject.toml files recursively
    pattern = os.path.join(base_dir, "**/pyproject.toml")
    pyproject_files = glob.glob(pattern, recursive=True)
    
    projects = {}
    
    for pyproject_path in pyproject_files:
        pyproject_dir = os.path.dirname(pyproject_path)
        if base_dir == pyproject_dir or 'venv/' in pyproject_dir or 'node_modules/' in pyproject_dir:
            continue

        try:
            # Read and parse the pyproject.toml file
            with open(pyproject_path, "rb") as f:
                pyproject_data = tomli.load(f)
            
            # Extract the project name if it exists
            if "project" in pyproject_data and "name" in pyproject_data["project"]:
                project_name = pyproject_data["project"]["name"]
                
                # Extract scripts if they exist
                scripts = pyproject_data.get("tool", {}).get("devops", {}).get("scripts", {})

                # Extract deployment configuration if it exists
                deployment = pyproject_data.get("tool", {}).get("devops", {}).get("deployment", {})
                
                # Store the directory containing the pyproject.toml file and its scripts
                projects[project_name] = Project(
                    name=project_name, 
                    path=pyproject_dir, 
                    scripts=scripts,
                    deployment=deployment
                )
        except Exception as e:
            # Skip files that can't be parsed
            print(f"Error processing {pyproject_path}: {e}")
    
    print(f"{Fore.YELLOW}Workspace Discovery initialized in {base_dir}. Workspaces found: {', '.join(projects.keys())}{Style.RESET_ALL}")

    _projects = projects
    return projects


def get_port_for_service_name(service_name: str) -> int | None:
    """
    Returns the port for the given service name, or None if not found.
    Iterates the discovered projects and returns as soon as a match is found.
    """
    projects = find_python_projects()
    for project in projects.values():
        svc_name = project.deployment.get("service_name")
        if svc_name != service_name:
            continue
        port = project.deployment.get("port")
        if port is None:
            continue
        try:
            return int(port)
        except (TypeError, ValueError):
            raise ValueError(f"Invalid port value for service {service_name}: {port}")
    return None
