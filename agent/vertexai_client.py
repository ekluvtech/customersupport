"""Google Vertex AI (Gemini) LLM Client"""

import logging
from typing import Dict, List, Optional, Any, Callable, Awaitable
import json
import asyncio
import time
import warnings

logger = logging.getLogger(__name__)

# Suppress deprecation warnings from Vertex AI SDK if needed
# The SDK may show warnings about deprecated features that will be removed in 2026
# We're using the recommended API patterns, but some internal SDK code may still trigger warnings
warnings.filterwarnings("ignore", category=UserWarning, module="vertexai.generative_models")


def _create_text_part(text: str):
    """
    Create a Part object from text string.
    The SDK's Content expects Part objects with _raw_part attribute.
    """
    from vertexai.generative_models import Part
    
    # Try different methods to create Part from text
    try:
        # Method 1: Create Part using the protobuf structure directly
        from google.cloud.aiplatform_v1beta1.types import content as content_pb2
        text_part_pb = content_pb2.Part(text=text)
        # Part has a _from_pb method or similar
        if hasattr(Part, '_from_pb'):
            return Part._from_pb(text_part_pb)
        elif hasattr(Part, 'from_pb'):
            return Part.from_pb(text_part_pb)
    except:
        pass
    
    try:
        # Method 2: Create Part using dict format
        if hasattr(Part, 'from_dict'):
            return Part.from_dict({"text": text})
    except:
        pass
    
    try:
        # Method 3: Create a simple wrapper that has _raw_part attribute
        # This matches what Content.__init__ expects
        class TextPart:
            def __init__(self, text):
                self._raw_part = {"text": text}
        return TextPart(text)
    except:
        # Last resort: return the text and hope SDK handles it
        return text


