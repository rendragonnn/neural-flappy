"""
Neural Flappy Bird — Main Entry Point
Author: rendragonnn
Version: 1.0.0

A NEAT-powered evolutionary AI that learns to play Flappy Bird.
Features real-time neural network visualization and fitness history graphs.
"""

import os
import sys
import pygame
import neat

from game.world import World
from game.bird import Bird
from ai.neat_runner import NeatRunner
from ai.genome_store import save_genome, load_genome
from ui.hud import HUD
from ui.visualizer import NeuralNetVisualizer
from ui.stats_panel import StatsPanel
from utils.colors import BG_COLOR, PANEL_DIVIDER, PANEL_BORDER


# ── Constants ───────────────────────────────────────────────────────
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 700
GAME_WIDTH = 800
FPS = 60
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config-feedforward.txt")

# Speed multiplier steps
SPEED_OPTIONS = [1, 2, 5, 10]


def get_node_values(bird: Bird) -> dict[int, float]:
    """Extract node activation values from a bird's network for visualization."""
    if bird is None or not bird.alive:
        return {}
    net = bird.network
    values: dict[int, float] = {}
    # Input values
    if hasattr(net, "input_nodes") and hasattr(net, "values"):
        for k, v in net.values.items():
            values[k] = v
    else:
        # Manual extraction from FeedForwardNetwork
        # The network stores values internally; we reconstruct from the last activation
        try:
            # Get input node IDs
            config = neat.Config(
                neat.DefaultGenome,
                neat.DefaultReproduction,
                neat.DefaultSpeciesSet,
                neat.DefaultStagnation,
                CONFIG_PATH,
            )
            input_keys = config.genome_config.input_keys
            output_keys = config.genome_config.output_keys

            # Get last inputs from world
            world_inputs = bird._last_inputs if hasattr(bird, "_last_inputs") else []
            for i, key in enumerate(sorted(input_keys)):
                if i < len(world_inputs):
                    values[key] = world_inputs[i]

            # Get node values from network's internal state
            if hasattr(net, "node_evals"):
                for node_eval in net.node_evals:
                    node_id = node_eval[0]
                    # We'll use genome fitness or output as approximate
                    if node_id in output_keys:
                        # Get last output
                        if hasattr(bird, "_last_output"):
                            values[node_id] = bird._last_output
                        else:
                            values[node_id] = 0.0
                    elif node_id not in input_keys:
                        # Hidden node — approximate
                        values[node_id] = 0.5
        except Exception:
            pass
    return values


