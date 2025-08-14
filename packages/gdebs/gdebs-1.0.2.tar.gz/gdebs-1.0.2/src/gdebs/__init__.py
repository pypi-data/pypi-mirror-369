"""
Gene Drive Simulation Package (gdebs)

A Python package for simulating the spread of gene drives through animal populations.

This package provides tools for:
1. Simulating gene drive spread in animal populations
2. Visualizing simulation results
3. Managing simulation settings

Available gene drive types:
- Female Sterility: Affected females cannot reproduce
- Female Lethality: Affected females die at birth
"""

from gdebs.core import Animal, WildPig, Boar, Sow, AnimalGroup, PigPatch, GeneDrive
from gdebs.simulation import Simulation, simulate_n_years
from gdebs.utils import load_settings, save_settings, get_default_settings
from gdebs.visualization import display_graphs, analyze_simulation_results, save_results_to_csv

__version__ = "1.0.0"
__all__ = [
    # Core components
    'Animal',
    'WildPig',
    'Boar',
    'Sow',
    'AnimalGroup',
    'PigPatch',
    'GeneDrive',
    
    # Simulation
    'Simulation',
    'simulate_n_years',
    
    # Utilities
    'load_settings',
    'save_settings',
    'get_default_settings',
    
    # Visualization
    'display_graphs',
    'analyze_simulation_results',
    'save_results_to_csv',
] 