class VertexAIClient:
    """Client for interacting with Google Vertex AI (Gemini) API"""
    
    def __init__(self, config: Dict[str, Any]):
        import os
        from pathlib import Path
        # Get configuration
        self.credentials_path = config.get("credentials_path") or os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        self.project_id = config.get("project_id") or os.getenv("GOOGLE_CLOUD_PROJECT")
        self.location = config.get("location", "us-central1")
        self.model = config.get("model", "gemini-2.5-flash)")
        self.temperature = config.get("temperature", 0.7)
        self.max_tokens = config.get("max_tokens", 2048)
        self.timeout = config.get("timeout", 300)
        
        # Validate credentials path if provided
        if self.credentials_path:
            credentials_file = Path(self.credentials_path)
            if not credentials_file.exists():
                raise FileNotFoundError(
                    f"Credentials file not found: {self.credentials_path}. "
                    "Please check the path in your config.yaml or GOOGLE_APPLICATION_CREDENTIALS environment variable."
                )
            
            # Try to extract project_id from credentials file if not provided
            if not self.project_id:
                try:
                    with open(credentials_file, 'r') as f:
                        creds_data = json.load(f)
                        self.project_id = creds_data.get("project_id")
                except Exception as e:
                    logger.warning(f"Could not read project_id from credentials file: {e}")
        
        if not self.project_id:
            raise ValueError(
                "Google Cloud project_id is required. "
                "Set 'project_id' in config.yaml under 'vertexai' section, "
                "or set GOOGLE_CLOUD_PROJECT environment variable, "
                "or include it in your credentials JSON file."
            )
        
        # Initialize Vertex AI client
        try:
            import vertexai
            from vertexai.generative_models import GenerativeModel, Tool, FunctionDeclaration
            
            # Set credentials if JSON file is provided
            if self.credentials_path:
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(Path(self.credentials_path).absolute())
                logger.info(f"Using credentials from: {self.credentials_path}")
            
            # Initialize Vertex AI with credentials
            # Use the newer API pattern to avoid deprecation warnings
            vertexai.init(
                project=self.project_id, 
                location=self.location,
                # Explicitly set to avoid deprecated defaults
            )
            self.vertexai = vertexai
            self.GenerativeModel = GenerativeModel
            self.Tool = Tool
            self.FunctionDeclaration = FunctionDeclaration
            
            # Create model instance
            # Fix common model name typos
            model_name = self.model
            if "gemini-2.5" in model_name.lower() or "gemini-2.5-flash" in model_name.lower():
                logger.warning(f"Model name '{model_name}' may not be valid. Using 'gemini-2.0-flash-exp' instead")
                model_name = "gemini-2.0-flash-exp"
            elif "gemini-2.5-flash-lite" in model_name.lower():
                logger.warning(f"Model name '{model_name}' may not be valid. Using 'gemini-2.0-flash-exp' instead")
                model_name = "gemini-2.0-flash-exp"
            
            # Use the newer API pattern - create model with explicit parameters
            self.client = GenerativeModel(
                model_name=model_name,
                # Avoid deprecated parameters
            )
            self.model = model_name  # Update to corrected name
            logger.info(f"Vertex AI client initialized with project: {self.project_id}, model: {self.model}")
            
        except ImportError:
            raise ImportError(
                "google-cloud-aiplatform package is required for Vertex AI. "
                "Install it with: pip install google-cloud-aiplatform"
            )
        except Exception as e:
            logger.error(f"Error initializing Vertex AI: {e}")
            raise
    
    async def verify_connection(self):
        """Verify Vertex AI connection"""
        try:
            # Test connection by generating a simple response
            # Note: Vertex AI SDK is synchronous, so we run it in executor
            loop = asyncio.get_event_loop()
            
            # Use retry logic for connection verification too
            max_retries = 2
            for attempt in range(max_retries):
                try:
                    response = await loop.run_in_executor(
                        None, 
                        lambda: self.client.generate_content("Hello")
                    )
                    logger.info(f"Connected to Vertex AI. Using model: {self.model} in project: {self.project_id}")
                    return
                except Exception as e:
                    error_str = str(e)
                    is_rate_limit = "429" in error_str or "Resource exhausted" in error_str
                    
                    if is_rate_limit and attempt < max_retries - 1:
                        wait_time = 5.0  # Wait 5 seconds for rate limit
                        logger.warning(f"Rate limit during connection test. Waiting {wait_time}s before retry...")
                        await asyncio.sleep(wait_time)
                        continue
                    else:
                        raise
            
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "Resource exhausted" in error_str:
                error_msg = (
                    f"Cannot connect to Vertex AI: Rate limit exceeded (429). "
                    "Please wait a few minutes and try again, or check your quota limits. "
                    "See: https://cloud.google.com/vertex-ai/generative-ai/docs/error-code-429"
                )
            else:
                error_msg = f"Cannot connect to Vertex AI: {e}"
            logger.error(error_msg)
            raise ConnectionError(error_msg) from e
    
    async def generate(
        self,
        message: str,
        system_prompt: str,
        context: Optional[List[Dict[str, str]]] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_executor: Optional[Callable[[str, Dict[str, Any]], Awaitable[Any]]] = None
    ) -> str:
        """
        Generate a response using Vertex AI Gemini
        
        Args:
            message: User message
            system_prompt: System prompt
            context: Conversation history
            tools: Available MCP tools (converted to Gemini function format)
            tool_executor: Function to execute tools
        
        Returns:
            Generated response
        """
        try:
            from vertexai.generative_models import Content, Part
            
            # Build conversation history using Vertex AI Content objects
            conversation_history = []
            
            # Combine system prompt with message for Gemini
            # Gemini doesn't have a separate system role, so we prepend it to the first user message
            full_message = message
            if system_prompt:
                full_message = f"{system_prompt}\n\nUser: {message}"
            
            # Add context (conversation history) if available
            if context:
                for msg in context:
                    role = msg.get("role", "user")
                    content = msg.get("content", "")
                    # Map assistant/model to model role
                    mapped_role = "model" if role in ["assistant", "model"] else "user"
                    # Create Part object from text string using helper function
                    part = _create_text_part(content)
                    
                    conversation_history.append(
                        Content(
                            role=mapped_role,
                            parts=[part]
                        )
                    )
            
            # Add current message - create Part object from text using helper function
            message_part = _create_text_part(full_message)
            
            conversation_history.append(
                Content(
                    role="user",
                    parts=[message_part]
                )
            )
            
            # Convert MCP tools to Gemini function format if available
            gemini_tools = None
            if tools:
                gemini_tools = self._convert_tools_to_gemini_format(tools)
            
            # Generate response with retry logic for rate limits
            # Note: Vertex AI SDK is synchronous, so we run it in executor
            loop = asyncio.get_event_loop()
            
            # Use GenerationConfig object instead of dict to avoid deprecation
            from vertexai.generative_models import GenerationConfig
            
            generation_config = GenerationConfig(
                temperature=self.temperature,
                max_output_tokens=self.max_tokens,
            )
            
            # Retry logic for 429 (rate limit) and other transient errors
            max_retries = 3
            retry_delay = 2.0  # Start with 2 seconds
            backoff_multiplier = 2.0
            
            for attempt in range(max_retries):
                try:
                    if gemini_tools:
                        response = await loop.run_in_executor(
                            None,
                            lambda: self.client.generate_content(
                                contents=conversation_history,  # Use 'contents' parameter name
                                generation_config=generation_config,
                                tools=gemini_tools
                            )
                        )
                    else:
                        response = await loop.run_in_executor(
                            None,
                            lambda: self.client.generate_content(
                                contents=conversation_history,  # Use 'contents' parameter name
                                generation_config=generation_config
                            )
                        )
                    # Success - break out of retry loop
                    break
                    
                except Exception as e:
                    error_str = str(e)
                    # Check if it's a 429 rate limit error
                    is_rate_limit = "429" in error_str or "Resource exhausted" in error_str or "rate limit" in error_str.lower()
                    
                    if is_rate_limit and attempt < max_retries - 1:
                        wait_time = retry_delay * (backoff_multiplier ** attempt)
                        logger.warning(
                            f"Rate limit hit (429) on attempt {attempt + 1}/{max_retries}. "
                            f"Retrying in {wait_time:.1f} seconds..."
                        )
                        await asyncio.sleep(wait_time)
                        continue
                    elif attempt < max_retries - 1:
                        # Other transient errors - retry with shorter delay
                        wait_time = retry_delay
                        logger.warning(
                            f"Error on attempt {attempt + 1}/{max_retries}: {e}. "
                            f"Retrying in {wait_time:.1f} seconds..."
                        )
                        await asyncio.sleep(wait_time)
                        continue
                    else:
                        # Last attempt failed or non-retryable error
                        if is_rate_limit:
                            raise ConnectionError(
                                f"Vertex AI rate limit exceeded after {max_retries} attempts. "
                                "Please wait a few minutes and try again, or check your quota limits. "
                                "See: https://cloud.google.com/vertex-ai/generative-ai/docs/error-code-429"
                            ) from e
                        raise
            
            # Handle function calls if present
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                
                # Check for function calls
                if hasattr(candidate, 'content') and candidate.content:
                    parts = candidate.content.parts
                    
                    # Check if there are function calls
                    function_calls = [part for part in parts if hasattr(part, 'function_call') and part.function_call]
                    
                    if function_calls and tool_executor:
                        return await self._handle_function_calls(
                            function_calls, conversation_history, gemini_tools, tool_executor, generation_config
                        )
                    
                    # Extract text response
                    text_parts = [part.text for part in parts if hasattr(part, 'text') and part.text]
                    return "".join(text_parts) if text_parts else ""
            
            # Fallback: try to get text from response
            if hasattr(response, 'text'):
                return response.text
            
            return str(response)
            
        except Exception as e:
            logger.error(f"Error generating response with Vertex AI: {e}")
            raise
    
    def _convert_tools_to_gemini_format(self, tools: List[Dict[str, Any]]) -> List[Any]:
        """Convert MCP tools to Gemini function calling format"""
        function_declarations = []
        
        for tool in tools:
            name = tool.get("name", "")
            description = tool.get("description", "")
            parameters = tool.get("parameters", {})
            
            # Convert JSON Schema to Gemini format
            properties = parameters.get("properties", {})
            required = parameters.get("required", [])
            
            # Build Gemini function declaration
            function_decl = self.FunctionDeclaration(
                name=name,
                description=description,
                parameters={
                    "type": "object",
                    "properties": properties,
                    "required": required
                }
            )
            function_declarations.append(function_decl)
        
        if function_declarations:
            return [self.Tool(function_declarations=function_declarations)]
        return None
    
    async def _handle_function_calls(
        self,
        function_calls: List[Any],
        conversation_history: List[Any],
        tools: Optional[List[Any]],
        tool_executor: Callable[[str, Dict[str, Any]], Awaitable[Any]],
        generation_config: Dict[str, Any]
    ) -> str:
        """Handle function calls from Gemini response"""
        from vertexai.generative_models import Content, Part
        
        # Add model's function call to conversation
        # function_calls are already Part objects with function_call attributes
        # We can use them directly
        function_call_parts = []
        for fc in function_calls:
            # fc is already a Part object with function_call attribute
            # Just add it directly
            function_call_parts.append(fc)
        
        if function_call_parts:
            conversation_history.append(
                Content(role="model", parts=function_call_parts)
            )
        
        # Execute function calls
        function_responses = []
        for function_call in function_calls:
            import json
            if hasattr(function_call, 'function_call'):
                func_name = function_call.function_call.name
                # Convert args to dict - args might be a protobuf Struct or dict-like object
                args_obj = function_call.function_call.args
                func_args = {}
                
                try:
                    # Try different methods to extract args
                    if hasattr(args_obj, '_pb'):
                        # It's a protobuf Struct, convert to dict
                        from google.protobuf.json_format import MessageToDict
                        func_args = MessageToDict(args_obj._pb, preserving_proto_field_name=True)
                    elif hasattr(args_obj, 'keys'):
                        # It's dict-like, convert to regular dict
                        func_args = dict(args_obj)
                    elif isinstance(args_obj, dict):
                        # Already a dict
                        func_args = args_obj
                    elif hasattr(args_obj, '__dict__'):
                        # It's an object with attributes
                        func_args = {k: v for k, v in args_obj.__dict__.items() if not k.startswith('_')}
                    else:
                        # Try to convert using json
                        
                        try:
                            func_args = json.loads(json.dumps(args_obj, default=str))
                        except:
                            # Last resort: try to access as attributes
                            if hasattr(args_obj, 'order_id'):
                                func_args = {'order_id': getattr(args_obj, 'order_id')}
                            else:
                                logger.warning(f"Could not convert args for {func_name}, args_obj type: {type(args_obj)}, value: {args_obj}")
                                func_args = {}
                except Exception as e:
                    logger.error(f"Error extracting args for {func_name}: {e}, args_obj type: {type(args_obj)}")
                    func_args = {}
            else:
                # Fallback if structure is different
                func_name = getattr(function_call, 'name', 'unknown')
                func_args = getattr(function_call, 'args', {})
                if not isinstance(func_args, dict):
                    func_args = dict(func_args) if hasattr(func_args, 'keys') else {}
            
            logger.info(f"Executing function {func_name} with args: {func_args} (args type: {type(func_args)})")
            
            try:
                print("Executing tool..")
                result = await tool_executor(func_name, func_args)
                print("Tool executed successfully")
                print(f"result: {result}")
                # Convert result to proper format for function_response
                # The response field expects a struct (dict), not a string
                # First, serialize to JSON to handle datetime/date and other non-serializable types
                def json_serializer(obj):
                    """JSON serializer for objects not serializable by default json code"""
                    from datetime import datetime, date
                    from decimal import Decimal
                    
                    if isinstance(obj, (datetime, date)):
                        return obj.isoformat()
                    elif isinstance(obj, Decimal):
                        # Convert Decimal to float or string
                        return float(obj)
                    raise TypeError(f"Type {type(obj)} not serializable")
                
                # Convert result to JSON string first to handle all types properly
                #print(f"result: pre json_desi {result}")
                json_str = json.dumps(result, default=json_serializer)
                print(f"json_str: {json_str}")
                # Then parse back to dict to ensure all types are JSON-compatible
                # This ensures datetime/date objects are converted to strings
                if isinstance(result, str):
                    # If result is already a string, wrap it
                    response_struct = {"result": result}
                elif isinstance(result, (dict, list)):
                    # Parse the JSON string back to ensure all types are converted
                    parsed_result = json.loads(json_str)
                    response_struct = parsed_result if isinstance(parsed_result, dict) else {"items": parsed_result}
                else:
                    # For other types, wrap in dict
                    response_struct = {"result": json.loads(json_str)}
                print(f"response_struct: {response_struct}")
                # Create function response Part using protobuf
                # The SDK needs proper Part objects with function_response
                try:
                    from google.cloud.aiplatform_v1beta1.types import content as content_pb2
                    from google.protobuf import struct_pb2
                    
                    # Ensure all datetime/date objects are converted to strings
                    # Convert to JSON and back to ensure all types are JSON-compatible
                    # This handles datetime.date, datetime.datetime, and other non-serializable types
                    # Double conversion ensures everything is properly serialized
                    json_str_clean = json.dumps(response_struct, default=json_serializer)
                    cleaned_struct = json.loads(json_str_clean)
                    
                    
                    # Recursively clean any remaining non-serializable types
                    def clean_value(v):
                        """Recursively clean values to ensure they're protobuf-compatible"""
                        from datetime import datetime, date
                        from decimal import Decimal
                        
                        if isinstance(v, (datetime, date)):
                            return v.isoformat()
                        elif isinstance(v, Decimal):
                            # Convert Decimal to float
                            return float(v)
                        elif isinstance(v, dict):
                            return {k: clean_value(val) for k, val in v.items()}
                        elif isinstance(v, list):
                            return [clean_value(item) for item in v]
                        elif isinstance(v, (int, float, str, bool, type(None))):
                            return v
                        else:
                            # Convert unknown types to string
                            return str(v)
                    # Clean the struct recursively
                    final_struct = clean_value(cleaned_struct) if isinstance(cleaned_struct, dict) else {"result": clean_value(cleaned_struct)}
                    print(f"final_struct: {final_struct}")
                    # Create a simple struct with the cleaned data
                    # protobuf Struct uses update() method, not direct assignment
                    struct_value = struct_pb2.Struct()
                    struct_value.update(final_struct)
                    
                    # Create the protobuf Part with function_response
                    func_response_pb = content_pb2.Part(
                        function_response=content_pb2.FunctionResponse(
                            name=func_name,
                            response=struct_value
                        )
                    )
                    # Convert protobuf to Part object
                    if hasattr(Part, '_from_pb'):
                        func_part = Part._from_pb(func_response_pb)
                    else:
                        # Create Part directly from protobuf
                        func_part = Part(func_response_pb)
                    function_responses.append(func_part)
                except Exception as pb_error:
                    logger.debug(f"Protobuf approach failed for {func_name}: {pb_error}", exc_info=True)
                    # Fallback: try creating Part with dict structure
                    try:
                        # The SDK might accept a dict that gets converted
                        # response must be a dict/struct, not a string
                        func_part = Part.from_dict({
                            "function_response": {
                                "name": func_name,
                                "response": response_struct  # Use struct, not string
                            }
                        }) if hasattr(Part, 'from_dict') else None
                        if func_part:
                            function_responses.append(func_part)
                        else:
                            # Try alternative: create Part using JSON string in struct
                            try:
                                print(f"response_struct: {response_struct}")
                                # Convert response_struct to JSON string and wrap in struct
                                json_str = json.dumps(response_struct, default=str)
                                json_struct = {"json_result": json_str}
                                print(f"json_struct: {json_struct}")
                                func_part = Part.from_dict({
                                    "function_response": {
                                        "name": func_name,
                                        "response": json_struct
                                    }
                                }) if hasattr(Part, 'from_dict') else None
                                if func_part:
                                    function_responses.append(func_part)
                                else:
                                    raise ValueError("from_dict returned None")
                            except Exception as json_error:
                                logger.warning(f"Could not create function response Part for {func_name} (protobuf: {pb_error}, dict: {json_error}), will include in text response")
                                # Store result to include in final response
                                if not hasattr(self, '_function_results'):
                                    self._function_results = []
                                self._function_results.append(f"{func_name}: {json.dumps(response_struct, default=str)}")
                    except Exception as dict_error:
                        logger.warning(f"Could not create function response Part for {func_name}: {dict_error}", exc_info=True)
                        # Store result to include in final response
                        if not hasattr(self, '_function_results'):
                            self._function_results = []
                        self._function_results.append(f"{func_name}: {json.dumps(response_struct, default=str)}")
            except Exception as e:
                logger.error(f"Error executing function {func_name}: {e}")
                error_message = str(e)
                
                # Create error response Part using protobuf
                # response must be a struct (dict), not a string
                try:
                    from google.cloud.aiplatform_v1beta1.types import content as content_pb2
                    from google.protobuf import struct_pb2
                    
                    # Create error struct - use update() method for protobuf Struct
                    error_struct = struct_pb2.Struct()
                    error_struct.update({"error": error_message})
                    
                    func_response_pb = content_pb2.Part(
                        function_response=content_pb2.FunctionResponse(
                            name=func_name,
                            response=error_struct  # Use struct, not string
                        )
                    )
                    if hasattr(Part, '_from_pb'):
                        func_part = Part._from_pb(func_response_pb)
                    else:
                        func_part = Part(func_response_pb)
                    function_responses.append(func_part)
                except Exception as pb_error:
                    logger.debug(f"Protobuf approach failed for error response: {pb_error}")
                    # Fallback: try dict approach
                    try:
                        # response must be a dict/struct, not a string
                        error_response_struct = {"error": error_message}
                        func_part = Part.from_dict({
                            "function_response": {
                                "name": func_name,
                                "response": error_response_struct  # Use struct, not string
                            }
                        }) if hasattr(Part, 'from_dict') else None
                        if func_part:
                            function_responses.append(func_part)
                        else:
                            # Last resort: create a simple text response instead
                            # This will be added as a regular message part
                            logger.warning(f"Could not create function error response Part for {func_name}, will include error in text response")
                            # Store error to include in final response
                            if not hasattr(self, '_function_errors'):
                                self._function_errors = []
                            self._function_errors.append(f"Function {func_name} failed: {error_message}")
                    except Exception as dict_error:
                        logger.warning(f"Could not create error response Part for {func_name}: {dict_error}")
                        # Store error to include in final response
                        if not hasattr(self, '_function_errors'):
                            self._function_errors = []
                        self._function_errors.append(f"Function {func_name} failed: {error_message}")
        
        # Add function responses to conversation
        if function_responses:
            conversation_history.append(
                Content(role="user", parts=function_responses)
            )
        
        # Get final response from Gemini
        # Note: Vertex AI SDK is synchronous, so we run it in executor
        import asyncio
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self.client.generate_content(
                contents=conversation_history,  # Use 'contents' parameter name
                generation_config=generation_config,
                tools=tools
            )
        )
        
        # Extract text from response
        response_text = ""
        if hasattr(response, 'candidates') and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, 'content') and candidate.content:
                parts = candidate.content.parts
                text_parts = [part.text for part in parts if hasattr(part, 'text') and part.text]
                response_text = "".join(text_parts) if text_parts else ""
        
        # Fallback: try to get text from response
        if not response_text and hasattr(response, 'text'):
            response_text = response.text
        
        if not response_text:
            response_text = str(response)
        
        # Append any function results that couldn't be sent as function responses
        if hasattr(self, '_function_results') and self._function_results:
            results_summary = "\n\nFunction results: " + "; ".join(self._function_results)
            response_text += results_summary
            # Clear results after including them
            self._function_results = []
        
        # Append any function errors that couldn't be sent as function responses
        if hasattr(self, '_function_errors') and self._function_errors:
            error_summary = "\n\nNote: Some functions encountered errors: " + "; ".join(self._function_errors)
            response_text += error_summary
            # Clear errors after including them
            self._function_errors = []
        
        return response_text
    
    async def close(self):
        """Close the Vertex AI client"""
        # Vertex AI client doesn't need explicit closing, but we keep this for consistency
        pass

