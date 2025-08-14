import os
import subprocess
from typing import List, Optional
from ..discovery import find_python_projects
from ..env import load_env_vars, validate_env_vars
from colorama import Fore, Style
import shlex


def run(script_spec: str, env: str, script_args: List[str] = None) -> int:
    """
    Execute a script from a project's scripts.
    
    Args:
        script_spec: String in the format "x:y" where x is a project name and y is a script name
        script_args: Additional arguments to pass to the script
        
    Returns:
        The exit code of the executed script
    """
    if script_args is None:
        script_args = []
    if ":" not in script_spec:
        print(f"Error: Invalid script specification '{script_spec}'. Expected format 'project:script'")
        return 1
    
    project_name, script_name = script_spec.split(":", 1)
    
    # Find all projects
    projects = find_python_projects()
    
    if project_name not in projects:
        print(f"Error: Project '{project_name}' not found. Available projects: {', '.join(projects.keys())}")
        return 1
    
    project = projects[project_name]
    
    if not project.scripts or script_name not in project.scripts:
        print(f"Error: Script '{script_name}' not found in project '{project_name}'.")
        if project.scripts:
            print(f"Available scripts: {', '.join(project.scripts.keys())}")
        else:
            print(f"No scripts defined in project '{project_name}'.")
        return 1

    script_str = project.scripts[script_name]
    script_commands = shlex.split(script_str)
    
    # Load environment variables
    load_env_vars(env)
    
    # Validate environment variables against env.yaml files
    if not validate_env_vars():
        print(f"{Fore.RED}Environment validation failed. Aborting command.{Style.RESET_ALL}")
        return 1
    
    # Change to the project directory
    original_dir = os.getcwd()
    os.chdir(project.path)
    
    try:
        
        # Execute the script using uv run
        cmd = ["uv", "run", *script_commands]
        
        # Add any script arguments
        if script_args:
            cmd.extend(script_args)
            
        print(f"{Fore.YELLOW}Executing: {' '.join(cmd)} in {project.path}\n{Style.RESET_ALL}")
        
        # Run the command
        result = subprocess.run(cmd, check=False)
        return result.returncode
    except Exception as e:
        print(f"Error executing script: {e}")
        return 1
    finally:
        # Restore the original directory
        os.chdir(original_dir)
