"""
eDeriv2: A molecular graph generation and analysis toolkit using Graph Neural Networks.

This package provides state-of-the-art Graph Neural Network (GNN) models for 
molecular representation learning, graph generation, and molecular property prediction.
"""

__version__ = "0.1.0"
__author__ = "eDeriv2 Team"
__email__ = "your.email@example.com"

# Import main modules (handle missing dependencies gracefully)
try:
    from . import chem_handlers
except ImportError:
    chem_handlers = None

try:
    from . import input_tools
except ImportError:
    input_tools = None

try:
    from . import nn_tools
except ImportError:
    nn_tools = None

try:
    from . import optm_tools
except ImportError:
    optm_tools = None

try:
    from . import output_tools
except ImportError:
    output_tools = None

try:
    from . import sys_tools
except ImportError:
    sys_tools = None

__all__ = [
    "chem_handlers",
    "input_tools", 
    "nn_tools",
    "optm_tools",
    "output_tools",
    "sys_tools"
]
