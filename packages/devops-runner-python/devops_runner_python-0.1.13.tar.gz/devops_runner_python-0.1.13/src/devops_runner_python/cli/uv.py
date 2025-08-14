import os
import subprocess
from ..discovery import find_python_projects
from colorama import Fore, Style


def uv(args: list[str]) -> int:
    """
    Run arbitrary uv commands on all discovered projects sequentially.
    
    Args:
        args: List of arguments to pass to uv
        
    Returns:
        0 if all commands were successful, 1 otherwise
    """
    if not args:
        print("Error: No uv command specified")
        return 1
    
    # Check if pyproject.toml exists in the current directory
    if os.path.exists(os.path.join(os.getcwd(), "pyproject.toml")):
        print(f"{Fore.YELLOW}Found pyproject.toml in current directory, running uv {' '.join(args)}...{Style.RESET_ALL}")
        try:
            result = subprocess.run(["uv"] + args, check=False)
            if result.returncode != 0:
                print(f"Error: uv {' '.join(args)} failed in current directory")
                return 1
        except Exception as e:
            print(f"Error running uv {' '.join(args)} in current directory: {e}")
            return 1
    
    # Find all projects
    projects = find_python_projects()
    
    if not projects:
        print("No projects found")
        return 1
    
    print(f"Running 'uv {' '.join(args)}' for {len(projects)} projects:")
    for project_name, project in projects.items():
        print(f"  - {project_name} ({project.path})")
        
        # Save current directory
        original_dir = os.getcwd()
        
        try:
            # Change to project directory
            os.chdir(project.path)
            
            # Run uv command
            print(f"\n{Fore.YELLOW}Running uv {' '.join(args)} in {project.path}...{Style.RESET_ALL}")
            result = subprocess.run(["uv"] + args, check=False)
            
            if result.returncode != 0:
                print(f"Error: uv {' '.join(args)} failed for project '{project_name}'")
                return 1
        except Exception as e:
            print(f"Error running uv command for project '{project_name}': {e}")
            return 1
        finally:
            # Restore original directory
            os.chdir(original_dir)
    
    return 0
