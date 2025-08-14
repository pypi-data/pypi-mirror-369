"""
Main simulation module for the Gene Drive Simulation package.

This module contains the Simulation class that drives the gene drive spread
simulation and related utility functions.
"""

from typing import Callable, Iterable, List, Dict, Any, Type, TypeVar, Protocol
import numpy as np

from ..core.gene_drive import GeneDrive


class AnimalFactory(Protocol):
    """Protocol for animal factory functions."""
    
    def __call__(self, weight: Iterable, life_span: int, gene_edit: bool, age: int) -> Any:
        """Create an animal instance."""
        ...


class AnimalPopulation(Protocol):
    """Protocol for animal population classes."""
    
    def add_to_adult_population(self, animals: Iterable) -> None:
        """Add animals to the adult population."""
        ...
    
    def choose_females(self, size: int) -> Any:
        """Choose females for artificial insemination."""
        ...
    
    def adult_survival_trial(self, probability: float) -> None:
        """Perform survival trial for adult animals."""
        ...
    
    def remove_deceased(self) -> None:
        """Remove deceased animals from all populations."""
        ...
    
    def newborn_survival_trial(self, probability: float) -> None:
        """Perform survival trial for newborn animals."""
        ...
    
    def update_populations(self) -> None:
        """Update all populations for the next year."""
        ...
    
    def allocate_mates(self) -> Iterable:
        """Allocate mates for breeding."""
        ...
    
    @property
    def population_stats_for_current_year(self) -> Dict[str, int]:
        """Get population statistics for the current year."""
        ...
    
    @property
    def young_population(self) -> List:
        """Get the young population."""
        ...


T = TypeVar('T', bound=AnimalPopulation)


