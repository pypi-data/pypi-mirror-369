"""
Skyrelis: AI Agent Observability Library

Simple decorators for comprehensive AI agent monitoring and tracing.
"""

import os
import inspect
import functools
from typing import Optional, Callable, Any, Dict, Union, List
from datetime import datetime
import uuid

# Module-level logger setup
import logging
logging.basicConfig(level=logging.INFO)


def _is_langchain_agent(obj) -> bool:
    """
    Check if an object is a LangChain agent.
    
    Args:
        obj: Object to check
        
    Returns:
        bool: True if it's a LangChain agent, False otherwise
    """
    # Check for common LangChain agent methods and attributes
    langchain_methods = ['invoke', 'run', 'arun']
    langchain_attrs = ['llm', 'tools', 'agent', 'memory']
    
    has_langchain_methods = any(hasattr(obj, method) for method in langchain_methods)
    has_langchain_attrs = any(hasattr(obj, attr) for attr in langchain_attrs)
    
    return has_langchain_methods or has_langchain_attrs


def _extract_agent_metadata(obj) -> Dict[str, Any]:
    """
    Extract metadata from a LangChain agent object.
    
    Args:
        obj: The agent object
        
    Returns:
        Dict containing agent metadata including system prompts
    """
    metadata = {
        "agent_type": type(obj).__name__,
        "extraction_time": datetime.utcnow().isoformat(),
        "attributes": {},
        "system_prompts": []
    }
    
    # Extract common LangChain agent attributes
    common_attrs = [
        'llm', 'tools', 'agent', 'chain', 'memory', 'callbacks',
        'verbose', 'max_iterations', 'early_stopping_method'
    ]
    
    for attr in common_attrs:
        if hasattr(obj, attr):
            try:
                value = getattr(obj, attr)
                if value is not None:
                    # Convert to string representation for serialization
                    if hasattr(value, '__dict__'):
                        metadata["attributes"][attr] = str(value)
                    else:
                        metadata["attributes"][attr] = value
            except Exception:
                # Skip attributes that can't be accessed
                pass
    
    # Extract system prompts from various sources
    system_prompts = _extract_system_prompts(obj)
    if system_prompts:
        metadata["system_prompts"] = system_prompts
    
    # Extract LLM-specific information
    if hasattr(obj, 'llm') and obj.llm is not None:
        llm = obj.llm
        metadata["llm_info"] = {
            "type": type(llm).__name__,
            "model_name": getattr(llm, 'model_name', None),
            "temperature": getattr(llm, 'temperature', None),
            "max_tokens": getattr(llm, 'max_tokens', None),
        }
    
    # Extract tools information
    if hasattr(obj, 'tools') and obj.tools is not None:
        metadata["tools"] = [
            {
                "name": getattr(tool, 'name', str(tool)),
                "type": type(tool).__name__,
                "description": getattr(tool, 'description', None)
            }
            for tool in obj.tools
        ]
    
    # Extract agent-specific information
    if hasattr(obj, 'agent') and obj.agent is not None:
        agent = obj.agent
        metadata["agent_info"] = {
            "type": type(agent).__name__,
            "system_message": getattr(agent, 'system_message', None),
            "human_message": getattr(agent, 'human_message', None),
        }
    
    return metadata


def _extract_system_prompts(obj) -> List[Dict[str, Any]]:
    """
    Extract system prompts from various LangChain agent structures.
    
    Args:
        obj: The agent object
        
    Returns:
        List of system prompts with their sources
    """
    system_prompts = []
    
    # Method 1: Extract from agent.runnable (modern LangChain agents)
    if hasattr(obj, 'agent') and obj.agent is not None:
        runnable = getattr(obj.agent, 'runnable', None)
        if runnable is not None:
            prompts = _extract_prompts_from_runnable(runnable)
            system_prompts.extend(prompts)
    
    # Method 2: Extract from direct prompt attribute
    if hasattr(obj, 'prompt'):
        prompt = getattr(obj, 'prompt')
        if prompt is not None:
            prompts = _extract_prompts_from_template(prompt)
            system_prompts.extend(prompts)
    
    # Method 3: Extract from agent's prompt if available
    if hasattr(obj, 'agent') and obj.agent is not None and hasattr(obj.agent, 'prompt'):
        prompt = getattr(obj.agent, 'prompt')
        if prompt is not None:
            prompts = _extract_prompts_from_template(prompt)
            system_prompts.extend(prompts)
    
    # Method 4: Extract from chain structures
    if hasattr(obj, 'chain') and obj.chain is not None:
        prompts = _extract_prompts_from_runnable(obj.chain)
        system_prompts.extend(prompts)
    
    return system_prompts


