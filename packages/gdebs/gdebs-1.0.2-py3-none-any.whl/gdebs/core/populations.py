"""
Population models for the Gene Drive Simulation package.

This module contains classes that manage groups of animals in the simulation,
including tracking population metrics and handling mating and survival trials.
"""

from abc import ABC, abstractmethod
from typing import Iterator, Iterable, Generator
import itertools
import numpy as np

from .animals import Boar, Sow


class AnimalGroup(ABC):
    """Abstract base class for groups of animals in the simulation."""

    @abstractmethod
    def __init__(self):
        """Initialize an animal group."""
        pass

    @abstractmethod
    def __repr__(self) -> str:
        """Return a string representation of the animal group."""
        pass


class PigPatch(AnimalGroup):
    """
    A group of wild pigs (boars and sows) in the simulation.
    
    This class manages populations of male and female pigs, including
    those carrying gene drives. It handles population updates, mating,
    and survival trials.
    
    Attributes:
        boar_population: List of adult male pigs
        normal_sow_population: List of adult female pigs without gene drive
        gene_edit_sow_population: List of adult female pigs with gene drive
        young_population: List of young pigs (under 1 year old)
    """

    def __init__(self):
        """Initialize an empty pig patch."""
        self.boar_population = []
        self.normal_sow_population = []
        self.gene_edit_sow_population = []
        self.young_population = []

    def __repr__(self) -> str:
        """Return a string representation of the pig patch."""
        return (f"{self.__class__.__name__}"
                f"(boar_population={self.boar_population[0:5]}, "
                f"normal_sow_population={self.normal_sow_population[0:5]}, "
                f"gene_edit_sow_population={self.gene_edit_sow_population[0:5]},"
                f"young_population={self.young_population[0:5]}")

    def move_young_to_adult(self) -> None:
        """Move animals older than 1 year from young population to adult population."""
        adults = (animal for animal in self.young_population if animal.age > 1)
        self.add_to_adult_population(adults)

    def add_to_adult_population(self, animals: Iterable) -> None:
        """
        Add animals to the appropriate adult population.
        
        Animals are sorted based on their type (Boar or Sow) and whether they
        carry the gene drive.
        
        Args:
            animals: An iterable of animals to add to the adult population
        
        Raises:
            TypeError: If an animal is neither a Boar nor a Sow
        """
        for animal in list(animals):
            if isinstance(animal, Boar):
                self.boar_population.append(animal)
            elif isinstance(animal, Sow):
                if animal.fertile:
                    self.normal_sow_population.append(animal)
                else:
                    self.gene_edit_sow_population.append(animal)
            else:
                raise TypeError("Animal is neither a Boar or a Sow")

    def remove_deceased(self) -> None:
        """Remove dead animals from all populations."""
        self.boar_population = [animal for animal in self.boar_population if animal.alive is True]
        self.normal_sow_population = [animal for animal in self.normal_sow_population if animal.alive is True]
        self.gene_edit_sow_population = [animal for animal in self.gene_edit_sow_population if animal.alive is True]
        self.young_population = [animal for animal in self.young_population if animal.age <= 1 and animal.alive is True]

    def update_populations(self) -> None:
        """
        Update all populations for the next year.
        
        This includes aging animals, moving young to adult populations,
        and removing deceased animals.
        """
        self.all_animal_update_operations()
        self.move_young_to_adult()
        self.remove_deceased()

    def all_animal_update_operations(self) -> None:
        """
        Perform update operations on all animals.
        
        This increases the age of all animals by one year and updates
        their life status.
        """
        for animal in itertools.chain(self.boar_population, self.normal_sow_population,
                                      self.gene_edit_sow_population, self.young_population):
            try:
                animal.age_one_year()
                animal.update_life_status()
            except ValueError:
                pass

    def allocate_mates(self) -> Generator[tuple[Boar, list[Sow]], None, None]:
        """
        Allocate females to males for mating.
        
        Males are sorted by weight, and females are distributed among them.
        
        Returns:
            Generator of tuples, each containing a boar and a list of sows
            allocated to that boar for mating.
        """
        boar_sorted = sorted(self.boar_population, key=lambda boar: boar.weight.pop(0))
        females_per_division = len(self.normal_sow_population) // 5
        mate_allocation = []

        for count in range(1, 6):
            remainder = females_per_division % count
            for value in [6 - count] * (females_per_division // (6 - count)):
                mate_allocation.append(value)
            if remainder > 0:
                mate_allocation.append(remainder)

        combined = ((boar, self.normal_sow_population[i:i + group_size])
                    for i, (boar, group_size) in enumerate(zip(boar_sorted, mate_allocation)))

        return combined

    def choose_females(self, size: int):
        """
        Choose a random sample of females for artificial insemination.
        
        Args:
            size: Number of females to select
            
        Returns:
            Array of selected females, or False if there aren't enough females
        """
        if len(self.normal_sow_population) < size:
            return False
        else:
            return np.random.choice(self.normal_sow_population, size)

    def reset_mated(self) -> None:
        """Reset the mated status of all normal females."""
        for i in self.normal_sow_population:
            i.mated = False

    @property
    def population_count(self) -> int:
        """
        Get the total population count.
        
        Returns:
            Total number of animals in all populations
        """
        return len(self.boar_population) + len(self.normal_sow_population) \
            + len(self.gene_edit_sow_population) + len(self.young_population)

    @property
    def adult_population_count(self) -> int:
        """
        Get the adult population count.
        
        Returns:
            Total number of adult animals
        """
        return self.population_count - len(self.young_population)

    @property
    def effective_pop_count(self) -> int:
        """
        Get the effective population count (excluding gene drive females).
        
        Returns:
            Effective population count
        """
        return self.population_count - len(self.gene_edit_sow_population)

    @property
    def population_stats_for_current_year(self) -> dict:
        """
        Get population statistics for the current year.
        
        Returns:
            Dictionary with population statistics
        """
        return {
            'Normal_Males': len(list(self.normal_boars)),
            'Normal_Females': len(self.normal_sow_population),
            'Gene_Edit_Males': len(list(self.gene_edit_boars)),
            'Gene_Edit_Females': len(self.gene_edit_sow_population),
            'Young_Population': len(self.young_population),
            'Adult_Population': self.adult_population_count,
            'Total_Population': self.population_count,
            'Effective_Adult_Population': self.adult_population_count - len(self.gene_edit_sow_population)
        }

    @property
    def normal_boars(self) -> Iterator[Boar]:
        """
        Get an iterator of normal boars (without gene drive).
        
        Returns:
            Iterator of normal boars
        """
        return (boar for boar in self.boar_population if not boar.gene_edit)

    @property
    def gene_edit_boars(self) -> Iterator[Boar]:
        """
        Get an iterator of gene drive boars.
        
        Returns:
            Iterator of gene drive boars
        """
        return (boar for boar in self.boar_population if boar.gene_edit)

    def adult_survival_trial(self, probability: float) -> None:
        """
        Perform survival trial for adult animals.
        
        Args:
            probability: Survival probability for each adult animal
        """
        survival_array = np.random.binomial(1, probability, self.adult_population_count)

        for i, animal in enumerate(itertools.chain(self.boar_population, self.normal_sow_population,
                                                   self.gene_edit_sow_population)):
            if survival_array[i] == 0:
                animal.alive = False

    def newborn_survival_trial(self, probability: float) -> None:
        """
        Perform survival trial for newborn animals.
        
        Args:
            probability: Survival probability for each newborn animal
        """
        survival_array = np.random.binomial(1, probability, len(self.young_population))
        for i, animal in enumerate(self.young_population):
            if survival_array[i] == 0:
                animal.alive = False