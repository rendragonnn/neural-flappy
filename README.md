# 🐦 Neural Flappy Bird

## ✨ Features

- **NEAT Evolution** — Population of 30 birds evolves neural networks from scratch
- **Real-time Neural Network Visualizer** — Watch the best bird's brain fire in real-time
- **Fitness History Graph** — Track evolution progress across generations
- **Species Coloring** — Each species gets a unique color for easy identification
- **Speed Control** — Run at 1x, 2x, 5x, or 10x speed to fast-forward evolution
- **Save/Load Best Genome** — Persist the champion and replay it in showcase mode
- **No External Assets** — Everything is drawn with Pygame primitives
- **Beautiful Dark UI** — Clean, modern interface with accent colors

---

## 🧠 How NEAT Works

**NEAT** (NeuroEvolution of Augmenting Topologies) is an evolutionary algorithm that evolves both the **weights** and the **structure** of neural networks. Unlike traditional neuroevolution that uses a fixed topology, NEAT starts with minimal networks (just inputs connected to outputs) and gradually adds complexity through mutations.

Each bird in the game has its own neural network that takes 5 inputs: the bird's vertical position, its velocity, the distance to the next pipe, and the top and bottom positions of the pipe gap. The network outputs a single value — if it's above 0.5, the bird flaps.

Every generation, the population of 30 birds plays the game simultaneously. Birds that survive longer and pass more pipes receive higher fitness scores. The best-performing genomes are selected as parents for the next generation, with mutations that can add new nodes, new connections, or modify existing weights.

NEAT also uses **speciation** — grouping similar networks together so that new innovations have time to optimize before competing with established strategies. This prevents premature convergence and allows the population to explore diverse solutions.

---

## 🚀 Installation

```bash
git clone https://github.com/rendragonnn/neural-flappy
cd neural-flappy
pip install -r requirements.txt
python main.py
```

### Requirements

- Python 3.10+
- Pygame 2.5.2
- neat-python 0.92
- numpy 1.26.4

---

## 🎮 Controls

| Key     | Action                                  |
| ------- | --------------------------------------- |
| `SPACE` | Pause / Resume                          |
| `UP`    | Increase speed (1x → 2x → 5x → 10x)     |
| `DOWN`  | Decrease speed                          |
| `R`     | Restart from generation 1               |
| `S`     | Save best genome to file                |
| `L`     | Load best genome and watch it play solo |
| `ESC`   | Quit (in showcase mode)                 |

---

## ⚙️ NEAT Configuration

| Parameter            | Value | Description                                           |
| -------------------- | ----- | ----------------------------------------------------- |
| `pop_size`           | 30    | Number of birds per generation                        |
| `fitness_threshold`  | 5000  | Fitness score to "solve" the game                     |
| `activation`         | tanh  | Activation function for all nodes                     |
| `weight_mutate_rate` | 0.8   | Probability of mutating a connection weight           |
| `node_add_prob`      | 0.2   | Probability of adding a new hidden node               |
| `conn_add_prob`      | 0.5   | Probability of adding a new connection                |
| `max_stagnation`     | 20    | Generations without improvement before species dies   |
| `survival_threshold` | 0.3   | Fraction of species members that survive to reproduce |

---

## 📁 Project Structure

```
neural-flappy/
├── main.py              # Entry point, NEAT loop, game orchestration
├── game/
│   ├── __init__.py
│   ├── bird.py          # Bird physics, animation, genome binding
│   ├── pipe.py          # Pipe generation, scrolling, gap logic
│   ├── ground.py        # Scrolling ground
│   └── world.py         # Game world state, collision, scoring
├── ai/
│   ├── __init__.py
│   ├── neat_runner.py   # NEAT setup, fitness function, generation loop
│   └── genome_store.py  # Save/load best genome as pickle
├── ui/
│   ├── __init__.py
│   ├── hud.py           # HUD overlay: gen, alive, score, fps
│   ├── visualizer.py    # Real-time neural network visualizer panel
│   └── stats_panel.py   # Generation history graph (fitness over time)
├── utils/
│   ├── __init__.py
│   ├── colors.py        # All color constants
│   └── fonts.py         # Font loader helper
├── config-feedforward.txt
├── requirements.txt
└── README.md
```

---

## 📄 License

MIT License — feel free to use, modify, and distribute.

---

**Made with ❤️ by [rendragonnn](https://github.com/rendragonnn)**
