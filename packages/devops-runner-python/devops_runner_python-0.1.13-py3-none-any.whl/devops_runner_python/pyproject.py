import os
from typing import Any
import tomli
from pydantic import BaseModel
from .discovery import get_port_for_service_name

class PyprojectData(BaseModel):
    data: dict[str, Any]
    deployment: dict[str, Any]


def get_pyproject_data():
    """
    Reads the pyproject.toml file in the current working directory and returns its data.
    """
    pyproject_path = os.path.join(os.getcwd(), "pyproject.toml")
    with open(pyproject_path, "rb") as f:
        pyproject_data = tomli.load(f)
        
    deployment = pyproject_data.get("tool", {}).get("devops", {}).get("deployment", {})
    return PyprojectData(data=pyproject_data, deployment=deployment)


def get_service_endpoint(service_name: str) -> str:
    """
    Resolves the HTTP endpoint for a given service name.

    - If running inside Kubernetes (IS_KUBERNETES == "true"), returns http://{service_name}
    - Otherwise, uses local port discovery and returns http://127.0.0.1:{port}
    """
    if os.environ.get("IS_KUBERNETES", "").lower() == "true":
        return f"http://{service_name}"

    service_port = get_port_for_service_name(service_name)
    if not service_port:
        raise RuntimeError(f"Port not found for service {service_name}")
    return f"http://127.0.0.1:{service_port}"
    