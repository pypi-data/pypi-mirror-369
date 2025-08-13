"""
Skyrelis: AI Agent Security Library

Skyrelis provides comprehensive security tools for AI agents, starting with 
enterprise-grade observability and expanding to complete agent security solutions.

🔒 **Security-First Design** - Built for enterprise AI security requirements
📊 **Complete Observability** - Full visibility into agent behavior and interactions  
🛡️ **Risk Detection** - Identify potential security threats and anomalies
🔍 **Audit & Compliance** - Comprehensive logging for regulatory requirements

Current Features (v0.1):
- **Observability & Monitoring**: Complete agent execution tracing
- **System Prompt Security**: Capture and monitor agent instructions
- **Agent Registry**: Centralized agent inventory and management
- **Real-time Alerts**: Instant notification of security events

Coming Soon:
- **Prompt Injection Detection**: Identify and block malicious inputs
- **Agent Sandboxing**: Isolated execution environments
- **Access Control**: Role-based agent permissions
- **Threat Intelligence**: AI-powered security insights

Example:
    from skyrelis import observe

    @observe(monitor_url="https://your-monitor.com")
    class SecureAgent(AgentExecutor):
        pass

    # Your agent now has enterprise-grade security monitoring!
"""

__version__ = "0.1.4"
__author__ = "Skyrelis Team"
__email__ = "security@skyrelis.com"

# Import the main decorators that users will use
from .decorators import (
    observe_langchain_agent,
    observe_agent,
    quick_observe,
    quick_observe_class,
    send_trace,
    capture_agent_metadata
)

# Simple alias for the main decorator
observe = observe_langchain_agent

# Public API - these are the only functions users should use
__all__ = [
    "observe",                    # Main security decorator (alias for observe_langchain_agent)
    "observe_langchain_agent",    # Full name if preferred
    "observe_agent",              # For function-based agents
    "quick_observe",              # Quick function decorator
    "quick_observe_class",        # Quick class decorator
    "send_trace",                 # Manual trace sending
    "capture_agent_metadata",     # Metadata extraction utility
] 