def _extract_prompts_from_runnable(runnable) -> List[Dict[str, Any]]:
    """Extract prompts from a LangChain runnable object."""
    prompts = []
    
    try:
        # Check if runnable has steps (RunnableSequence)
        if hasattr(runnable, 'steps'):
            for step in runnable.steps:
                prompts.extend(_extract_prompts_from_runnable(step))
        
        # Check if it's a ChatPromptTemplate
        if hasattr(runnable, 'messages'):
            prompts.extend(_extract_prompts_from_template(runnable))
        
        # Check if runnable has a mapper (RunnableAssign)
        if hasattr(runnable, 'mapper'):
            for key, value in runnable.mapper.items():
                prompts.extend(_extract_prompts_from_runnable(value))
        
        # Check if it's a bound runnable
        if hasattr(runnable, 'bound'):
            prompts.extend(_extract_prompts_from_runnable(runnable.bound))
            
    except Exception as e:
        # Silently continue if extraction fails
        pass
    
    return prompts


def _extract_prompts_from_template(template) -> List[Dict[str, Any]]:
    """Extract system prompts from a prompt template."""
    prompts = []
    
    try:
        # Handle ChatPromptTemplate
        if hasattr(template, 'messages'):
            for message in template.messages:
                if hasattr(message, 'prompt') and hasattr(message.prompt, 'template'):
                    # Check if it's a SystemMessagePromptTemplate
                    if 'System' in type(message).__name__:
                        prompts.append({
                            "type": "system_prompt",
                            "source": "ChatPromptTemplate.SystemMessage",
                            "template": message.prompt.template,
                            "input_variables": getattr(message.prompt, 'input_variables', []),
                            "partial_variables": getattr(message.prompt, 'partial_variables', {})
                        })
        
        # Handle direct PromptTemplate
        elif hasattr(template, 'template'):
            # Check if it looks like a system prompt (heuristic)
            template_text = template.template.lower()
            if any(keyword in template_text for keyword in ['you are', 'system:', 'assistant', 'helpful']):
                prompts.append({
                    "type": "system_prompt",
                    "source": "PromptTemplate",
                    "template": template.template,
                    "input_variables": getattr(template, 'input_variables', []),
                    "partial_variables": getattr(template, 'partial_variables', {})
                })
        
        # Handle string templates
        elif isinstance(template, str):
            template_text = template.lower()
            if any(keyword in template_text for keyword in ['you are', 'system:', 'assistant', 'helpful']):
                prompts.append({
                    "type": "system_prompt",
                    "source": "string_template",
                    "template": template,
                    "input_variables": [],
                    "partial_variables": {}
                })
                
    except Exception as e:
        # Silently continue if extraction fails
        pass
    
    return prompts