class Simulation:
    """
    Main simulation class for gene drive spread.
    
    This class manages the simulation of a gene drive spreading through
    a population of animals over time.
    
    Attributes:
        animal_populations: Population of animals being simulated
        settings: Dictionary of simulation settings
        male_animal: Factory function to create male animals
        female_animal: Factory function to create female animals
        original_population_size: Initial population size for threshold calculations
    """

    def __init__(self, 
                 animal_populations: Callable[[], T],
                 settings: Dict[str, Any],
                 male_animal: AnimalFactory,
                 female_animal: AnimalFactory):
        """
        Initialize a simulation.
        
        Args:
            animal_populations: Function that returns a new animal population instance
            settings: Dictionary of simulation settings
            male_animal: Factory function to create male animals
            female_animal: Factory function to create female animals
        """
        self.animal_populations = animal_populations()
        self.settings = settings
        self.male_animal = male_animal
        self.female_animal = female_animal
        self.original_population_size = None  # Will store the initial population size

    def initialize_simulation(self, 
                             size_male: int, 
                             size_ge_male: int, 
                             size_female: int, 
                             size_child_male: int,
                             size_child_female: int) -> Dict[str, int]:
        """
        Initialize the simulation with starting populations.
        
        Args:
            size_male: Number of adult males to start with
            size_ge_male: Number of gene drive adult males to start with
            size_female: Number of adult females to start with
            size_child_male: Number of male children to start with
            size_child_female: Number of female children to start with
            
        Returns:
            Dictionary with population statistics after initialization
        """
        self.animal_populations.add_to_adult_population(self.create_males(size_male, False))
        self.animal_populations.add_to_adult_population(self.create_males(size_ge_male, True))
        self.animal_populations.add_to_adult_population(self.create_females(size_female, False))
        self.animal_populations.young_population.extend(self.create_child_males(size_child_male, False))
        self.animal_populations.young_population.extend(self.create_child_females(size_child_female, False))
        current_stats = self.animal_populations.population_stats_for_current_year

        # Store the original population size for GE carrier threshold calculations
        self.original_population_size = current_stats.get('Total_Population', 0)

        self.animal_populations.update_populations()
        return current_stats

    def create_females(self, size: int, gene_edit: bool = False) -> Iterable:
        """
        Create a group of adult females.
        
        Args:
            size: Number of females to create
            gene_edit: Whether the females carry the gene drive
            
        Returns:
            Iterable of female animals
        """
        life_spans = self.determine_life_spans(size)
        weights = self.determine_weights(life_spans)
        return (self.female_animal(weights[i], life_spans[i], gene_edit, 1)
                for i in range(size))

    def create_males(self, size: int, gene_edit: bool) -> Iterable:
        """
        Create a group of adult males.
        
        Args:
            size: Number of males to create
            gene_edit: Whether the males carry the gene drive
            
        Returns:
            Iterable of male animals
        """
        life_spans = self.determine_life_spans(size)
        weights = self.determine_weights(life_spans)
        boars = (self.male_animal(weights[i], life_spans[i], gene_edit, 1) 
                for i in range(size))
        return boars

    def create_child_males(self, size: int, gene_edit: bool) -> List:
        """
        Create a group of male children.
        
        Args:
            size: Number of male children to create
            gene_edit: Whether the male children carry the gene drive
            
        Returns:
            List of male child animals
        """
        life_spans = self.determine_life_spans(size)
        weights = self.determine_weights(life_spans)
        boars = [self.male_animal(weights[i], life_spans[i], gene_edit, 0) 
                for i in range(size)]
        return boars

    def create_child_females(self, size: int, gene_edit: bool) -> List:
        """
        Create a group of female children.
        
        Args:
            size: Number of female children to create
            gene_edit: Whether the female children carry the gene drive
            
        Returns:
            List of female child animals
        """
        life_spans = self.determine_life_spans(size)
        weights = self.determine_weights(life_spans)
        sows = [self.female_animal(weights[i], life_spans[i], gene_edit, 0) 
               for i in range(size)]
        return sows

    def create_litter(self, gene_edit: bool) -> List:
        """
        Create a litter of offspring.
        
        Args:
            gene_edit: Whether the parent carries the gene drive
            
        Returns:
            List of newborn animals
        """
        litter_size = self.determine_litter_size()
        life_spans = self.determine_life_spans(litter_size)
        weights = self.determine_weights(life_spans)
        gene_edit_chance = self._gene_edit_chance(gene_edit, litter_size)
        sex_chance = self._sex_chance(litter_size, gene_edit)
        young = []
        
        gene_drive_type = GeneDrive.from_string(self.settings["gene_drive_type"])
        
        for i in range(litter_size):
            if sex_chance[i]:
                young.append(self.male_animal(weights[i], life_spans[i], gene_edit_chance[i], 0))
            elif gene_drive_type == GeneDrive.FEMALE_LETHALITY and gene_edit is True:
                # Female lethality drive causes females to die at birth
                pass
            else:
                young.append(self.female_animal(weights[i], life_spans[i], gene_edit_chance[i], 0))
        return young

    def _sex_chance(self, litter_size: int, gene_edit: bool) -> List[bool]:
        """
        Determine the sex of each offspring in a litter.
        
        Args:
            litter_size: Size of the litter
            gene_edit: Whether the parent carries the gene drive
            
        Returns:
            List of booleans indicating sex (True for male, False for female)
        """
        return np.random.binomial(1, self.settings['sex_rate'], litter_size).astype(bool).tolist()

    def _gene_edit_chance(self, gene_edit: bool, litter_size: int) -> List[bool]:
        """
        Determine whether each offspring inherits the gene drive.
        
        Args:
            gene_edit: Whether the parent carries the gene drive
            litter_size: Size of the litter
            
        Returns:
            List of booleans indicating gene drive inheritance
        """
        if gene_edit:
            gene_edit_chance = np.random.binomial(
                1,
                self.settings['gene_edit_success_rate'],
                litter_size
            ).astype(bool).tolist()
        else:
            gene_edit_chance = [False] * litter_size
        return gene_edit_chance

    def determine_litter_size(self) -> int:
        """
        Determine the size of a litter.
        
        Returns:
            Litter size based on the configured distribution
            
        Raises:
            ValueError: If the litter size distribution type is not supported
        """
        if self.settings['litter_size_distribution_type'] == 'Poisson':
            mean, lower, upper = self.settings['litter_size']
            litter_size = np.random.poisson(mean)
            return max(min(litter_size, upper), lower)
        else:
            raise ValueError(f"Unsupported litter size distribution: {self.settings['litter_size_distribution_type']}")

    def determine_life_spans(self, size: int) -> np.ndarray:
        """
        Determine the life spans for a group of animals.
        
        Args:
            size: Number of animals to generate life spans for
            
        Returns:
            Array of life spans
            
        Raises:
            ValueError: If the life span distribution type is not supported
        """
        if self.settings['life_span_distribution_type'] == 'Normal':
            mean, sd, lower, upper = self.settings['life_span']
            life_spans = np.random.normal(mean, sd, size).astype(int)
            life_spans = limiter(life_spans, lower, upper)
        elif self.settings['life_span_distribution_type'] == 'Uniform':
            lower, upper = self.settings['life_span']
            life_spans = np.random.uniform(lower, upper, size).astype(int)
        else:
            raise ValueError(f"Unsupported life span distribution: {self.settings['life_span_distribution_type']}")

        return life_spans

    def determine_weights(self, life_spans: List[int]) -> List[List[int]]:
        """
        Determine the weights for each year of life for a group of animals.
        
        Args:
            life_spans: List of animal life spans
            
        Returns:
            List of weight progressions, one for each animal
        """
        mean, increase, sd, lower, upper = self.settings['body_weight']
        weights = []
        for life_span in life_spans:
            weight = np.random.normal(
                loc=mean + increase * np.arange(1, life_span + 2),
                scale=sd, 
                size=(int(life_span) + 1)
            ).astype(int)
            limiter(weight, lower, upper)
            weights.append(weight.tolist())
        return weights

    def simulate_year(self) -> Dict[str, int]:
        """
        Simulate one year of the population.
        
        This method handles:
        - Artificial insemination if enabled
        - Adding new gene drive carriers if enabled
        - Survival trials for adults and newborns
        - Mating and reproduction
        
        Returns:
            Dictionary with population statistics after the year
        """
        adult_survival_probability = self.settings['adult_survival_rate']
        newborn_survival_probability = self.settings['newborn_survival_rate']
        survival_trial_first = self.settings.get('survival_trial_first', False)

        if self.settings.get('targeted_hunting', False):
            adult_survival_probability = self.settings['targeted_hunting_survival_rate']
            self.settings['targeted_hunting'] = False

        if self.settings.get('artificial_insemination', False):
            ai_females = self.animal_populations.choose_females(self.settings["AI_per_year"])
            if ai_females is not False:
                for female in ai_females:
                    new_litter = self.create_litter(True)
                    female.mated = True
                    self.animal_populations.young_population.extend(new_litter)

        # Handle adding gene-edited carriers with population decline protection
        if self.settings.get('added_ge_carriers', False):
            # Check if population has dropped to 30% of original size
            # Only proceed if we have a valid original population size
            if self.original_population_size is not None:
                current_population = self.animal_populations.population_stats_for_current_year.get('Total_Population', 0)
                population_threshold = self.original_population_size * 0.3
                
                if current_population <= population_threshold:
                    # Population has declined to 30% of original - stop adding GE carriers
                    self.settings['added_ge_carriers'] = False
                    print(f"Population declined to {current_population} (30% threshold reached). Stopping GE carrier addition.")
                else:
                    # Continue adding GE carriers
                    ge_males = self.create_males(self.settings['number_of_added_GE_boars'], True)
                    self.animal_populations.add_to_adult_population(ge_males)
            else:
                # Fallback: continue adding GE carriers if original population size not set
                ge_males = self.create_males(self.settings['number_of_added_GE_boars'], True)
                self.animal_populations.add_to_adult_population(ge_males)

        if survival_trial_first:
            self.animal_populations.adult_survival_trial(adult_survival_probability)
            self.animal_populations.remove_deceased()
            self.mating()
            self.animal_populations.newborn_survival_trial(newborn_survival_probability)
        else:
            self.mating()
            self.animal_populations.adult_survival_trial(adult_survival_probability)
            self.animal_populations.newborn_survival_trial(newborn_survival_probability)

        self.animal_populations.remove_deceased()
        self.animal_populations.update_populations()
        return self.animal_populations.population_stats_for_current_year

    def mating(self) -> None:
        """
        Handle mating between animals in the population.
        
        This method pairs males with females and creates offspring
        based on the simulation settings.
        """
        mating_groups = self.animal_populations.allocate_mates()
        gene_drive_type = GeneDrive.from_string(self.settings["gene_drive_type"])
        
        for group in mating_groups:
            gene_edit = group[0].gene_edit
            for female in group[1]:
                if female.mated:
                    continue
                elif female.gene_edit and gene_drive_type == GeneDrive.FEMALE_STERILITY:
                    # Females with sterility gene drive cannot produce offspring
                    continue
                else:
                    new_litter = self.create_litter(gene_edit)
                    self.animal_populations.young_population.extend(new_litter)


