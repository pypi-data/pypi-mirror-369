from typing import Callable, Iterable
from enum import Enum, auto
import numpy as np

class GeneDrive(Enum):
    FEMALE_STERILITY = 1
    FEMALE_LETHALITY = 2

class Simulation:

    def __init__(self, animal_populations: callable, settings: dict,
                 male_animal: Callable[[Iterable, int, bool, int], object],
                 female_animal: Callable[[Iterable, int, bool, int], object]):

        self.animal_populations = animal_populations()
        self.settings = settings
        self.male_animal = male_animal
        self.female_animal = female_animal

    def initialize_simulation(self, size_male: int, size_ge_male: int, size_female: int, size_child_male: int,
                              size_child_female: int):
        self.animal_populations.add_to_adult_population(self.create_males(size_male, False))
        self.animal_populations.add_to_adult_population(self.create_males(size_ge_male, True))
        self.animal_populations.add_to_adult_population(self.create_females(size_female, False))
        self.animal_populations.young_population.extend(self.create_child_males(size_child_male, False))
        self.animal_populations.young_population.extend(self.create_child_females(size_child_female, False))
        current_stats = self.animal_populations.population_stats_for_current_year

        self.animal_populations.update_populations()
        return current_stats

    def create_females(self, size: int, gene_edit: bool = False):
        life_spans = self.determine_life_spans(size)
        weights = self.determine_weights(life_spans)
        return (self.female_animal(weights[i], life_spans[i], gene_edit,
                                   1)
                for i in range(size))

    def create_males(self, size: int, gene_edit: bool):
        life_spans = self.determine_life_spans(size)
        weights = self.determine_weights(life_spans)
        boars = (self.male_animal(weights[i], life_spans[i], gene_edit,
                                  1) for
                 i in range(size))
        return boars

    def create_child_males(self, size: int, gene_edit: bool):
        life_spans = self.determine_life_spans(size)
        weights = self.determine_weights(life_spans)
        boars = (self.male_animal(weights[i], life_spans[i], gene_edit,
                                  0) for
                 i in range(size))
        return boars

    def create_child_females(self, size: int, gene_edit: bool):
        life_spans = self.determine_life_spans(size)
        weights = self.determine_weights(life_spans)
        sows = (self.female_animal(weights[i], life_spans[i], gene_edit,
                                 0) for
                i in range(size))
        return sows

    def create_litter(self, gene_edit: bool):
        litter_size = self.determine_litter_size()
        life_spans = self.determine_life_spans(litter_size)
        weights = self.determine_weights(life_spans)
        gene_edit_chance = self._gene_edit_chance(gene_edit, litter_size)
        sex_chance = self._sex_chance(litter_size, gene_edit)
        young = []
        for i in range(litter_size):
            if sex_chance[i]:
                young.append(self.male_animal(weights[i], life_spans[i], gene_edit_chance[i], 0))
            elif self.settings["gene_drive_type"] == "Female Lethality" and gene_edit is True:
                pass
            else:
                young.append(self.female_animal(weights[i], life_spans[i], gene_edit_chance[i], 0))
        return young

    def _sex_chance(self, litter_size, gene_edit: bool):
        return np.random.binomial(1, self.settings['sex_rate'], litter_size).astype(bool).tolist()

    def _gene_edit_chance(self, gene_edit: bool, litter_size: int) -> list:
        if gene_edit:
            gene_edit_chance = np.random.binomial(1,
                                                  self.settings['gene_edit_success_rate'],
                                                  litter_size).astype(bool).tolist()
        else:
            gene_edit_chance = np.zeros(litter_size).astype(bool)
        return gene_edit_chance

    def determine_litter_size(self):
        if self.settings['litter_size_distribution_type'] == 'Poisson':
            mean, lower, upper = self.settings['litter_size']
            litter_size = np.random.poisson(mean)
        else:
            raise ValueError("Something broke.")
        return litter_size

    def determine_life_spans(self, size):
        life_spans = None
        if self.settings['life_span_distribution_type'] == 'Normal':
            mean, sd, lower, upper = self.settings['life_span']
            life_spans = np.random.normal(mean, sd, size).astype(int)
            life_spans = limiter(life_spans, lower, upper)

        elif self.settings['life_span_distribution_type'] == 'Uniform':
            lower, upper = self.settings['life_span']
            life_spans = np.random.uniform(lower, upper, size).astype(int)

        return life_spans.tolist()

    def determine_weights(self, life_spans: list):
        mean, increase, sd, lower, upper = self.settings['body_weight']
        weights = []
        for life_span in life_spans:
            weight = np.random.normal(loc=mean + increase * np.arange(1, life_span + 2),
                                      scale=sd, size=(int(life_span) + 1)).astype(int)
            limiter(weight, lower, upper)
            weights.append(weight.tolist())
        return weights

    def simulate_year(self) -> dict:

        adult_survival_probability = self.settings['adult_survival_rate']
        newborn_survival_probability = self.settings['newborn_survival_rate']
        survival_trial_first = self.settings['survival_trial_first']

        if self.settings['targeted_hunting']:
            adult_survival_probability = self.settings['targeted_hunting_survival_rate']
            self.settings['targeted_hunting'] = False

        if self.settings['artificial_insemination']:
            ai_females = self.animal_populations.choose_females(self.settings["AI_per_year"])
            if ai_females is False:
                pass
            else:
                for i in ai_females:
                    new_litter = self.create_litter(True)
                    i.mated = True
                    self.animal_populations.young_population.extend(new_litter)

        if self.settings['added_ge_carriers']:
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

    def mating(self):
        mating_groups = self.animal_populations.allocate_mates()
        for group in mating_groups:
            gene_edit = group[0].gene_edit
            for _ in group[1]:
                if _.mated is True:
                    pass
                elif _.gene_edit is True and self.settings['gene_drive_type'] is "Female Sterility":
                    "print owo"
                    pass
                else:
                    new_litter = self.create_litter(gene_edit)
                    self.animal_populations.young_population.extend(new_litter)


def limiter(variable, lower, upper):
    variable[variable < lower] = lower
    variable[variable > upper] = upper
    return variable


def simulate_n_years(population_type: callable, settings: dict,
                     male: Callable[[Iterable, int, bool, int], object],
                     female: Callable[[Iterable, int, bool, int], object]):
    sim = Simulation(population_type, settings, male, female)
    size_female = settings['starting_females']
    size_male = settings['starting_males']
    size_ge_male = settings['starting_ge_males']
    size_child_male = settings['starting_child_males']
    size_child_female = settings['starting_child_females']
    sim_stats = ([sim.initialize_simulation(size_male, size_ge_male, size_female, size_child_male, size_child_female)]
                 + [sim.simulate_year() for _ in range(settings['number_of_years'])])
    return sim_stats
