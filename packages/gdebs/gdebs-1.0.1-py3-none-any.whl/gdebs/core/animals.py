"""
Animal models for the Gene Drive Simulation package.

This module contains the base Animal class and specific animal implementations 
(WildPig, Boar, Sow) used in gene drive simulations.
"""

from abc import ABC, abstractmethod
from typing import Iterable
import itertools


class Animal(ABC):
    """
    Abstract base class for animals in the simulation.
    
    Attributes:
        id_counter: Class variable to generate unique IDs for animal instances
        age: Current age of the animal in years
    """
    id_counter = itertools.count()

    @abstractmethod
    def __init__(self, age: int):
        """
        Initialize an animal with a given age.
        
        Args:
            age: The age of the animal in years
        """
        self.age = age

    @abstractmethod
    def __repr__(self) -> str:
        """Return a string representation of the animal."""
        pass

    def age_one_year(self) -> None:
        """Increase the animal's age by one year."""
        self.age += 1


class WildPig(Animal):
    """
    Base class for wild pigs in the simulation.
    
    Attributes:
        id_number: Unique identifier for the animal
        weight: Weight progression for each year of life
        life_span: Maximum age the animal can reach
        gene_edit: Whether the animal carries the gene drive
        age: Current age of the animal in years
        alive: Whether the animal is currently alive
    """

    @abstractmethod
    def __init__(self, weight: Iterable, life_span: int, gene_edit: bool, age: int, sex: bool, alive: bool = True):
        """
        Initialize a wild pig.
        
        Args:
            weight: Weight progression for each year of life
            life_span: Maximum age the animal can reach
            gene_edit: Whether the animal carries the gene drive
            age: Current age of the animal in years
            sex: Biological sex of the animal (True for male, False for female)
            alive: Whether the animal is currently alive (default True)
        """
        self.id_number = next(self.id_counter)
        self.weight = weight
        self.life_span = life_span
        self.gene_edit = gene_edit
        self.age = age
        self.alive = alive

    def __repr__(self) -> str:
        """Return a string representation of the wild pig."""
        return (f"{self.__class__.__name__}(ID={self.id_number}, weight={self.weight}, life_span={self.life_span},"
                f"gene_edit={self.gene_edit}, age={self.age}, life_status={self.alive})")

    def update_life_status(self) -> None:
        """Update whether the animal is alive based on its age and life span."""
        if self.age > self.life_span:
            self.alive = False


class Boar(WildPig):
    """
    Male wild pig implementation.
    
    Male pigs can carry the gene drive but are not affected by it.
    They can still pass the gene drive to their offspring.
    """
    
    def __init__(self, weight: Iterable, life_span: int, gene_edit: bool, age: int):
        """
        Initialize a boar (male wild pig).
        
        Args:
            weight: Weight progression for each year of life
            life_span: Maximum age the animal can reach
            gene_edit: Whether the animal carries the gene drive
            age: Current age of the animal in years
        """
        super().__init__(weight, life_span, gene_edit, age, sex=True)


class Sow(WildPig):
    """
    Female wild pig implementation.
    
    Female pigs can be affected by the gene drive depending on the type:
    - With female sterility drive, they cannot mate and produce offspring
    - With female lethality drive, they die at birth
    
    Attributes:
        mated: Whether the sow has mated in the current year
    """
    
    def __init__(self, weight: Iterable, life_span: int, gene_edit: bool, age: int):
        """
        Initialize a sow (female wild pig).
        
        Args:
            weight: Weight progression for each year of life
            life_span: Maximum age the animal can reach
            gene_edit: Whether the animal carries the gene drive
            age: Current age of the animal in years
        """
        super().__init__(weight, life_span, gene_edit, age, sex=False)
        self.mated = False

    @property
    def fertile(self) -> bool:
        """
        Determine if the sow is fertile.
        
        Returns:
            False if the sow carries the gene drive (sterile), True otherwise
        """
        return not self.gene_edit 