def observe_agent(
    remote_observer_url: Optional[str] = None,
    agent_name: Optional[str] = None,
    enable_remote_observer: bool = True,
    capture_metadata: bool = True,
    **config_kwargs
):
    """
    Decorator to add observability to a LangChain agent.
    
    This decorator automatically detects if the decorated function returns or uses
    a LangChain agent and captures comprehensive traces including system prompts,
    LLM parameters, and agent attributes.
    
    Args:
        remote_observer_url: URL of the standalone observer (defaults to env var REMOTE_OBSERVER_URL)
        agent_name: Name for the agent (defaults to function name)
        enable_remote_observer: Whether to send traces to remote observer
        capture_metadata: Whether to capture agent metadata (LLM params, tools, etc.)
        **config_kwargs: Additional configuration options
    
    Example:
        @observe_agent(remote_observer_url="http://localhost:8000", agent_name="my_agent")
        def my_agent_function():
            # Your agent code here
            return agent  # Returns a LangChain agent
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Lazy imports to avoid requiring LangChain at import time
            from skyrelis.core.agent_observer import AgentObserver
            from skyrelis.core.monitored_agent import MonitoredAgent
            from skyrelis.config.observer_config import ObserverConfig
            
            # Get configuration
            config = ObserverConfig(
                remote_observer_url=remote_observer_url or os.getenv("REMOTE_OBSERVER_URL", "http://localhost:8000"),
                enable_remote_observer=enable_remote_observer,
                **config_kwargs
            )
            
            # Create observer
            observer = AgentObserver(config)
            
            # Execute the function
            result = func(*args, **kwargs)
            
            # Check if result is a LangChain agent
            if _is_langchain_agent(result):
                # Extract agent metadata if requested
                if capture_metadata:
                    agent_metadata = _extract_agent_metadata(result)
                    observer.add_custom_metadata("agent_metadata", agent_metadata)
                
                # Create monitored agent
                monitored_agent = MonitoredAgent(result, observer, config)
                
                # Replace the result with the monitored agent
                return monitored_agent
            else:
                # If not a LangChain agent, just return the result
                # but still create a trace for the function execution
                trace_id = str(uuid.uuid4())
                observer.start_trace(trace_id, {"args": args, "kwargs": kwargs})
                
                # Check if result contains spans
                spans = None
                if isinstance(result, dict) and "spans" in result:
                    spans = result["spans"]
                    # Use the result field as output_data if it exists
                    output_data = result.get("result", result)
                else:
                    output_data = result
                
                # Add spans to the trace if present
                if spans and trace_id in observer.active_traces:
                    observer.active_traces[trace_id]["spans"] = spans
                
                observer.end_trace(trace_id, output_data)
                return result
            
        return wrapper
    return decorator


def observe_langchain_agent(
    remote_observer_url: Optional[str] = None,
    agent_name: Optional[str] = None,
    enable_remote_observer: bool = True,
    capture_metadata: bool = True,
    **config_kwargs
):
    """
    Decorator specifically for LangChain agent classes.
    
    This decorator automatically captures system prompts, LLM parameters,
    tools, and all agent attributes when the class is instantiated.
    
    Args:
        remote_observer_url: URL of the standalone observer (defaults to env var REMOTE_OBSERVER_URL)
        agent_name: Name for the agent (defaults to class name)
        enable_remote_observer: Whether to send traces to remote observer
        capture_metadata: Whether to capture agent metadata (LLM params, tools, etc.)
        **config_kwargs: Additional configuration options
    
    Example:
        @observe_langchain_agent(remote_observer_url="http://localhost:8000")
        class MyAgent(AgentExecutor):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
    """
    def decorator(cls):
        # Import datetime for trace timing
        from datetime import datetime
        from typing import Dict, Any
        
        original_init = cls.__init__
        original_invoke = getattr(cls, 'invoke', None)
        
        # Get agent name
        agent_name_final = agent_name or cls.__name__
        
        def __init__(self, *args, **kwargs):
            # Lazy imports to avoid requiring LangChain at import time
            from skyrelis.core.agent_observer import AgentObserver
            from skyrelis.core.monitored_agent import ObservabilityCallbackHandler
            from skyrelis.config.observer_config import ObserverConfig
            import requests
            import uuid
            
            # Call original init first
            original_init(self, *args, **kwargs)
            
            # Generate unique agent ID and set on instance
            self._agent_id = str(uuid.uuid4())
            self._agent_name = agent_name_final
            
            # Get configuration
            config = ObserverConfig(
                remote_observer_url=remote_observer_url or os.getenv("REMOTE_OBSERVER_URL", "http://localhost:8000"),
                enable_remote_observer=enable_remote_observer,
                **config_kwargs
            )
            
            # Set up observability
            self._observer = AgentObserver(config)
            
            # Extract agent metadata if requested (including system prompts)
            if capture_metadata:
                agent_metadata = _extract_agent_metadata(self)
                self._agent_metadata = agent_metadata
                print(f"🤖 Agent initialized with metadata: {agent_metadata}")
                
                # Add metadata to observer for inclusion in all traces
                self._observer.add_custom_metadata("agent_metadata", agent_metadata)
                if "system_prompts" in agent_metadata:
                    self._observer.add_custom_metadata("system_prompts", agent_metadata["system_prompts"])
                
                # Register agent with the monitor
                self._register_agent_with_monitor(config.remote_observer_url, agent_metadata)
        
        def _register_agent_with_monitor(self, monitor_url: str, agent_metadata: Dict[str, Any]):
            """Register this agent instance with the monitor."""
            import requests
            import json
            
            def _make_json_serializable(obj):
                """Convert objects to JSON-serializable format."""
                if hasattr(obj, '__dict__'):
                    return str(obj)
                return obj
            
            try:
                # Ensure all data is JSON serializable
                registration_data = {
                    "agent_id": self._agent_id,
                    "agent_name": self._agent_name,
                    "agent_type": agent_metadata.get("agent_type", "unknown"),
                    "system_prompts": agent_metadata.get("system_prompts", []),
                    "tools": agent_metadata.get("tools", []),  # These are already simplified in metadata
                    "llm_info": agent_metadata.get("llm_info", {}),
                    "metadata": {
                        "extraction_time": agent_metadata.get("extraction_time"),
                        "attributes": {}, # Skip complex attributes to avoid serialization issues
                        "agent_info": agent_metadata.get("agent_info", {})
                    }
                }
                
                # Test JSON serialization before sending
                json.dumps(registration_data)
                
                response = requests.post(
                    f"{monitor_url}/api/agents/register",
                    json=registration_data,
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("status") == "success":
                        print(f"✅ Agent registered with monitor: {self._agent_id}")
                    else:
                        print(f"⚠️  Agent registration failed: {result.get('message', 'unknown error')}")
                else:
                    print(f"⚠️  Agent registration HTTP error: {response.status_code}")
                    
            except Exception as e:
                print(f"⚠️  Failed to register agent with monitor: {e}")
                # Don't raise - agent should still work without registration
        
        def invoke(self, input_data: Dict[str, Any], config=None, **kwargs):
            """Wrap the invoke method to add observability."""
            # Lazy imports
            from skyrelis.core.monitored_agent import ObservabilityCallbackHandler
            import uuid
            
            # Generate trace ID
            trace_id = str(uuid.uuid4())
            
            # Start trace with correct API (including agent_id)
            metadata = {"agent_name": self._agent_name, "agent_id": self._agent_id}
            self._observer.start_trace(
                trace_id=trace_id,
                input_data=input_data,
                metadata=metadata
            )
            
            try:
                # Create observability callback
                observability_callback = ObservabilityCallbackHandler(self._observer, trace_id)
                
                # Prepare config with callbacks
                if config is None:
                    config = {}
                
                # Get existing callbacks and add ours
                callbacks = config.get("callbacks", [])
                if not isinstance(callbacks, list):
                    callbacks = [callbacks] if callbacks else []
                
                callbacks.append(observability_callback)
                config["callbacks"] = callbacks
                
                # Call original invoke with our callback
                result = original_invoke(self, input_data, config=config, **kwargs)
                
                # End trace with success (using correct API)
                self._observer.end_trace(
                    trace_id=trace_id,
                    output_data=result,
                    error=None
                )
                
                return result
                
            except Exception as e:
                # End trace with error (using correct API)
                self._observer.end_trace(
                    trace_id=trace_id,
                    output_data=None,
                    error=e
                )
                
                raise e

        # Replace methods
        cls.__init__ = __init__
        cls._register_agent_with_monitor = _register_agent_with_monitor
        if original_invoke:
            cls.invoke = invoke
        
        return cls
    return decorator


def quick_observe(func: Callable) -> Callable:
    """
    Simple decorator that adds basic observability with default settings.
    
    Uses environment variables for configuration:
    - REMOTE_OBSERVER_URL: URL of the standalone observer
    - AGENT_NAME: Name for the agent
    
    Example:
        @quick_observe
        def my_agent_function():
            # Your agent code here
            return agent  # Returns a LangChain agent
    """
    return observe_agent()(func)


def quick_observe_class(cls):
    """
    Simple decorator for LangChain agent classes with default settings.
    
    Example:
        @quick_observe_class
        class MyAgent:
            def run(self, input_text):
                # Your agent code here
                pass
    """
    return observe_langchain_agent()(cls)


# Convenience functions for manual usage
def create_observer(
    remote_observer_url: Optional[str] = None,
    agent_name: str = "unnamed_agent",
    enable_remote_observer: bool = True,
    **config_kwargs
):
    """
    Create an observer instance for manual usage.
    
    Args:
        remote_observer_url: URL of the standalone observer
        agent_name: Name for the agent
        enable_remote_observer: Whether to send traces to remote observer
        **config_kwargs: Additional configuration options
    
    Returns:
        AgentObserver instance
    """
    # Lazy imports to avoid requiring LangChain at import time
    from skyrelis.core.agent_observer import AgentObserver
    from skyrelis.config.observer_config import ObserverConfig
    
    config = ObserverConfig(
        remote_observer_url=remote_observer_url or os.getenv("REMOTE_OBSERVER_URL", "http://localhost:8000"),
        enable_remote_observer=enable_remote_observer,
        **config_kwargs
    )
    return AgentObserver(config)


def send_trace(
    trace_data: Dict[str, Any],
    observer_url: Optional[str] = None,
    agent_name: str = "unnamed_agent"
):
    """
    Manually send a trace to the observer.
    
    Args:
        trace_data: Dictionary containing trace information
        observer_url: URL of the standalone observer
        agent_name: Name for the agent
    """
    # Lazy imports to avoid requiring LangChain at import time
    from skyrelis.utils.remote_observer_client import RemoteObserverClient
    from skyrelis.config.observer_config import ObserverConfig
    
    url = observer_url or os.getenv("OBSERVER_URL", "http://localhost:8000")
    config = ObserverConfig(remote_observer_url=url)
    client = RemoteObserverClient(config)
    
    # Add agent_name to trace_data
    if agent_name:
        trace_data["agent_name"] = agent_name
    
    return client.send_trace_sync(trace_data)


def capture_agent_metadata(agent) -> Dict[str, Any]:
    """
    Capture metadata from a LangChain agent.
    
    Args:
        agent: The LangChain agent object
        
    Returns:
        Dict containing agent metadata including LLM parameters, tools, etc.
    """
    return _extract_agent_metadata(agent) 