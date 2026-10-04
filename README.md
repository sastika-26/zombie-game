# AI Escape Grid

A 10x10 escape game made with Python and Pygame. Every run creates a fresh, solvable maze with a new exit location. Reach the gold exit before the timer expires while a BFS-controlled enemy follows the shortest route to you.

## Run the game

Install Python, then open a terminal in this project folder and run:

```bash
pip install pygame
python main.py
```

On Python 3.14, if `pip install pygame` cannot find a compatible wheel, install the compatible Community Edition instead:

```bash
pip install pygame-ce
python main.py
```

`pygame-ce` provides the same `pygame` import used by this project.

## How to play

- Choose **Easy**, **Medium**, or **Hard** from the opening screen. Click a level, or press **1**, **2**, or **3**, then press **Enter** to start.
- Move one tile with an **Arrow Key** or **WASD**.
- Reach the gold exit to win.
- Avoid the coral-colored enemy. It moves one tile after each legal player move.
- Press **R** or click **NEW SCENARIO** to generate a different maze at the same difficulty.
- Press **M** or click **CHANGE DIFFICULTY** to return to level selection. Press **Esc** to quit.

## Difficulty levels

- **Easy:** 45 seconds, 12 walls, and the enemy starts farther away.
- **Medium:** 35 seconds, 23 walls, and the enemy starts closer.
- **Hard:** 30 seconds, 32 walls, and the enemy starts closest.

Each generated maze is checked to ensure there is a route from the player to the exit and a route for the enemy to pursue the player.

## How the BFS enemy works

Breadth-First Search (BFS) explores the grid one step at a time. It checks all reachable neighboring tiles before moving on to tiles farther away, so the first route it finds to the player uses the fewest steps. Wall tiles are skipped during this search.

After each successful player move, the game runs BFS from the enemy's position to the player's new position. It then moves the enemy to the next tile on that shortest path. The search is small and easy to follow in `find_path_bfs()` in `main.py`.

## Project files

- `main.py` - game, drawing, controls, timer, and BFS pathfinding
- `README.md` - setup, controls, and a short explanation of the AI