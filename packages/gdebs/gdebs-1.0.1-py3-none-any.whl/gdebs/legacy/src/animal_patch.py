from abc import ABC, abstractmethod
from typing import Iterator, Iterable, Generator
import itertools
import numpy as np
import time as time


class Animal(ABC):
    id_counter = itertools.count()

    @abstractmethod
    def __init__(self, age):
        self.age = age

    @abstractmethod
    def __repr__(self):
        pass

    def age_one_year(self) -> None:
        self.age += 1


class WildPig(Animal):

    @abstractmethod
    def __init__(self, weight: Iterable, life_span: int, gene_edit: bool, age: int, sex: bool, alive: bool = True):
        self.id_number = next(self.id_counter)
        self.weight = weight
        self.life_span = life_span
        self.gene_edit = gene_edit
        self.age = age
        self.alive = alive

    def __repr__(self):
        return (f"{self.__class__.__name__}(ID={self.id_number}, weight={self.weight}, life_span={self.life_span},"
                f"gene_edit={self.gene_edit}, age={self.age}, life_status={self.alive})")

    # def __str__(self) -> str:
    #     return f"ID: {self.id_number}, Species: Wild Pig, Age: {self.age}, " \
    #            f"Life Span: {self.life_span}, Gene Modified: {self.gene_edit}"

    def update_life_status(self) -> None:
        if self.age > self.life_span:
            self.alive = False


class Boar(WildPig):
    def __init__(self, weight: Iterable, life_span: int, gene_edit: bool, age: int):
        super().__init__(weight, life_span, gene_edit, age, sex=False)

    def fight(self):
        pass


class Sow(WildPig):
    def __init__(self, weight: Iterable, life_span: int, gene_edit: bool, age: int):
        super().__init__(weight, life_span, gene_edit, age, sex=False)
        self.mated = False

    @property
    def fertile(self) -> bool:
        return not self.gene_edit


class AnimalGroup(ABC):

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def __repr__(self):
        pass


# Patch refers to a group of pigs
class PigPatch(AnimalGroup):

    def __init__(self):
        self.boar_population = []
        self.normal_sow_population = []
        self.gene_edit_sow_population = []
        self.young_population = []

    def __repr__(self):
        return (f"{self.__class__.__name__}"
                f"(boar_population={self.boar_population[0:5]}, "
                f"normal_sow_population={self.normal_sow_population[0:5]}, "
                f"gene_edit_sow_population={self.gene_edit_sow_population[0:5]},"
                f"young_population={self.young_population[0:5]}")

    def move_young_to_adult(self) -> None:
        adults = (animal for animal in self.young_population if animal.age > 1)
        self.add_to_adult_population(adults)

    def add_to_adult_population(self, animals: Iterable) -> None:
        # Assume that the animal has a 'gender' attribute and an 'is_gene_edited' attribute.
        for animal in list(animals):
            if isinstance(animal, Boar):
                self.boar_population.append(animal)
            elif isinstance(animal, Sow):
                if animal.fertile:
                    self.normal_sow_population.append(animal)
                else:
                    self.gene_edit_sow_population.append(animal)
            else:
                print(animal)
                raise TypeError("Animal is neither a Boar or a Sow")

    def remove_deceased(self) -> None:
        self.boar_population = [animal for animal in self.boar_population if animal.alive is True]
        self.normal_sow_population = [animal for animal in self.normal_sow_population if animal.alive is True]
        self.gene_edit_sow_population = [animal for animal in self.gene_edit_sow_population if animal.alive is True]
        self.young_population = [animal for animal in self.young_population if animal.age <= 1 and animal.alive is True]

    def update_populations(self) -> None:
        self.all_animal_update_operations()
        self.move_young_to_adult()
        self.remove_deceased()

    def all_animal_update_operations(self) -> None:
        for animal in itertools.chain(self.boar_population, self.normal_sow_population,
                                      self.gene_edit_sow_population, self.young_population):
            try:
                animal.age_one_year()
                animal.update_life_status()
            except ValueError:
                pass

    def allocate_mates(self) -> Generator[tuple[any, list], any, None]:
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

    def choose_females(self, size):
        if len(self.normal_sow_population) < size:
            return False
        else:
            return np.random.choice(self.normal_sow_population, size)

    def reset_mated(self):
        for i in self.normal_sow_population:
            i.mated = False

    @property
    def population_count(self) -> int:
        return len(self.boar_population) + len(self.normal_sow_population) \
            + len(self.gene_edit_sow_population) + len(self.young_population)

    @property
    def adult_population_count(self) -> int:
        return self.population_count - len(self.young_population)

    @property
    def effective_pop_count(self) -> int:
        return self.population_count - len(self.gene_edit_sow_population)

    @property
    def population_stats_for_current_year(self) -> {}:
        return {'Normal_Males': len(list(self.normal_boars)),
                'Normal_Females': len(self.normal_sow_population),
                'Gene_Edit_Males': len(list(self.gene_edit_boars)),
                'Gene_Edit_Females': len(self.gene_edit_sow_population),
                'Young_Population': len(self.young_population),
                'Adult_Population': self.adult_population_count,
                'Total_Population': self.population_count,
                'Effective_Adult_Population': self.adult_population_count - len(self.gene_edit_sow_population)}

    @property
    def normal_boars(self) -> Iterator[Boar]:
        return (boar for boar in self.boar_population if not boar.gene_edit)

    @property
    def gene_edit_boars(self) -> Iterator[Boar]:
        return (boar for boar in self.boar_population if boar.gene_edit)

    # def get_population_stats_list(self) -> []:
    #     return list(self.population_stats_for_current_year.value)
    #
    #     return [len(self.normal_boars),
    #             len(self.normal_sow_population),
    #             len(self.gene_edit_boars),
    #             len(self.gene_edit_sow_population),
    #             self.dead_population,
    #             self.get_effective_pop_count]

    # Updating Populations

    def adult_survival_trial(self, probability: float) -> None:
        survival_array = np.random.binomial(1, probability, self.adult_population_count)

        for i, animal in enumerate(itertools.chain(self.boar_population, self.normal_sow_population,
                                                   self.gene_edit_sow_population)):
            if survival_array[i] == 0:
                animal.alive = False

    def newborn_survival_trial(self, probability: float) -> None:
        survival_array = np.random.binomial(1, probability, len(self.young_population))
        for i, animal in enumerate(self.young_population):
            if survival_array[i] == 0:
                animal.alive = False


def timer(func):
    def wrapper(args):
        start = time.time()
        func(args)
        end = time.time()
        print(f"Function: {func.__name__}, Run time: {end - start}")

    return wrapper
