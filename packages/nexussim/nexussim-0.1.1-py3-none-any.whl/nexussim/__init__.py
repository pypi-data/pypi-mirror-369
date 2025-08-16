# File: nexussim/__init__.py

# This makes the core classes and functions available at the top level,
# allowing for cleaner imports like 'from nexussim import DiseaseModel'.

from .core import DiseaseModel, Agent
from .analysis import (
    get_simulation_files,
    generate_epidemic_curve,
    analyze_patches,
    track_infection_centroid,
    create_animation,
    calculate_rate_of_spread,
    create_persistence_map,
)

# You can also define a package-level version variable
__version__ = "0.1.0"