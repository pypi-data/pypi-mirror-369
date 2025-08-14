"""
Settings management utilities for the Gene Drive Simulation package.

This module provides functions for loading and saving simulation settings.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional


def save_settings(settings: Dict[str, Any], filepath: Optional[str] = None) -> None:
    """
    Save simulation settings to a JSON file.
    
    Args:
        settings: Dictionary containing simulation settings
        filepath: Path to save the settings file (default: "settings.json" in current directory)
    """
    if filepath is None:
        filepath = "settings.json"
    
    # Ensure directory exists
    directory = os.path.dirname(filepath)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
    
    with open(filepath, "w") as file:
        json.dump(settings, file, indent=4)


def load_settings(filepath: Optional[str] = None) -> Dict[str, Any]:
    """
    Load simulation settings from a JSON file.
    
    Args:
        filepath: Path to the settings file (default: "settings.json" in current directory)
        
    Returns:
        Dictionary containing simulation settings
        
    Raises:
        FileNotFoundError: If the settings file doesn't exist
    """
    if filepath is None:
        filepath = "settings.json"
    
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Settings file not found: {filepath}")
    
    with open(filepath, "r") as file:
        settings = json.load(file)
    
    return settings


def get_default_settings() -> Dict[str, Any]:
    """
    Get default simulation settings.
    
    Returns:
        Dictionary containing default simulation settings
    """
    return {
        # Starting population
        "starting_males": 500,
        "starting_females": 500,
        "starting_ge_males": 0,
        "starting_child_males": 500,
        "starting_child_females": 500,
        
        # Rate parameters
        "sex_rate": 0.5,
        "adult_survival_rate": 0.87,
        "newborn_survival_rate": 0.45,
        "gene_edit_success_rate": 0.85,
        
        # Distribution settings
        "life_span_distribution_type": "Normal",
        "life_span": [5, 2, 1, 6],  # [mean, sd, lower_bound, upper_bound]
        "body_weight_distribution_type": "Normal",
        "body_weight": [250, 50, 50, 10, 400],  # [mean, increase_per_year, sd, lower_bound, upper_bound]
        "litter_size_distribution_type": "Poisson",
        "litter_size": [5, 1, 8],  # [lambda, lower_bound, upper_bound]
        
        # Simulation parameters
        "number_of_litters": 1,
        "number_of_years": 20,
        "number_of_simulations": 20,
        
        # Gene drive options
        "gene_drive_type": "Female Sterility",
        "artificial_insemination": False,
        "AI_per_year": 0,
        "targeted_hunting": False,
        "targeted_hunting_survival_rate": 0.25,
        "added_ge_carriers": False,
        "number_of_added_GE_boars": 0,
        
        # Extra settings
        "survival_trial_first": False
    } 