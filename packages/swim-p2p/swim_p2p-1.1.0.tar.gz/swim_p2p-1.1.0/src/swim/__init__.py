"""
SWIM P2P: A robust implementation of the SWIM protocol for P2P membership and failure detection.

This library provides a complete implementation of the SWIM (Scalable Weakly-consistent 
Infection-style Process Group Membership) protocol with ZeroMQ integration for reliable
peer-to-peer communication.

Example:
>>> from swim import SWIMNode, SWIMConfig
>>> 
>>> config = SWIMConfig(
...     node_id="node1",
...     bind_address="127.0.0.1",
...     bind_port=7946
... )
>>> node = SWIMNode(config)
>>> await node.start()
"""

import importlib
import inspect

# Import version information - try different import paths
try:
    from .__version__ import __version__, __author__, __author_email__
except ImportError:
    try:
        from swim.__version__ import __version__, __author__, __author_email__
    except ImportError:
        # Fallback version info
        __version__ = "0.1.0"
        __authors__ = "Ruth Mutua, Marriane Akeyo"
        __author_email__ = "ruthmutua@example.com, annemarrieakeyo42@gmail.com"

# Initialize empty __all__ list
__all__ = ["__version__", "__authors__", "__author_email__"]

# Auto-discover and import key modules
_CORE_MODULES = [
    "config",
    "protocol.node",
    "protocol.member", 
    "protocol.message",
    "transport.base",
    "transport.udp",
    "transport.tcp",
    "transport.hybrid",
    "events.dispatcher",
    "events.types",
    "integration.agent",
    "integration.message_router",
    "metrics.collector",
]

# Import core modules and collect their public classes/functions
for module_name in _CORE_MODULES:
    try:
        # Import the module
        full_module_name = f"swim.{module_name}"
        module = importlib.import_module(full_module_name)
        
        # Import all public classes and functions from the module
        for name, obj in inspect.getmembers(module):
            # Skip private attributes and imported modules
            if name.startswith("_") or inspect.ismodule(obj):
                continue
                
            # Only include classes and functions defined in this module
            if (inspect.isclass(obj) or inspect.isfunction(obj)) and obj.__module__ == full_module_name:
                # Import into the swim namespace
                globals()[name] = obj
                __all__.append(name)
                
    except ImportError:
        # Skip modules that aren't available yet
        pass