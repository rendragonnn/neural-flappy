"""
Save and load the best NEAT genome as a pickle file.
"""

import os
import pickle
import neat


GENOME_FILE = "best_genome.pkl"


def save_genome(genome: neat.DefaultGenome, config: neat.Config, filepath: str = GENOME_FILE) -> None:
    """Save the best genome and config to a pickle file."""
    data = {
        "genome": genome,
        "config": config,
    }
    with open(filepath, "wb") as f:
        pickle.dump(data, f)
    print(f"[GenomeStore] Saved best genome to {filepath}")


def load_genome(filepath: str = GENOME_FILE) -> tuple[neat.DefaultGenome, neat.Config] | None:
    """Load a saved genome and config from a pickle file.
    Returns (genome, config) or None if file doesn't exist.
    """
    if not os.path.exists(filepath):
        print(f"[GenomeStore] No saved genome found at {filepath}")
        return None
    with open(filepath, "rb") as f:
        data = pickle.load(f)
    print(f"[GenomeStore] Loaded genome from {filepath}")
    return data["genome"], data["config"]