class App:
    """Main application class orchestrating the NEAT evolution with Pygame."""

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Neural Flappy Bird — by rendragonnn")
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()

        self.hud = HUD()
        self.visualizer = NeuralNetVisualizer()
        self.stats_panel = StatsPanel()

        self.neat_runner = NeatRunner(CONFIG_PATH)
        self.speed_index = 0  # index into SPEED_OPTIONS
        self.paused = False
        self.running = True
        self.showcase_mode = False

        # Generation control
        self._generation_running = False
        self._restart_requested = False

    def run(self) -> None:
        """Main application loop using NEAT's run method."""
        self.neat_runner.setup()

        try:
            self.neat_runner.population.run(self._eval_genomes, n=1000)
        except SystemExit:
            pass
        except KeyboardInterrupt:
            pass
        finally:
            pygame.quit()

    def run_showcase(self, genome: neat.DefaultGenome, config: neat.Config) -> None:
        """Run a single genome in showcase mode."""
        self.showcase_mode = True
        self.hud.showcase_mode = True
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        bird = Bird(x=World.BIRD_START_X, y=300, genome=genome, network=net, species_id=0)

        world = World()
        world.reset([bird])

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                        return
                    self._handle_key(event.key)

            if not self.paused:
                alive = world.update()
                if not alive:
                    # Restart showcase
                    genome.fitness = 0.0
                    net = neat.nn.FeedForwardNetwork.create(genome, config)
                    bird = Bird(x=World.BIRD_START_X, y=300, genome=genome, network=net, species_id=0)
                    world.reset([bird])

            # Store inputs for visualization
            if bird.alive:
                inputs = world.get_inputs_for_bird(bird)
                bird._last_inputs = inputs
                output = net.activate(inputs)
                bird._last_output = output[0]

            # Render
            self.screen.fill(BG_COLOR)
            world.draw(self.screen)

            # Panel divider
            pygame.draw.line(
                self.screen, PANEL_BORDER,
                (GAME_WIDTH, 0), (GAME_WIDTH, WINDOW_HEIGHT), 2
            )

            # HUD
            self.hud.draw(
                self.screen,
                generation=0,
                alive=1 if bird.alive else 0,
                total=1,
                score=world.score,
                best_score=world.best_score,
                species=1,
                fps=self.clock.get_fps(),
            )
            self.hud.draw_controls_hint(self.screen)

            # Visualizer
            node_vals = get_node_values(bird)
            self.visualizer.draw(
                self.screen,
                genome=genome,
                config=config,
                net=net,
                node_values=node_vals,
                generation=0,
                species_id=0,
            )

            # Stats
            self.stats_panel.draw(self.screen, [], 0)

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()

    def _eval_genomes(
        self, genomes: list[tuple[int, neat.DefaultGenome]], config: neat.Config
    ) -> None:
        """Evaluate all genomes for one generation — called by NEAT's population.run()."""
        if not self.running:
            raise SystemExit

        if self._restart_requested:
            self._restart_requested = False
            self.neat_runner.setup()
            raise SystemExit

        self.neat_runner.start_generation(genomes, config)
        world = self.neat_runner.world

        # Game loop for this generation
        generation_alive = True
        while generation_alive and self.running:
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    self.neat_runner.end_generation()
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    self._handle_key(event.key)

            if self._restart_requested:
                break

            if self.paused:
                self._render(world)
                self.clock.tick(FPS)
                continue

            # Run game steps based on speed multiplier
            speed = SPEED_OPTIONS[self.speed_index]
            for _ in range(speed):
                # Store inputs for visualization before update
                best_bird = world.get_best_bird()
                if best_bird and best_bird.alive:
                    inputs = world.get_inputs_for_bird(best_bird)
                    best_bird._last_inputs = inputs
                    output = best_bird.network.activate(inputs)
                    best_bird._last_output = output[0]

                generation_alive = world.update()
                if not generation_alive:
                    break

            self._render(world)
            self.clock.tick(FPS)

        self.neat_runner.end_generation()

    def _handle_key(self, key: int) -> None:
        """Handle keyboard input."""
        if key == pygame.K_SPACE:
            self.paused = not self.paused
            self.hud.paused = self.paused
        elif key == pygame.K_UP:
            self.speed_index = min(self.speed_index + 1, len(SPEED_OPTIONS) - 1)
            self.hud.speed_multiplier = SPEED_OPTIONS[self.speed_index]
        elif key == pygame.K_DOWN:
            self.speed_index = max(self.speed_index - 1, 0)
            self.hud.speed_multiplier = SPEED_OPTIONS[self.speed_index]
        elif key == pygame.K_r:
            self._restart_requested = True
        elif key == pygame.K_s:
            if self.neat_runner.best_genome:
                save_genome(self.neat_runner.best_genome, self.neat_runner.config)
        elif key == pygame.K_l:
            result = load_genome()
            if result:
                genome, config = result
                self.running = False
                pygame.quit()
                # Restart in showcase mode
                app = App()
                app.run_showcase(genome, config)
                sys.exit()

    def _render(self, world: World) -> None:
        """Render the full screen."""
        self.screen.fill(BG_COLOR)

        # Game panel
        world.draw(self.screen)

        # Panel divider
        pygame.draw.line(
            self.screen, PANEL_BORDER,
            (GAME_WIDTH, 0), (GAME_WIDTH, WINDOW_HEIGHT), 2
        )
        # Horizontal divider between NN and stats panels
        pygame.draw.line(
            self.screen, PANEL_BORDER,
            (GAME_WIDTH, 400), (WINDOW_WIDTH, 400), 1
        )

        # HUD
        best_bird = world.get_best_bird()
        self.hud.draw(
            self.screen,
            generation=self.neat_runner.generation,
            alive=self.neat_runner.get_alive_count(),
            total=self.neat_runner.get_total_count(),
            score=world.score,
            best_score=world.best_score,
            species=self.neat_runner.species_count,
            fps=self.clock.get_fps(),
        )
        self.hud.draw_controls_hint(self.screen)

        # Neural network visualizer
        if best_bird and best_bird.alive:
            node_vals = get_node_values(best_bird)
            self.visualizer.draw(
                self.screen,
                genome=best_bird.genome,
                config=self.neat_runner.config,
                net=best_bird.network,
                node_values=node_vals,
                generation=self.neat_runner.generation,
                species_id=best_bird.species_id,
            )
        else:
            self.visualizer.draw(
                self.screen,
                genome=None,
                config=None,
                net=None,
                node_values=None,
                generation=self.neat_runner.generation,
            )

        # Stats panel
        self.stats_panel.draw(
            self.screen,
            self.neat_runner.fitness_history,
            self.neat_runner.best_fitness_ever,
        )

        pygame.display.flip()


def main() -> None:
    """Entry point."""
    # Check for showcase mode from command line
    if len(sys.argv) > 1 and sys.argv[1] == "--showcase":
        result = load_genome()
        if result:
            genome, config = result
            app = App()
            app.run_showcase(genome, config)
        else:
            print("No saved genome found. Run training first.")
        return

    app = App()
    app.run()


if __name__ == "__main__":
    main()
