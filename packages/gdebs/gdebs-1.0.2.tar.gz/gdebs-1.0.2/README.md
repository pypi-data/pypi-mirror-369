# gdebs - Gene Drive Simulation Package

An event-based simulation package for observing the spread of a gene drive in animal populations.

## Description

The gdebs library simulates the spread of gene drives in animal populations. Gene drives are genetic modifications that can be inherited and affect reproduction or survival, specifically:

1. **Female Sterility Drive**: Females cannot mate and have offspring
2. **Female Lethality Drive**: Females die at birth

Males are unaffected by these gene drives but can pass them down to their offspring. This library provides tools for simulating, analyzing, and visualizing the spread of these gene drives in populations over time.

## Installation

### Requirements

- Python 3.13 or higher
- Dependencies:
  - numpy
  - pandas
  - matplotlib
  - streamlit (for web interface)

### Installing from PyPI

```bash
pip install gdebs
```

### Installing from Source

1. Clone the repository:
```bash
git clone https://github.com/rsnarang/gdebs.git
cd gdebs
```

2. Install the package:
```bash
pip install -e .
```

## Usage

### Basic Simulation

Here's a simple example to run a gene drive simulation:

```python
import numpy as np
from time import time
from gdebs import PigPatch, Boar, Sow, simulate_n_years, get_default_settings

# Get default settings
settings = get_default_settings()

# Customize settings
settings["number_of_simulations"] = 10
settings["starting_males"] = 500
settings["starting_females"] = 500
settings["starting_ge_males"] = 50  # Start with gene-edited males
settings["gene_edit_success_rate"] = 0.9  # Success rate for passing gene drive

# Run simulation
np.random.seed(42)  # Set seed for reproducibility
result = simulate_n_years(PigPatch, settings, Boar, Sow)

# Access results
for year, stats in enumerate(result):
    print(f"Year {year}:")
    print(f"  Total population: {stats['Total_Population']}")
    print(f"  Gene-edited animals: {stats['Gene_Edit_Males'] + stats['Gene_Edit_Females']}")
```

### Analyzing and Visualizing Results

The library provides tools for analyzing and visualizing simulation results:

```python
from gdebs import analyze_simulation, display_graphs
import pandas as pd

# Run multiple simulations
sim_array = []
for i in range(settings["number_of_simulations"]):
    np.random.seed(1000 + i)
    result = simulate_n_years(PigPatch, settings, Boar, Sow)
    sim_array.append(result)

# Analyze results
mean_array, std_array = analyze_simulation(sim_array)

# Create DataFrame for visualization
column_names = [
    "Normal_Males", "Normal_Females", 
    "Gene_Edit_Males", "Gene_Edit_Females",
    "Young_Population", "Adult_Population", 
    "Total_Population", "Effective_Adult_Population"
]

mean_df = pd.DataFrame(mean_array, columns=column_names)
mean_df['Year'] = mean_df.index.astype(int)

# Move Year to first column
cols = mean_df.columns.tolist()
cols = cols[-1:] + cols[:-1]
mean_df = mean_df[cols]

# Display graphs
display_graphs(mean_df)
```

### Web Interface

The package includes a Streamlit web interface for easy interaction:

```bash
cd examples
streamlit run app.py
```

This will launch a web application where you can:
- Configure all simulation parameters
- Run simulations with different settings
- Visualize and analyze results
- Save simulation data for further analysis

## Settings Configuration

The simulation is highly configurable through settings:

```python
from gdebs import get_default_settings, save_settings, load_settings

# Get default settings
settings = get_default_settings()

# Modify settings
settings["starting_males"] = 1000
settings["starting_females"] = 1000
settings["gene_edit_success_rate"] = 0.75

# Save settings to file
save_settings(settings, "my_simulation_settings.json")

# Load settings from file
settings = load_settings("my_simulation_settings.json")
```

### Key Settings Parameters

- **Population Parameters**:
  - `starting_males`: Initial male population
  - `starting_females`: Initial female population
  - `starting_ge_males`: Initial gene-edited male population
  - `starting_child_males`: Initial male child population
  - `starting_child_females`: Initial female child population

- **Rate Parameters**:
  - `sex_rate`: Ratio of male to female birth (0.5 = equal)
  - `adult_survival_rate`: Probability of adults surviving each year
  - `newborn_survival_rate`: Probability of newborns surviving first year
  - `gene_edit_success_rate`: Probability of passing gene drive to offspring

- **Simulation Parameters**:
  - `number_of_litters`: Maximum number of litters per female per year
  - `number_of_years`: Duration of simulation in years
  - `number_of_simulations`: Number of simulation trials to run

- **Gene Drive Introduction**:
  - `artificial_insemination`: Enable artificial insemination
  - `targeted_hunting`: Enable targeted hunting
  - `added_ge_carriers`: Add new gene drive carriers each year

## Project Structure

- **core**: Core classes for animals and population dynamics
- **simulation**: Simulation engine and algorithms
- **utils**: Utility functions and settings management
- **visualization**: Data analysis and visualization tools
- **examples**: Example scripts and applications
- **tests**: Test suite for the library

## License

This project is licensed under the GNU General Public License v3.0 - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Author

Rocky Sam Narang (rnarang@uoguelph.ca; rssnarang@gmail.com) 