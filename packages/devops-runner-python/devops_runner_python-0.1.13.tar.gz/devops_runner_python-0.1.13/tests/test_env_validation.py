import os
import pytest
from unittest.mock import patch, mock_open
from devops_runner_python.env_validation import (
    parse_env_yaml,
    validate_env_vars,
    parse_dotenv_file,
    validate_environment
)


@pytest.fixture
def mock_env():
    """Fixture to set and reset environment variables for testing."""
    original_env = os.environ.copy()
    yield
    os.environ.clear()
    os.environ.update(original_env)


def test_parse_env_yaml_valid():
    """Test parsing a valid env.yaml file."""
    yaml_content = """
    - TEST_ENV_MANDATORY
    - TEST_ENV_OPTIONAL: optional
    - TEST_ENV_BOOLEAN: boolean
    - TEST_ENV_ENUM: [option1, option2]
    """
    
    with patch('builtins.open', mock_open(read_data=yaml_content)):
        with patch('os.path.exists', return_value=True):
            result = parse_env_yaml('dummy.yaml')
    
    assert result is not None
    assert result['TEST_ENV_MANDATORY'] == 'required'
    assert result['TEST_ENV_OPTIONAL'] == 'optional'
    assert result['TEST_ENV_BOOLEAN'] == 'boolean'
    assert result['TEST_ENV_ENUM'] == ['option1', 'option2']


def test_parse_env_yaml_invalid_not_list():
    """Test parsing an invalid env.yaml file (not a list)."""
    yaml_content = """
    TEST_ENV_MANDATORY: required
    """
    
    with patch('builtins.open', mock_open(read_data=yaml_content)):
        with patch('os.path.exists', return_value=True):
            with patch('builtins.print') as mock_print:
                result = parse_env_yaml('dummy.yaml')
    
    assert result is None
    mock_print.assert_called_with("Error in dummy.yaml: env.yaml file must resolve to an array")


def test_parse_env_yaml_invalid_multiple_keys():
    """Test parsing an invalid env.yaml file (object with multiple keys)."""
    yaml_content = """
    - 
      TEST_ENV1: optional
      TEST_ENV2: optional
    """
    
    with patch('builtins.open', mock_open(read_data=yaml_content)):
        with patch('os.path.exists', return_value=True):
            with patch('builtins.print') as mock_print:
                result = parse_env_yaml('dummy.yaml')
    
    assert result is None
    # The error message should contain information about multiple keys
    mock_print.assert_called()


def test_validate_env_vars_all_valid(mock_env):
    """Test validating environment variables when all are valid."""
    os.environ['TEST_ENV_MANDATORY'] = 'value'
    os.environ['TEST_ENV_BOOLEAN'] = 'true'
    os.environ['TEST_ENV_ENUM'] = 'option1'
    
    requirements = {
        'TEST_ENV_MANDATORY': 'required',
        'TEST_ENV_OPTIONAL': 'optional',
        'TEST_ENV_BOOLEAN': 'boolean',
        'TEST_ENV_ENUM': ['option1', 'option2']
    }
    
    errors = validate_env_vars(requirements, 'dummy.yaml')
    assert not errors


def test_validate_env_vars_missing_required(mock_env):
    """Test validating environment variables when a required one is missing."""
    requirements = {
        'TEST_ENV_MANDATORY': 'required'
    }
    
    errors = validate_env_vars(requirements, 'dummy.yaml')
    assert 'TEST_ENV_MANDATORY' in errors
    assert 'required but missing' in errors['TEST_ENV_MANDATORY']


def test_validate_env_vars_invalid_boolean(mock_env):
    """Test validating environment variables when a boolean is invalid."""
    os.environ['TEST_ENV_BOOLEAN'] = 'not_a_boolean'
    
    requirements = {
        'TEST_ENV_BOOLEAN': 'boolean'
    }
    
    errors = validate_env_vars(requirements, 'dummy.yaml')
    assert 'TEST_ENV_BOOLEAN' in errors
    assert 'must be either true or false' in errors['TEST_ENV_BOOLEAN']


def test_validate_env_vars_invalid_enum(mock_env):
    """Test validating environment variables when an enum value is invalid."""
    os.environ['TEST_ENV_ENUM'] = 'option3'
    
    requirements = {
        'TEST_ENV_ENUM': ['option1', 'option2']
    }
    
    errors = validate_env_vars(requirements, 'dummy.yaml')
    assert 'TEST_ENV_ENUM' in errors
    assert 'must be one of option1, option2' in errors['TEST_ENV_ENUM']


