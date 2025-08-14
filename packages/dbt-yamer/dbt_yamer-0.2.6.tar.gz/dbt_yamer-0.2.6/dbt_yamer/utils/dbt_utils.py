"""
Utility functions for dbt operations.
"""
from typing import List
from dbt_yamer.utils.subprocess_utils import run_subprocess
from dbt_yamer.utils.security_utils import validate_tag_selector, validate_model_name, build_safe_command
from dbt_yamer.exceptions import SubprocessError, ValidationError
from dbt_yamer.handlers.file_handlers import find_dbt_project_root


def expand_tag_selectors(selectors: List[str], target: str = None) -> List[str]:
    """
    Expand tag selectors to actual model names using dbt ls command.
    
    Args:
        selectors: List of model selectors (may include tag: selectors)
        target: Optional dbt target to use
        
    Returns:
        List of expanded model names
        
    Raises:
        ValidationError: If validation fails
        SubprocessError: If dbt command fails
    """
    if not selectors:
        return []
    
    processed_models = []
    
    for selector in selectors:
        # Validate selector
        validated_selector = validate_tag_selector(selector)
        
        if validated_selector.startswith('tag:'):
            # Expand tag selector
            cmd_args = ["--quiet", "ls", "--select", validated_selector]
            if target:
                cmd_args.extend(["-t", target])
                
            # Find dbt project root to run command from correct directory
            try:
                project_root = find_dbt_project_root()
            except Exception as e:
                raise SubprocessError(f"Could not find dbt project root: {e}")
            
            cmd_list = build_safe_command(["dbt"], cmd_args)
            
            try:
                result = run_subprocess(cmd_list, capture_output=True, timeout=60, cwd=str(project_root))
                if result and result.stdout:
                    # Split the fully qualified names and take the last part
                    tag_models = [
                        path.split('.')[-1] 
                        for path in result.stdout.strip().splitlines()
                        if path.strip()
                    ]
                    if not tag_models:
                        raise ValidationError(f"No models found for tag selector '{selector}'")
                    
                    processed_models.extend(tag_models)
                else:
                    raise ValidationError(f"No output from dbt ls for selector '{selector}'")
                    
            except SubprocessError as e:
                raise SubprocessError(f"Error expanding tag selector '{selector}': {e}")
        else:
            # Regular model name - validate it
            validated_model = validate_model_name(validated_selector)
            processed_models.append(validated_model)
    
    return processed_models


def get_model_sql_path(model_name: str, target: str = None) -> str:
    """
    Get the SQL file path for a dbt model using dbt ls command.
    
    Args:
        model_name: Name of the model
        target: Optional dbt target to use
        
    Returns:
        Path to the SQL file
        
    Raises:
        ValidationError: If validation fails
        SubprocessError: If dbt command fails or model not found
    """
    validated_model = validate_model_name(model_name)
    
    cmd_args = [
        "--quiet",
        "ls",
        "--resource-types", "model",
        "--select", validated_model,
        "--output", "path"
    ]
    
    if target:
        cmd_args.extend(["-t", target])
    
    # Find dbt project root to run command from correct directory
    try:
        project_root = find_dbt_project_root()
    except Exception as e:
        raise SubprocessError(f"Could not find dbt project root: {e}")
    
    cmd_list = build_safe_command(["dbt"], cmd_args)
    
    try:
        result = run_subprocess(cmd_list, capture_output=True, timeout=60, cwd=str(project_root))
        if not result or not result.stdout:
            raise SubprocessError(f"No output from dbt ls for model '{model_name}'")
        
        paths = result.stdout.strip().splitlines()
        if not paths:
            raise ValidationError(f"Model '{model_name}' not found in dbt project")
        
        return paths[0]  # Return first path if multiple
        
    except SubprocessError as e:
        raise SubprocessError(f"Error getting path for model '{model_name}': {e}")


def extract_yaml_from_dbt_output(output: str) -> str:
    """
    Extract YAML content from dbt output by finding lines that form valid YAML.
    
    Args:
        output: Raw output from dbt command containing logs and YAML
        
    Returns:
        Only the YAML content without log lines
    """
    import re
    lines = output.split('\n')
    yaml_lines = []
    
    # Look for the start of YAML content (version: 2)
    yaml_started = False
    
    for line in lines:
        # Remove timestamp prefix if present
        clean_line = re.sub(r'^\d{2}:\d{2}:\d{2} ', '', line)
        
        # Skip obvious dbt log lines
        if (line.strip().startswith('Running') or 
            line.strip().startswith('Found') or
            line.strip().startswith('Completed') or
            clean_line.strip().startswith('Completed') or
            re.search(r'\[debug\]|\[info\]|\[warn\]|\[error\]', line)):
            continue
            
        # Check if this line looks like YAML content
        if not yaml_started:
            # Look for version: 2 to start YAML block
            if clean_line.strip() == 'version: 2':
                yaml_started = True
                yaml_lines.append(clean_line)
        else:
            # We're in YAML block, include all remaining lines after cleaning timestamps
            yaml_lines.append(clean_line)
    
    return '\n'.join(yaml_lines)


def clean_dbt_output(output: str) -> str:
    """
    Clean dbt output by removing timestamp prefixes and other logging artifacts.
    
    Args:
        output: Raw output from dbt command
        
    Returns:
        Cleaned output with timestamps removed
    """
    import re
    lines = output.split('\n')
    cleaned_lines = []
    
    for line in lines:
        # Remove timestamp patterns like "15:50:43 " at the beginning of lines
        # Pattern matches HH:MM:SS followed by one space only
        cleaned_line = re.sub(r'^\d{2}:\d{2}:\d{2} ', '', line)
        cleaned_lines.append(cleaned_line)
    
    return '\n'.join(cleaned_lines)


def run_dbt_operation(macro_name: str, args_dict: dict, target: str = None) -> str:
    """
    Run a dbt run-operation command safely using bash shell.
    
    Args:
        macro_name: Name of the macro to run
        args_dict: Arguments to pass to the macro as a dictionary
        target: Optional dbt target to use
        
    Returns:
        Output from the dbt command
        
    Raises:
        ValidationError: If validation fails
        SubprocessError: If dbt command fails
    """
    if not macro_name:
        raise ValidationError("Macro name cannot be empty")
    
    if not macro_name.replace('_', '').isalnum():
        raise ValidationError(f"Invalid macro name: {macro_name}")
    
    # Build JSON args safely
    import json
    try:
        args_json = json.dumps(args_dict)
    except (TypeError, ValueError) as e:
        raise ValidationError(f"Invalid arguments for macro: {e}")
    
    # Find dbt project root to run command from correct directory
    try:
        project_root = find_dbt_project_root()
    except Exception as e:
        raise SubprocessError(f"Could not find dbt project root: {e}")
    
    # Build command args
    cmd_args = [
        "--quiet",
        "run-operation",
        macro_name,
        "--args", args_json
    ]
    
    if target:
        validated_target = validate_model_name(target)  # Reuse validation logic
        cmd_args.extend(["-t", validated_target])
    
    cmd_list = build_safe_command(["dbt"], cmd_args)
    
    try:
        result = run_subprocess(cmd_list, capture_output=True, timeout=300, cwd=str(project_root))
        if not result:
            raise SubprocessError("No result from dbt run-operation")
        
        # Parse the output to extract only the YAML content
        raw_output = result.stdout.strip()
        yaml_content = extract_yaml_from_dbt_output(raw_output)
        
        return yaml_content
        
    except SubprocessError as e:
        raise SubprocessError(f"Error running dbt operation '{macro_name}': {e}")