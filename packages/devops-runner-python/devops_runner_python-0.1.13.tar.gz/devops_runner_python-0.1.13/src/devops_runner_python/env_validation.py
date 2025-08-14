import os
import yaml
from typing import Dict, List, Union, Optional
from glob import glob
from dotenv import dotenv_values
from colorama import Fore, Style

# Type definitions
EnvRequirement = Union[str, List[str]]
ParsedEnvYaml = Dict[str, EnvRequirement]


def find_env_yaml_files() -> List[str]:
    """Find all env.yaml files in the project, excluding node_modules/ and venv/ folders."""
    all_files = glob("**/env.yaml", recursive=True)
    
    # Filter out files in node_modules/ and venv/ directories
    filtered_files = []
    for file_path in all_files:
        if 'node_modules/' not in file_path and 'venv/' not in file_path:
            filtered_files.append(file_path)
    
    return filtered_files


def find_dotenv_files() -> List[str]:
    """Find .env.global file if it exists."""
    files = []
    
    # Add global .env file if it exists
    global_env_file = "config/.env.global"
    if os.path.exists(global_env_file):
        files.append(global_env_file)
    
    return files


def parse_env_yaml(file_path: str) -> Optional[ParsedEnvYaml]:
    """Parse an env.yaml file and return the environment requirements."""
    if not os.path.exists(file_path):
        print(f"Skipping {file_path}: does not exist")
        return None
    
    try:
        with open(file_path, 'r') as f:
            env_manifest = yaml.safe_load(f)
        
        if not isinstance(env_manifest, list):
            print(f"Error in {file_path}: env.yaml file must resolve to an array")
            return None
        
        all_env = {}
        for env in env_manifest:
            if isinstance(env, dict):
                if len(env) != 1:
                    print(f"Error in {file_path}: every object in env.yaml must have one key. Error near: {list(env.keys())[0]}")
                    return None
                
                name, value = list(env.items())[0]
                if not (isinstance(value, list) or value in ['optional', 'boolean']):
                    print(f"Error in {file_path}: invalid value for {name}: {value}")
                    return None
                
                all_env[name] = value
            else:
                all_env[env] = 'required'
        
        return all_env
    except yaml.YAMLError as e:
        print(f"Error parsing {file_path}: {e}")
        return None


def validate_env_vars(env_requirements: ParsedEnvYaml, file_path: str) -> Dict[str, str]:
    """Validate environment variables against requirements."""
    errors = {}
    
    # Get the relative path to make error messages more helpful
    rel_path = os.path.relpath(file_path)
    
    for key, requirement in env_requirements.items():
        value = os.environ.get(key)
        
        if requirement != 'optional' and not value:
            errors[key] = f"Error in {rel_path}: {key} is required but missing"
        elif requirement == 'boolean' and value and value.lower() not in ['true', 'false']:
            errors[key] = f"Error in {rel_path}: {key} must be either true or false. Value: {value}"
        elif isinstance(requirement, list) and value and value not in requirement:
            errors[key] = f"Error in {rel_path}: {key} must be one of {', '.join(requirement)}. Value: {value}"
    
    return errors


def parse_dotenv_file(file_path: str) -> List[str]:
    """Parse a .env file and return the keys."""
    if not os.path.exists(file_path):
        return []
    
    try:
        env_vars = dotenv_values(file_path)
        return list(env_vars.keys())
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return []


def validate_environment() -> bool:
    """
    Validate environment variables against all env.yaml files.
    
    Returns:
        True if validation passed, False otherwise
    """
    # Find all env.yaml files
    env_yaml_files = find_env_yaml_files()
    if not env_yaml_files:
        print("No env.yaml files found")
        return True
    
    # Find .env.global file
    dotenv_files = find_dotenv_files()
    
    # Parse env.yaml files
    yaml_requirements = {}
    all_keys_from_yaml = set()
    all_errors = {}
    
    for file_path in env_yaml_files:
        requirements = parse_env_yaml(file_path)
        if requirements is None:
            print(f"Failed to parse {file_path}")
            return False
        
        yaml_requirements[file_path] = requirements
        all_keys_from_yaml.update(requirements.keys())
        
        # Validate environment variables against requirements
        errors = validate_env_vars(requirements, file_path)
        for key, error in errors.items():
            if key not in all_errors:
                all_errors[key] = []
            all_errors[key].append(error)
    
    # Parse .env files and check for unused variables
    keys_from_dotenv = {}
    for file_path in dotenv_files:
        keys = parse_dotenv_file(file_path)
        for key in keys:
            if key not in keys_from_dotenv:
                keys_from_dotenv[key] = []
            keys_from_dotenv[key].append(file_path)
    
    # Find unused keys in .env files
    unused_keys = [key for key in keys_from_dotenv if key not in all_keys_from_yaml]
    
    # Print warnings for unused keys
    if unused_keys:
        print(f"{Fore.YELLOW}WARNING: some env variables exist in .env but not in env.yaml:{Style.RESET_ALL}")
        for key in unused_keys:
            print(f"\t{key} in: {', '.join(keys_from_dotenv[key])}")
        print()
    
    # Print errors
    if all_errors:
        for key, errors in all_errors.items():
            print(f"{Fore.RED}Errors for {key}:{Style.RESET_ALL}")
            for error in errors:
                print(f"\t{error}")
            print()
        return False
    
    return True
