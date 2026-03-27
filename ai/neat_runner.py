"""
NEAT runner for Neural Flappy Bird.
Handles NEAT population setup, the eval_genomes function,
and the generation loop integrated with Pygame rendering.
"""

import os
import neat
from game.bird import Bird
from game.world import World
from utils.colors import SPECIES_COLORS


class NeatRunner:
    """Manages the NEAT evolutionary process."""

    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config = neat.Config(
            neat.DefaultGenome,
            neat.DefaultReproduction,
            neat.DefaultSpeciesSet,
            neat.DefaultStagnation,
            config_path,
        )
        self.population: neat.Population | None = None
        self.generation = 0
        self.best_genome: neat.DefaultGenome | None = None
        self.best_fitness_ever = 0.0
        self.fitness_history: list[float] = []
        self.species_count = 0

        # Current generation state
        self.world = World()
        self.current_genomes: list[tuple] = []  # (genome_id, genome)
        self.current_nets: list = []

    def setup(self) -> None:
        """Initialize the NEAT population."""
        self.population = neat.Population(self.config)
        self.population.add_reporter(neat.StdOutReporter(True))
        self.generation = 0
        self.best_genome = None
        self.best_fitness_ever = 0.0
        self.fitness_history.clear()

    def create_birds_for_generation(
        self, genomes: list[tuple], config: neat.Config
    ) -> list[Bird]:
        """Create Bird objects from NEAT genomes for a generation."""
        birds = []
        species_map = {}

        # Build a species map from the population
        if self.population and self.population.species:
            for sid, species in self.population.species.species.items():
                for gid in species.members:
                    species_map[gid] = sid

        for genome_id, genome in genomes:
            genome.fitness = 0.0
            net = neat.nn.FeedForwardNetwork.create(genome, config)
            species_id = species_map.get(genome_id, 0)
            bird = Bird(
                x=World.BIRD_START_X,
                y=300,
                genome=genome,
                network=net,
                species_id=species_id % len(SPECIES_COLORS),
            )
            birds.append(bird)

        return birds

    def start_generation(self, genomes: list[tuple], config: neat.Config) -> None:
        """Begin a new generation: create birds and reset world."""
        self.generation += 1
        self.current_genomes = genomes
        birds = self.create_birds_for_generation(genomes, config)
        self.world.reset(birds)

        # Count species
        if self.population and self.population.species:
            self.species_count = len(self.population.species.species)
        else:
            self.species_count = 1

    def end_generation(self) -> None:
        """Finalize a generation: record fitness, track best."""
        # Find the best genome this generation
        best_fitness = 0.0
        for bird in self.world.birds:
            fitness = bird.get_fitness()
            bird.genome.fitness = fitness
            if fitness > best_fitness:
                best_fitness = fitness
                if fitness > self.best_fitness_ever:
                    self.best_fitness_ever = fitness
                    self.best_genome = bird.genome

        self.fitness_history.append(best_fitness)

    def get_alive_count(self) -> int:
        """Get number of alive birds."""
        return len(self.world.get_alive_birds())

    def get_total_count(self) -> int:
        """Get total number of birds this generation."""
        return len(self.world.birds)

    def get_best_bird(self) -> Bird | None:
        """Get the current best performing alive bird."""
        return self.world.get_best_bird()
