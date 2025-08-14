"""
Visualization utilities for the Gene Drive Simulation package.

This module provides functions for analyzing and visualizing simulation results.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple, Optional
import matplotlib.pyplot as plt
from datetime import datetime
import os


# Column names for population data
POP_COLUMN = 'Total_Population'
EFFECTIVE_POP_COLUMN = 'Effective_Adult_Population'
MALE_COLUMN = 'Normal_Males'
FEMALE_COLUMN = 'Normal_Females'
GE_MALE_COLUMN = 'Gene_Edit_Males'
GE_FEMALE_COLUMN = 'Gene_Edit_Females'
YOUNG_COLUMN = 'Young_Population'
ADULT_COLUMN = 'Adult_Population'

# Confidence level for error bars (95% CI)
CONFIDENCE_LEVEL = 1.96


def analyze_simulation_results(sim_array: List[List[Dict[str, int]]]) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Analyze results from multiple simulation runs and compute statistics.
    
    Args:
        sim_array: List of simulation results, where each result is a list of 
                  dictionaries containing population statistics for each year
    
    Returns:
        Tuple containing:
        - DataFrame with mean values for each statistic
        - DataFrame with standard deviation values for each statistic
    """
    # Convert the nested structure to a 3D numpy array
    flattened_data = [[[value for value in year_stats.values()] for year_stats in trial] 
                      for trial in sim_array]
    array_3d = np.array(flattened_data)
    
    # Calculate mean and standard deviation across trials
    mean_array = np.mean(array_3d, axis=0, dtype=int)
    std_array = np.std(array_3d, axis=0)
    
    # Create DataFrames
    columns = ["Normal_Males", "Normal_Females", "Gene_Edit_Males", "Gene_Edit_Females",
               "Young_Population", "Adult_Population", "Total_Population", "Effective_Adult_Population"]
    
    mean_df = pd.DataFrame(mean_array, columns=columns)
    std_df = pd.DataFrame(std_array, columns=columns)
    
    # Add year column
    mean_df['Year'] = range(len(mean_df))
    std_df['Year'] = range(len(std_df))
    
    return mean_df, std_df


