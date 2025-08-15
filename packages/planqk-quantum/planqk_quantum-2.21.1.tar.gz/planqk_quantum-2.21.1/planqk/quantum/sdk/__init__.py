import sys
if sys.version_info < (3, 11):
    raise RuntimeError(
        f"PLANQK SDK requires Python 3.11 or higher; "
        f"you are running {sys.version_info.major}.{sys.version_info.minor}."
    )


"""
PLANQK Quantum SDK module providing unified access to quantum providers.
"""

from ._version import __version__
from .braket.braket_provider import PlanqkBraketProvider
from .qiskit.provider import PlanqkQuantumProvider

# Only import submodules to make them accessible, not individual client classes
from . import braket
from . import qiskit
from . import client

__all__ = ['PlanqkQuantumProvider', 'PlanqkBraketProvider', '__version__', 'braket', 'qiskit', 'client']
