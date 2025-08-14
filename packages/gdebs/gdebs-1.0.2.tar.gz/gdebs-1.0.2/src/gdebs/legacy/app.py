from src.simulation import simulate_n_years
from src.animal_patch import PigPatch, Boar, Sow
import pandas as pd
import streamlit as st
import numpy as np
import multiprocessing as mp
import json
import time


def save_settings(settings: dict) -> None:
    with open(f"src/settings.json", "w") as file:
        json.dump(settings, file, indent=4)


def load_settings() -> dict:
    with open(f"src/settings.json", "r") as file:
        json_object = json.load(file)
        return json_object


def simulate_trial(seed: int):
    np.random.seed(seed)
    return simulate_n_years(PigPatch, load_settings(), Boar, Sow)


def simulation_for_n_trials(settings: dict) -> []:
    seeds = [int(time.time()) + i for i in range(settings['number_of_simulations'])]

    with mp.Pool() as pool:
        sim_array = pool.map(simulate_trial, seeds)
    return sim_array


# Population specific data
POP_COLUMN = 'Total Population'
EFFECTIVE_POP_COLUMN = 'Effective Population'
MALE_COLUMN = 'Males'
FEMALE_COLUMN = 'Females'
GD_FEMALE_COLUMN = 'Gene Drive Females'

# 95% CI
CONFIDENCE_LEVEL = 1.96

settings = {}

st.title("Gene Drive Spread Simulator")
st.text("Simulate the spread of a gene drive that "
        "affects a sow's reproductive capabilities.")

sim_name = st.text_input("Simulation Name")
animal_type = st.selectbox("Species", ["Feral Pigs", ])

# Environmental Parameters
with st.expander("Starting population and Rate parameters"):
    col1, col2, col3 = st.columns(3)
    with col1:
        settings["starting_males"] = st.number_input("Male population", min_value=1,
                                                     max_value=2 ** 31, step=1, value=500)
        settings["sex_rate"] = st.number_input("Ratio of male to female birth", value=0.5,
                                               min_value=0.000001, max_value=1.0)
        settings["starting_child_males"] = st.number_input("Male newborn population", min_value=0,
                                                           max_value=2 ** 31, step=1, value=500)

    with col2:
        settings["starting_females"] = st.number_input("Female population", min_value=1,
                                                       max_value=2 ** 31, step=1, value=500)
        settings["adult_survival_rate"] = st.number_input("Adult survival rate", value=0.87,
                                                          min_value=0.000001, max_value=1.0)
        settings["starting_child_females"] = st.number_input("Female newborn population", min_value=0,
                                                             max_value=2 ** 31, step=1, value=500)

    with col3:
        settings["starting_ge_males"] = st.number_input("Gene edit carrying male population", min_value=0,
                                                        max_value=2 ** 31, step=1)
        settings["newborn_survival_rate"] = st.number_input("Newborn first year survival rate", value=0.45,
                                                            min_value=0.0, max_value=1.0)
        settings["gene_edit_success_rate"] = st.number_input("Gene drive success rate", value=0.85,
                                                             min_value=0.000001, max_value=1.0)

# Random variables and distribution settings
with st.expander("Animal parameters"):
    # Lifespan
    settings["life_span_distribution_type"] = st.selectbox("Choose a distribution for lifespan",
                                                           ["Normal", "Uniform"])

    if settings["life_span_distribution_type"] == "Normal":
        col1, col2, col3, col4 = st.columns(4)
        settings["life_span"] = list(range(4))

        with col1:
            settings["life_span"][0] = st.number_input("Mean", min_value=1, max_value=500,
                                                       value=5)
        with col2:
            settings["life_span"][1] = st.number_input("Standard Deviation", min_value=1, max_value=500,
                                                       value=2)
        with col3:
            settings["life_span"][2] = st.number_input("Lower Bound", min_value=1, max_value=500,
                                                       value=1)

        with col4:
            settings["life_span"][3] = st.number_input("Upper Bound", min_value=1, max_value=500,
                                                       value=6)

    if settings["life_span_distribution_type"] == "Uniform":
        col1, col2 = st.columns(2)
        settings["life_span"] = list(range(2))

        with col1:
            settings["life_span"][0] = st.number_input("Lower bound", min_value=1, max_value=500,
                                                       value=1)

        with col2:
            settings["life_span"][1] = st.number_input("Upper bound", min_value=1, max_value=500,
                                                       value=6)

    st.markdown('-----------------------------')

    # Body weight
    settings["body_weight_distribution_type"] = st.selectbox("Choose a distribution for body weight",
                                                             ["Normal"])

    if settings["body_weight_distribution_type"] == "Normal":
        col1, col2, col3, col4, col5 = st.columns(5)
        settings["body_weight"] = list(range(5))

        with col1:
            settings["body_weight"][0] = st.number_input("Mean", min_value=1, max_value=2000,
                                                         value=250)
        with col2:
            settings["body_weight"][1] = st.number_input("Increase / year", min_value=1, max_value=2000,
                                                         value=50)
        with col3:
            settings["body_weight"][2] = st.number_input("Standard Deviation", min_value=1, max_value=2000,
                                                         value=50)
        with col4:
            settings["body_weight"][3] = st.number_input("Lower Bound", min_value=1, max_value=2000,
                                                         value=10)

        with col5:
            settings["body_weight"][4] = st.number_input("Upper Bound", min_value=1, max_value=2000,
                                                         value=400)

    st.markdown('-----------------------------')

    # Body weight
    settings["litter_size_distribution_type"] = st.selectbox("Choose a distribution for litter size",
                                                             ["Poisson"])

    if settings["litter_size_distribution_type"] == "Poisson":
        col1, col2, col3 = st.columns(3)
        settings["litter_size"] = list(range(3))

        with col1:
            settings["litter_size"][0] = st.number_input("Lambda", min_value=0, max_value=1000,
                                                         value=5)

        with col2:
            settings["litter_size"][1] = st.number_input("Lower Bound", min_value=0, max_value=1000,
                                                         value=1)

        with col3:
            settings["litter_size"][2] = st.number_input("Upper Bound", min_value=1, max_value=1000,
                                                         value=8)