def display_graphs(mean_df: pd.DataFrame, std_df: pd.DataFrame, 
                  settings: Optional[Dict[str, Any]] = None, 
                  show: bool = True, 
                  save_path: Optional[str] = None) -> None:
    """
    Display graphs of simulation results.
    
    Args:
        mean_df: DataFrame with mean values for each statistic
        std_df: DataFrame with standard deviation values for each statistic
        settings: Dictionary of simulation settings used (for titles/annotations)
        show: Whether to display the graphs (default: True)
        save_path: Path to save the graphs (default: None)
    """
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    # Add titles if settings are provided
    if settings:
        fig.suptitle(f"Gene Drive Simulation Results - {settings.get('gene_drive_type', 'Unknown')} Drive", 
                    fontsize=16)
    
    # Population Graph
    axes[0, 0].errorbar(mean_df['Year'], mean_df[POP_COLUMN], 
                        yerr=CONFIDENCE_LEVEL * std_df[POP_COLUMN] / np.sqrt(len(mean_df)),
                        marker='o', label='Total Population')
    axes[0, 0].errorbar(mean_df['Year'], mean_df[EFFECTIVE_POP_COLUMN], 
                        yerr=CONFIDENCE_LEVEL * std_df[EFFECTIVE_POP_COLUMN] / np.sqrt(len(mean_df)),
                        marker='s', label='Effective Population')
    axes[0, 0].legend()
    axes[0, 0].set_title('Population over Time')
    axes[0, 0].set_xlabel('Year')
    axes[0, 0].set_ylabel('Population')
    axes[0, 0].grid(True)
    
    # Gender Graph
    axes[0, 1].errorbar(mean_df['Year'], mean_df[MALE_COLUMN], 
                        yerr=CONFIDENCE_LEVEL * std_df[MALE_COLUMN] / np.sqrt(len(mean_df)),
                        marker='o', label='Males')
    axes[0, 1].errorbar(mean_df['Year'], mean_df[FEMALE_COLUMN], 
                        yerr=CONFIDENCE_LEVEL * std_df[FEMALE_COLUMN] / np.sqrt(len(mean_df)),
                        marker='s', label='Females')
    axes[0, 1].legend()
    axes[0, 1].set_title('Gender Distribution over Time')
    axes[0, 1].set_xlabel('Year')
    axes[0, 1].set_ylabel('Population')
    axes[0, 1].grid(True)
    
    # Gene Edit Graph
    axes[1, 0].errorbar(mean_df['Year'], mean_df[GE_MALE_COLUMN], 
                        yerr=CONFIDENCE_LEVEL * std_df[GE_MALE_COLUMN] / np.sqrt(len(mean_df)),
                        marker='o', label='Gene Drive Males')
    axes[1, 0].errorbar(mean_df['Year'], mean_df[GE_FEMALE_COLUMN], 
                        yerr=CONFIDENCE_LEVEL * std_df[GE_FEMALE_COLUMN] / np.sqrt(len(mean_df)),
                        marker='s', label='Gene Drive Females')
    axes[1, 0].legend()
    axes[1, 0].set_title('Gene Drive Carriers over Time')
    axes[1, 0].set_xlabel('Year')
    axes[1, 0].set_ylabel('Population')
    axes[1, 0].grid(True)
    
    # Age Distribution Graph
    axes[1, 1].errorbar(mean_df['Year'], mean_df[YOUNG_COLUMN], 
                        yerr=CONFIDENCE_LEVEL * std_df[YOUNG_COLUMN] / np.sqrt(len(mean_df)),
                        marker='o', label='Young Population')
    axes[1, 1].errorbar(mean_df['Year'], mean_df[ADULT_COLUMN], 
                        yerr=CONFIDENCE_LEVEL * std_df[ADULT_COLUMN] / np.sqrt(len(mean_df)),
                        marker='s', label='Adult Population')
    axes[1, 1].legend()
    axes[1, 1].set_title('Age Distribution over Time')
    axes[1, 1].set_xlabel('Year')
    axes[1, 1].set_ylabel('Population')
    axes[1, 1].grid(True)
    
    plt.tight_layout(rect=[0, 0, 1, 0.95])  # Adjust layout to make room for suptitle
    
    if save_path:
        plt.savefig(save_path)
    
    if show:
        plt.show()
    else:
        plt.close()


def save_results_to_csv(mean_df: pd.DataFrame, 
                       std_df: pd.DataFrame, 
                       sim_name: str, 
                       settings: Dict[str, Any]) -> Tuple[str, str]:
    """
    Save simulation results to CSV files.
    
    Args:
        mean_df: DataFrame with mean values for each statistic
        std_df: DataFrame with standard deviation values for each statistic
        sim_name: Name of the simulation for the output files
        settings: Dictionary of simulation settings
    
    Returns:
        Tuple of paths to the saved files (means file, standard deviations file)
    """
    # Create results directory if it doesn't exist
    results_dir = 'results'
    os.makedirs(results_dir, exist_ok=True)
    
    # Create timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Generate filenames
    if not sim_name:
        sim_name = f"simulation_{timestamp}"
    else:
        sim_name = f"{sim_name}_{timestamp}"
    
    means_filename = os.path.join(results_dir, f"{sim_name}_means.csv")
    stddev_filename = os.path.join(results_dir, f"{sim_name}_stddev.csv")
    settings_filename = os.path.join(results_dir, f"{sim_name}_settings.csv")
    
    # Save DataFrames to CSV
    mean_df.to_csv(means_filename, index=False)
    std_df.to_csv(stddev_filename, index=False)
    
    # Save settings as CSV
    pd.DataFrame([settings]).to_csv(settings_filename, index=False)
    
    return means_filename, stddev_filename 