def test_parse_dotenv_file():
    """Test parsing a .env.global file."""
    env_content = """
    # Comment
    TEST_ENV1=value1
    TEST_ENV2=value2
    
    # Another comment
    TEST_ENV3=value3
    """
    
    with patch('devops_python.env_validation.dotenv_values', return_value={
        'TEST_ENV1': 'value1',
        'TEST_ENV2': 'value2',
        'TEST_ENV3': 'value3'
    }):
        with patch('os.path.exists', return_value=True):
            result = parse_dotenv_file('dummy.env')
    
    assert set(result) == {'TEST_ENV1', 'TEST_ENV2', 'TEST_ENV3'}


@patch('devops_python.env_validation.find_env_yaml_files')
@patch('devops_python.env_validation.find_dotenv_files')
@patch('devops_python.env_validation.parse_env_yaml')
@patch('devops_python.env_validation.validate_env_vars')
@patch('devops_python.env_validation.parse_dotenv_file')
def test_validate_environment_success(
    mock_parse_dotenv, mock_validate, mock_parse_yaml, mock_find_dotenv, mock_find_yaml
):
    """Test successful environment validation."""
    # Setup mocks
    mock_find_yaml.return_value = ['project1/env.yaml']
    mock_find_dotenv.return_value = ['config/.env.global']
    mock_parse_yaml.return_value = {'TEST_ENV': 'required'}
    mock_validate.return_value = {}  # No errors
    mock_parse_dotenv.return_value = ['TEST_ENV']
    
    # Run validation
    result = validate_environment()
    
    # Assertions
    assert result is True
    mock_find_yaml.assert_called_once()
    mock_find_dotenv.assert_called_once()
    mock_parse_yaml.assert_called_once()
    mock_validate.assert_called_once()
    mock_parse_dotenv.assert_called_once()


@patch('devops_python.env_validation.find_env_yaml_files')
@patch('devops_python.env_validation.find_dotenv_files')
@patch('devops_python.env_validation.parse_env_yaml')
@patch('devops_python.env_validation.validate_env_vars')
@patch('devops_python.env_validation.parse_dotenv_file')
def test_validate_environment_with_errors(
    mock_parse_dotenv, mock_validate, mock_parse_yaml, mock_find_dotenv, mock_find_yaml
):
    """Test environment validation with errors."""
    # Setup mocks
    mock_find_yaml.return_value = ['project1/env.yaml']
    mock_find_dotenv.return_value = ['config/.env.global']
    mock_parse_yaml.return_value = {'TEST_ENV': 'required'}
    mock_validate.return_value = {'TEST_ENV': 'Error: TEST_ENV is required but missing'}
    mock_parse_dotenv.return_value = ['TEST_ENV']
    
    # Run validation with patched print to avoid output during tests
    with patch('builtins.print'):
        result = validate_environment()
    
    # Assertions
    assert result is False
    mock_find_yaml.assert_called_once()
    mock_find_dotenv.assert_called_once()
    mock_parse_yaml.assert_called_once()
    mock_validate.assert_called_once()
    mock_parse_dotenv.assert_called_once()


@patch('devops_python.env_validation.find_env_yaml_files')
@patch('devops_python.env_validation.find_dotenv_files')
@patch('devops_python.env_validation.parse_env_yaml')
@patch('devops_python.env_validation.parse_dotenv_file')
def test_validate_environment_with_warnings(
    mock_parse_dotenv, mock_parse_yaml, mock_find_dotenv, mock_find_yaml
):
    """Test environment validation with warnings (unused env vars)."""
    # Setup mocks
    mock_find_yaml.return_value = ['project1/env.yaml']
    mock_find_dotenv.return_value = ['config/.env.global']
    mock_parse_yaml.return_value = {'TEST_ENV1': 'required'}
    mock_parse_dotenv.return_value = ['TEST_ENV1', 'TEST_ENV2']  # TEST_ENV2 is unused
    
    # Mock validate_env_vars to return no errors
    with patch('devops_python.env_validation.validate_env_vars', return_value={}):
        # Run validation with patched print to avoid output during tests
        with patch('builtins.print'):
            result = validate_environment()
    
    # Assertions
    assert result is True  # Warnings don't cause failure
    mock_find_yaml.assert_called_once()
    mock_find_dotenv.assert_called_once()
    mock_parse_yaml.assert_called_once()
    mock_parse_dotenv.assert_called_once()