with st.expander("Simulation Parameters"):
    col1, col2, col3 = st.columns(3)
    with col1:
        # No. of litters for each sow should be a random poisson number between 0 and max value
        settings["number_of_litters"] = st.number_input("Max no. of litters per year", min_value=0,
                                                        max_value=2 ** 31, step=1, value=1)
    with col2:
        settings["number_of_years"] = st.number_input("Number of years per simulation trial", value=20,
                                                      min_value=0, max_value=100, step=1)
    with col3:
        settings["number_of_simulations"] = st.number_input("Number of simulation trials", value=20,
                                                            min_value=1, max_value=2 ** 31, step=1)

with st.expander("Gene Drive Introduction Options"):
    col1, col2, col3 = st.columns(3)
    with col1:
        settings["gene_drive_type"] = st.selectbox("Select a Gene Drive Type", ["Female Sterility",
                                                                                "Female Lethality"])
        # settings["gd_sex_rate"] = st.number_input("Female lethality sex rate", min_value=0, max_value=1)

        settings["artificial_insemination"] = st.checkbox("Artificial Insemination")
        if settings["artificial_insemination"]:
            settings["AI_per_year"] = st.number_input(
                "How many sows do you want to artificially inseminate each year?",
                min_value=0,
                max_value=2 ** 31,
                value=0, step=1)

    with col2:
        settings["targeted_hunting"] = st.checkbox(
            "Targeted Hunting - this decreases the survival rate of non-gene-edited animal")
        if settings["targeted_hunting"]:
            settings["targeted_hunting_survival_rate"] = st.number_input(
                "Set the first year adult survival rate:",
                min_value=0.0,
                max_value=1.0,
                value=0.25,
                step=0.01
            )

    with col3:
        settings["added_ge_carriers"] = st.checkbox("Add new gene drive carrying males each year")
        if settings["added_ge_carriers"]:
            settings["number_of_added_GE_boars"] = st.number_input(
                "How many gene edited boars do you want to add each year?",
                min_value=0,
                max_value=2 ** 31,
                value=0, step=1)

with st.expander("Extra"):
    col1, col2 = st.columns(2)
    with col1:
        settings['survival_trial_first'] = st.checkbox("Test survival first")


def run_simulation(settings):
    sim_array = simulation_for_n_trials(settings)
    flattened_data = [[[value for value in sim_array.values()] for sim_array in lst] for lst in sim_array]
    array_3d = np.array(flattened_data)
    mean_array = np.mean(array_3d, axis=0, dtype=int)
    std_array = np.std(array_3d, axis=0)
    return mean_array, std_array


def analyze_sim(mean_arr: np.ndarray, std_arr: np.ndarray):
    mean_df = pd.DataFrame(mean_arr, columns=["Normal_Males",
                                              "Normal_Females",
                                              "Gene_Edit_Males",
                                              "Gene_Edit_Females",
                                              "Young_Population",
                                              "Adult_Population",
                                              "Total_Population",
                                              "Effective_Adult_Population"])

    sd_df = pd.DataFrame(std_arr, columns=["Normal_Males",
                                           "Normal_Females",
                                           "Gene_Edit_Males",
                                           "Gene_Edit_Females",
                                           "Young_Population",
                                           "Adult_Population",
                                           "Total_Population",
                                           "Effective_Adult_Population"])

    mean_df['Year'] = mean_df.index.astype(int)
    sd_df['Year'] = sd_df.index.astype(int)
    cols = mean_df.columns.tolist()
    cols2 = sd_df.columns.tolist()
    cols = cols[-1:] + cols[:-1]
    cols2 = cols2[-1:] + cols2[:-1]
    mean_df = mean_df[cols]
    sd_df = sd_df[cols2]
    return mean_df, sd_df


# def display_graphs(df):
#     st.line_chart(df[['Year', 'Normal_Males', 'Normal_Females', 'Gene_Edit_Males', 'Gene_Edit_Females',
#                       'Young_Population',
#                       'Total_Population']], x="Year")

def display_graphs(df):
    st.line_chart(df[['Year', 'Normal_Males', 'Normal_Females', 'Gene_Edit_Males', 'Young_Population',
                      'Total_Population']], x="Year")


def save_csv(df1: pd.DataFrame, df2: pd.DataFrame, sim_name: str, settings: dict):
    from pathlib import Path
    dir_path = Path(f'./data/{sim_name}')
    dir_path.mkdir(parents=True, exist_ok=True)
    df1_path = Path(f'./data/{sim_name}/mean.csv')
    df2_path = Path(f'./data/{sim_name}/std.csv')
    df1.to_csv(df1_path, index=False)
    df2.to_csv(df2_path, index=False)
    with open(f'{dir_path}/settings.json', "w") as file:
        json.dump(settings, file, indent=4)


if st.button("Run simulation", type="primary"):
    st.write("Simulation has started")
    save_settings(settings)
    mean_arr, std_arr = run_simulation(settings)
    st.write("Simulation completed owo")
    mean_df, std_df = analyze_sim(mean_arr, std_arr)
    save_csv(mean_df, std_df, sim_name, settings)
    st.write(mean_df)
    display_graphs(mean_df)
    print(mean_df)
    st.write("The total population you see above also accounts for all of the children. However, their low survival "
             "rate leads to most of them dying anyways which is why we don't see them reach adulthood.")


