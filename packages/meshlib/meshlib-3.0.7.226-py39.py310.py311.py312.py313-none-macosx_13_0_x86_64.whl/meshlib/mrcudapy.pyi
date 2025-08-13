from __future__ import annotations
import meshlib.mrmeshpy
from meshlib.mrmeshpy import int_output
__all__: list[str] = ['int_output', 'isCudaAvailable']
def isCudaAvailable(driverVersion: meshlib.mrmeshpy.int_output = None, runtimeVersion: meshlib.mrmeshpy.int_output = None, computeMajor: meshlib.mrmeshpy.int_output = None, computeMinor: meshlib.mrmeshpy.int_output = None) -> bool:
    """
    Returns true if Cuda is present on this GPU.
    Since Cuda is not supported on this platform, this function always returns false.
    """
