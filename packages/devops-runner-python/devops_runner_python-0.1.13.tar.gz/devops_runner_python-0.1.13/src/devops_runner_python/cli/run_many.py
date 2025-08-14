import shutil
import subprocess
from typing import List
from ..discovery import find_python_projects
from ..env import load_env_vars, validate_env_vars
from colorama import Fore, Style


def run_many(script_name: str, env: str, kill_others_on_fail: bool = False, script_args: List[str] = None) -> int:
    """
    Run a script concurrently in all projects that define it.
    
    Args:
        script_name: The name of the script to run
        kill_others_on_fail: Whether to kill other processes if one fails
        script_args: Additional arguments to pass to the script
        
    Returns:
        0 if all scripts executed successfully, 1 otherwise
    """
    if script_args is None:
        script_args = []
    
    # Check if GNU parallel is installed
    if shutil.which('parallel') is None:
        print("Error: GNU parallel is not installed. Please install it to use the run-many command.")
        print("On macOS: brew install parallel")
        print("On Ubuntu/Debian: apt-get install parallel")
        print("On CentOS/RHEL: yum install parallel")
        return 1
    
    # Find all projects
    projects = find_python_projects()
    
    # Filter projects that have the specified script
    matching_projects = []
    for _project_name, project in projects.items():
        if script_name in project.scripts:
            matching_projects.append(project)
    
    if not matching_projects:
        print(f"No projects found with script '{script_name}'.")
        return 0
    
    print(f"Found {len(matching_projects)} projects with script '{script_name}':")
    for project in matching_projects:
        print(f"  - {project.name} ({project.path})")
    print()
    
    # Prepare the command for GNU parallel
    project_names = [project.name for project in matching_projects]
    
    # Base command
    parallel_cmd = [
        "parallel", 
        "--link", 
        "--tagstring", 
        "[{1}]",
        "--line-buffer"
    ]
    
    # Add halt option if kill_others_on_fail is True
    if kill_others_on_fail:
        parallel_cmd.extend(["--halt", "now,fail=1"])
    
    # Add the command to execute
    script_cmd = f"uv run devopspy run {{1}}:{script_name}"
    
    # Add script arguments if provided
    if script_args:
        script_args_str = ' '.join(script_args)
        script_cmd += f" {script_args_str}"
    
    parallel_cmd.append(script_cmd)
    
    # Add the project names, paths, and script
    parallel_cmd.extend([":::", *project_names])
    
    print(f"{Fore.YELLOW}Executing: {' '.join(parallel_cmd)}\n{Style.RESET_ALL}")
    
    try:
        # Load environment variables
        load_env_vars(env)
        
        # Validate environment variables against env.yaml files
        if not validate_env_vars():
            print(f"{Fore.RED}Environment validation failed. Aborting command.{Style.RESET_ALL}")
            return 1
        
        result = subprocess.run(parallel_cmd, check=False)
        return result.returncode
    except Exception as e:
        print(f"Error executing parallel command: {e}")
        return 1