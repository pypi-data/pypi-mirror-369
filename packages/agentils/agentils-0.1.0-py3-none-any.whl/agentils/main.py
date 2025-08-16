from .utils import Utils
from google import genai
from google.genai import types
import os
from typing import Optional, Literal, Any, Callable, Union
import inspect


class AgentsUtils:
    
    @staticmethod
    def execute_llm_with_tools(
        *, 
        model_name: str = 'gemini-2.0-flash-001', 
        output: Literal["json", "text"] = "json",
        api_key: Optional[str] = None,
        tools: Optional[list] = None,
        automatic_function_calling: bool = True,
        max_function_calls: int = 10,
        system_instruction: Optional[str] = None,
        temperature: Optional[float] = None,
        max_output_tokens: Optional[int] = None
    ):
        """
        Decorator for executing LLM calls with comprehensive tools integration.
        
        Args:
            model_name: The model to use (default: gemini-2.0-flash-001)
            output: Output format - "json" or "text"
            api_key: Optional API key (will use GOOGLE_API_KEY env var if not provided)
            tools: Optional list of tools (Python functions or Tool objects)
            automatic_function_calling: Whether to automatically call functions
            max_function_calls: Maximum number of automatic function calls
            system_instruction: Optional system instruction
            temperature: Optional temperature setting
            max_output_tokens: Optional max output tokens
        """
        def func_wrapper(func: Callable) -> Callable:
            def wrapper(*args, **kwargs) -> Any:
                # Get API key from parameter or environment
                key = api_key or os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
                if not key:
                    raise ValueError("API key required. Set GOOGLE_API_KEY environment variable or pass api_key parameter.")
                
                # Create client
                client = genai.Client(api_key=key)
                
                # Execute the decorated function to get the prompt/content
                text_output = func(*args, **kwargs)
                
                try:
                    # Build config
                    config_params = {}
                    
                    if tools:
                        config_params['tools'] = tools
                        
                        if automatic_function_calling:
                            config_params['automatic_function_calling'] = types.AutomaticFunctionCallingConfig(
                                maximum_remote_calls=max_function_calls
                            )
                        else:
                            config_params['automatic_function_calling'] = types.AutomaticFunctionCallingConfig(
                                disable=True
                            )
                    
                    if system_instruction:
                        config_params['system_instruction'] = system_instruction
                    
                    if temperature is not None:
                        config_params['temperature'] = temperature
                        
                    if max_output_tokens is not None:
                        config_params['max_output_tokens'] = max_output_tokens
                    
                    # Handle JSON output schema
                    if output == "json":
                        config_params['response_mime_type'] = 'application/json'
                    
                    # Create config if we have parameters
                    config = types.GenerateContentConfig(**config_params) if config_params else None
                    
                    # Generate content
                    if config:
                        response = client.models.generate_content(
                            model=model_name, 
                            contents=text_output,
                            config=config
                        )
                    else:
                        response = client.models.generate_content(
                            model=model_name, 
                            contents=text_output
                        )
                    
                    # Return formatted response
                    if output == "json":
                        return Utils.string_to_dict(response.text)
                    else:
                        return response.text
                        
                except Exception as e:
                    error_msg = f"Error executing LLM: {str(e)}"
                    if output == "json":
                        return {"error": error_msg}
                    else:
                        return error_msg
                        
            return wrapper
        return func_wrapper
    
    @staticmethod
    def execute_llm(
        *, 
        model_name: str = 'gemini-2.0-flash-001', 
        output: Literal["json", "text"] = "json",
        api_key: Optional[str] = None,
        system_instruction: Optional[str] = None,
        temperature: Optional[float] = None,
        max_output_tokens: Optional[int] = None
    ):
        """
        Simple decorator for executing LLM calls without tools.
        
        Args:
            model_name: The model to use (default: gemini-2.0-flash-001)
            output: Output format - "json" or "text"
            api_key: Optional API key (will use GOOGLE_API_KEY env var if not provided)
            system_instruction: Optional system instruction
            temperature: Optional temperature setting
            max_output_tokens: Optional max output tokens
        """
        return AgentsUtils.execute_llm_with_tools(
            model_name=model_name,
            output=output,
            api_key=api_key,
            tools=None,
            system_instruction=system_instruction,
            temperature=temperature,
            max_output_tokens=max_output_tokens
        )
    
    @staticmethod
    def create_function_tool(func: Callable) -> types.Tool:
        """
        Create a Tool object from a Python function.
        
        Args:
            func: Python function with proper docstring and type hints
            
        Returns:
            Tool object that can be used with execute_llm_with_tools
        """
        # Get function signature and docstring
        sig = inspect.signature(func)
        doc = inspect.getdoc(func) or f"Function {func.__name__}"
        
        # Parse parameters
        properties = {}
        required = []
        
        for param_name, param in sig.parameters.items():
            if param_name == 'self':
                continue
                
            param_type = 'STRING'  # Default type
            if param.annotation != inspect.Parameter.empty:
                if param.annotation == int:
                    param_type = 'INTEGER'
                elif param.annotation == float:
                    param_type = 'NUMBER'
                elif param.annotation == bool:
                    param_type = 'BOOLEAN'
                elif param.annotation == list:
                    param_type = 'ARRAY'
                elif param.annotation == dict:
                    param_type = 'OBJECT'
            
            properties[param_name] = types.Schema(
                type=param_type,
                description=f"Parameter {param_name}"
            )
            
            if param.default == inspect.Parameter.empty:
                required.append(param_name)
        
        # Create function declaration
        function_declaration = types.FunctionDeclaration(
            name=func.__name__,
            description=doc,
            parameters=types.Schema(
                type='OBJECT',
                properties=properties,
                required=required
            )
        )
        
        return types.Tool(function_declarations=[function_declaration])
    
    @staticmethod
    def create_chat_session(
        model_name: str = 'gemini-2.0-flash-001',
        api_key: Optional[str] = None,
        system_instruction: Optional[str] = None,
        tools: Optional[list] = None
    ):
        """
        Create a chat session for multi-turn conversations.
        
        Args:
            model_name: The model to use
            api_key: Optional API key
            system_instruction: Optional system instruction
            tools: Optional list of tools
            
        Returns:
            Chat session object
        """
        key = api_key or os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
        if not key:
            raise ValueError("API key required. Set GOOGLE_API_KEY environment variable or pass api_key parameter.")
        
        client = genai.Client(api_key=key)
        
        config_params = {}
        if system_instruction:
            config_params['system_instruction'] = system_instruction
        if tools:
            config_params['tools'] = tools
            
        config = types.GenerateContentConfig(**config_params) if config_params else None
        
        if config:
            return client.chats.create(model=model_name, config=config)
        else:
            return client.chats.create(model=model_name)
    
    @staticmethod
    def dictify(func):
        def wrapper():
            text_output = func()
            return Utils.string_to_dict(text_output)
        return wrapper
    
    
    
    def stringify(func):
        def wrapper():
            dict_output = func()
            return Utils.dict_to_string(dict_output)
        return wrapper
    
    
    
            