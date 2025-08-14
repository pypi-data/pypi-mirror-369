import os
from typing import Optional
from dotenv import load_dotenv
from .env_validation import validate_environment
from colorama import Fore, Style

def load_env_vars(env: str, cwd: Optional[str] = None) -> None:
    """
    Load environment variables from config/.env.global and config/.env.<env> files
    relative to the current working directory.
    
    Args:
        env: Environment name (default: 'development')
        cwd: Current working directory. If None, uses os.getcwd()
    """
    if cwd is None:
        cwd = os.getcwd()

    print(f"\n{Fore.BLUE}Loading environment variables for {env} in {cwd}{Style.RESET_ALL}\n")

    # Load environment-specific variables
    env_specific_path = os.path.join(cwd, 'config', f'.env.{env}')
    load_dotenv(env_specific_path)

    # Load global environment variables
    global_env_path = os.path.join(cwd, 'config', '.env.global')
    load_dotenv(global_env_path)

    os.environ["MONOREPO_ROOT"] = cwd
    os.environ["MONOREPO_ENV"] = env

def validate_env_vars() -> bool:
    """
    Validate environment variables against env.yaml files.
    
    Returns:
        True if validation passed, False otherwise
    """
    return validate_environment()
