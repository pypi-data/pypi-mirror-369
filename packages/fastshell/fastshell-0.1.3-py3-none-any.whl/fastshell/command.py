"""Command class for FastShell."""

import inspect
from typing import Any, Callable, Dict, List, Optional, get_type_hints
from dataclasses import dataclass

from .types import Parameter, ParameterType
from .exceptions import InvalidArguments
from .utils import parse_docstring, convert_value
from .validation import validate_and_convert, ValidationConfig


@dataclass
class Command:
    """Represents a shell command."""
    
    name: str
    func: Callable
    description: Optional[str] = None
    parameters: List[Parameter] = None
    use_pydantic: bool = True  # Enable Pydantic validation by default
    
    def __post_init__(self):
        if self.parameters is None:
            self.parameters = []
    
    @classmethod
    def from_function(cls, func: Callable, name: str, **kwargs) -> "Command":
        """Create a Command from a function.
        
        Args:
            func: Function to wrap
            name: Command name
            **kwargs: Additional command options
            
        Returns:
            Command instance
        """
        # Parse docstring
        docstring_info = parse_docstring(func.__doc__ or "")
        description = docstring_info.get("description", "")
        param_docs = docstring_info.get("parameters", {})
        
        # Get function signature and type hints
        sig = inspect.signature(func)
        type_hints = get_type_hints(func)
        
        # Create parameters
        parameters = []
        param_list = list(sig.parameters.items())
        
        for i, (param_name, param) in enumerate(param_list):
            param_type = type_hints.get(param_name, str)
            param_doc = param_docs.get(param_name, "")
            
            # Determine parameter type
            # Parameters without defaults are always ARGUMENT
            # Parameters with defaults are ARGUMENT if they come before any OPTION
            # or if all remaining parameters have defaults
            if param.default == inspect.Parameter.empty:
                ptype = ParameterType.ARGUMENT
                default = None
                required = True
            else:
                # Check if all remaining parameters have defaults
                remaining_params = param_list[i:]
                all_remaining_have_defaults = all(
                    p[1].default != inspect.Parameter.empty for p in remaining_params
                )
                
                if all_remaining_have_defaults:
                    # If all remaining parameters have defaults, treat as ARGUMENT
                    ptype = ParameterType.ARGUMENT
                    default = param.default
                    required = False
                else:
                    # Mixed case - treat as OPTION
                    ptype = ParameterType.OPTION
                    default = param.default
                    required = False
            
            parameters.append(Parameter(
                name=param_name,
                type=param_type,
                description=param_doc,
                default=default,
                required=required,
                parameter_type=ptype
            ))
        
        return cls(
            name=name,
            func=func,
            description=description,
            parameters=parameters,
            **kwargs
        )
    
    def execute(self, args: List[str], kwargs: Dict[str, str]) -> Any:
        """Execute the command with given arguments.
        
        Args:
            args: Positional arguments
            kwargs: Keyword arguments
            
        Returns:
            Function execution result
            
        Raises:
            InvalidArguments: If arguments are invalid
        """
        # Check for help request
        if 'help' in kwargs or 'h' in kwargs:
            from rich.console import Console
            console = Console()
            console.print(self.get_help())
            return
            
        try:
            # Convert arguments to proper types
            converted_args = []
            converted_kwargs = {}
            
            # Get parameter lists
            arg_params = [p for p in self.parameters if p.parameter_type == ParameterType.ARGUMENT]
            option_params = {p.name: p for p in self.parameters if p.parameter_type == ParameterType.OPTION}
            
            # First, handle keyword arguments to know which parameters are already provided
            provided_as_kwargs = set()
            for key, value in kwargs.items():
                provided_as_kwargs.add(key)
                if key in option_params:
                    param = option_params[key]
                    if self.use_pydantic:
                        converted_value = validate_and_convert(value, param.type, param.name)
                    else:
                        converted_value = convert_value(value, param.type)
                    converted_kwargs[key] = converted_value
                else:
                    # Check if it's an argument parameter provided as keyword
                    arg_param = next((p for p in arg_params if p.name == key), None)
                    if arg_param:
                        if self.use_pydantic:
                            converted_value = validate_and_convert(value, arg_param.type, arg_param.name)
                        else:
                            converted_value = convert_value(value, arg_param.type)
                        converted_kwargs[key] = converted_value
                    else:
                        # Unknown option
                        converted_kwargs[key] = value
            
            # Handle positional arguments
            # If any argument parameter is provided as keyword, convert all to kwargs
            if any(p.name in provided_as_kwargs for p in arg_params):
                # Convert all positional args to keyword args
                available_arg_params = [p for p in arg_params if p.name not in provided_as_kwargs]
                for i, arg in enumerate(args):
                    if i < len(available_arg_params):
                        param = available_arg_params[i]
                        if self.use_pydantic:
                            converted_value = validate_and_convert(arg, param.type, param.name)
                        else:
                            converted_value = convert_value(arg, param.type)
                        converted_kwargs[param.name] = converted_value
                    else:
                        # Extra positional arguments - this shouldn't happen in well-formed commands
                        converted_args.append(arg)
            else:
                # Normal positional argument handling
                for i, arg in enumerate(args):
                    if i < len(arg_params):
                        param = arg_params[i]
                        if self.use_pydantic:
                            converted_value = validate_and_convert(arg, param.type, param.name)
                        else:
                            converted_value = convert_value(arg, param.type)
                        converted_args.append(converted_value)
                    else:
                        # Extra positional arguments
                        converted_args.append(arg)
                
                # Handle missing arguments (add defaults for non-required ones)
                for i in range(len(args), len(arg_params)):
                    param = arg_params[i]
                    if param.required:
                        raise InvalidArguments(f"Missing required argument: {param.name}")
                    else:
                        # Add default value for optional argument
                        converted_args.append(param.default)
            
            # Add default values for missing options
            for param in option_params.values():
                if param.name not in converted_kwargs and param.default is not None:
                    converted_kwargs[param.name] = param.default
            
            # Execute function
            return self.func(*converted_args, **converted_kwargs)
            
        except TypeError as e:
            raise InvalidArguments(f"Invalid arguments: {e}")
        except ValueError as e:
            raise InvalidArguments(f"Type conversion error: {e}")
    
    def get_help(self) -> str:
        """Get help text for the command.
        
        Returns:
            Formatted help text
        """
        from .utils import format_type_name
        
        lines = []
        
        # Command name and description
        lines.append(f"Command: {self.name}")
        if self.description:
            lines.append(f"Description: {self.description}")
        
        # Usage
        usage_parts = [self.name]
        
        for param in self.parameters:
            if param.parameter_type == ParameterType.ARGUMENT:
                if param.required:
                    usage_parts.append(f"<{param.name}>")
                else:
                    usage_parts.append(f"[{param.name}]")
            else:
                usage_parts.append(f"[--{param.name.replace('_', '-')} VALUE]")
        
        lines.append(f"Usage: {' '.join(usage_parts)}")
        
        # Parameters
        if self.parameters:
            lines.append("\nParameters:")
            
            # Calculate max width for alignment
            max_name_width = max(len(param.name) for param in self.parameters)
            type_names = [format_type_name(param.type) for param in self.parameters]
            max_type_width = max(len(name) for name in type_names) if type_names else 0
            
            for param in self.parameters:
                # Format parameter name with proper alignment
                name_part = f"  {param.name:<{max_name_width}}"
                
                # Format type with proper alignment and styling
                type_name = format_type_name(param.type)
                type_part = f"({type_name:<{max_type_width}})"
                
                # Build the parameter line
                param_line = f"{name_part} {type_part}"
                
                # Add description if available
                if param.description:
                    param_line += f" - {param.description}"
                
                # Add default value and requirement info
                info_parts = []
                if not param.required:
                    info_parts.append("optional")
                if param.default is not None:
                    if isinstance(param.default, str):
                        # Truncate very long default values for display
                        default_str = param.default if len(param.default) <= 20 else f"{param.default[:20]}..."
                        info_parts.append(f"default: '{default_str}'")
                    else:
                        info_parts.append(f"default: {param.default}")
                
                if info_parts:
                    param_line += f" [{', '.join(info_parts)}]"
                
                lines.append(param_line)
        
        return "\n".join(lines)