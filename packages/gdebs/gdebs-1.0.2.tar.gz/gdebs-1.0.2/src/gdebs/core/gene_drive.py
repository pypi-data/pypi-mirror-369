"""
Gene drive types for the Gene Drive Simulation package.

This module defines the different types of gene drives that can be used in simulations.
"""

from enum import Enum


class GeneDrive(Enum):
    """
    Enum defining the types of gene drives available in the simulation.
    
    Attributes:
        FEMALE_STERILITY: Gene drive that causes females to be sterile
        FEMALE_LETHALITY: Gene drive that causes females to die at birth
    """
    
    FEMALE_STERILITY = "Female Sterility"
    FEMALE_LETHALITY = "Female Lethality"
    
    @classmethod
    def from_string(cls, drive_string: str) -> "GeneDrive":
        """
        Convert a string representation to a GeneDrive enum value.
        
        Args:
            drive_string: String representation of the gene drive type
            
        Returns:
            Corresponding GeneDrive enum value
            
        Raises:
            ValueError: If the string doesn't match any gene drive type
        """
        for drive in cls:
            if drive.value == drive_string:
                return drive
        raise ValueError(f"Unknown gene drive type: {drive_string}") 