def limiter(variable: np.ndarray, lower: int, upper: int) -> np.ndarray:
    """
    Limit values in an array to a specified range.
    
    Args:
        variable: Array to limit
        lower: Lower bound
        upper: Upper bound
        
    Returns:
        Limited array
    """
    variable[variable < lower] = lower
    variable[variable > upper] = upper
    return variable


def simulate_n_years(population_type: Callable[[], T],
                    settings: Dict[str, Any],
                    male: AnimalFactory,
                    female: AnimalFactory) -> List[Dict[str, int]]:
    """
    Simulate multiple years of population dynamics.
    
    Args:
        population_type: Function that returns a new animal population instance
        settings: Dictionary of simulation settings
        male: Factory function to create male animals
        female: Factory function to create female animals
        
    Returns:
        List of dictionaries with population statistics for each year
    """
    sim = Simulation(population_type, settings, male, female)
    size_female = settings['starting_females']
    size_male = settings['starting_males']
    size_ge_male = settings['starting_ge_males']
    size_child_male = settings.get('starting_child_males', 0)
    size_child_female = settings.get('starting_child_females', 0)
    
    # Initialize simulation and get initial stats
    initial_stats = sim.initialize_simulation(
        size_male, size_ge_male, size_female, size_child_male, size_child_female
    )
    
    # Simulate each year and collect stats
    year_stats = [initial_stats]
    for _ in range(settings['number_of_years']):
        year_stats.append(sim.simulate_year())
    
    return year_stats 