"""Core components for the Gene Drive Simulation package."""

from .animals import Animal, WildPig, Boar, Sow
from .populations import AnimalGroup, PigPatch
from .gene_drive import GeneDrive

__all__ = [
    'Animal',
    'WildPig',
    'Boar',
    'Sow',
    'AnimalGroup',
    'PigPatch',
    'GeneDrive',
] 