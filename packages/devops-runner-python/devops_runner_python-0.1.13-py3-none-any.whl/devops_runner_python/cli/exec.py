import os
import subprocess
from typing import List
from ..discovery import find_python_projects
from ..env import load_env_vars
from colorama import Fore, Style


def exec(project_name: str, env: str, command: List[str] = None) -> int:
    """
    Execute a command in a project's directory.
    
    Args:
        project_name: Name of the project to execute the command in
        command: Command to execute and its arguments
        
    Returns:
        The exit code of the executed command
    """
    if not command:
        print(f"Error: No command specified to execute in project '{project_name}'")
        return 1

    # Find all projects
    projects = find_python_projects()
    
    if project_name not in projects:
        print(f"Error: Project '{project_name}' not found. Available projects: {', '.join(projects.keys())}")
        return 1
    
    project = projects[project_name]
    
    # Change to the project directory
    original_dir = os.getcwd()
    os.chdir(project.path)
    
    try:
        # Load environment variables
        load_env_vars(env, original_dir)
        
        print(f"{Fore.YELLOW}Executing: {' '.join(command)} in {project.path}\n{Style.RESET_ALL}")
        
        # Run the command
        result = subprocess.run(command, check=False)
        return result.returncode
    except Exception as e:
        print(f"Error executing command: {e}")
        return 1
    finally:
        # Restore the original directory
        os.chdir(original_dir)