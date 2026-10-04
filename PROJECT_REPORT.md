# AI Escape Grid — Project Report

## 1. Project overview

**AI Escape Grid** is a small, single-player maze escape game built with Python and Pygame. The player moves through a randomly generated 10 × 10 grid, avoids walls and a pursuing enemy, and tries to reach the exit before the countdown ends. The enemy uses Breadth-First Search (BFS) to find a shortest path to the player's current position.

The project demonstrates a practical, visual use of a classical Artificial Intelligence search algorithm. It does not use machine learning: there is no trained model, training data, neural network, or learning process.

## 2. Objectives

- Build an interactive maze game with keyboard and mouse controls.
- Generate a different, playable maze scenario for each run.
- Use a pathfinding algorithm to make the enemy pursue the player.
- Provide selectable difficulty levels and a time-based challenge.
- Display the game and its status clearly using a graphical interface.

## 3. Technology and libraries used

| Technology | Use in the project |
|---|---|
| Python | Game logic, input handling, scenario generation, and program structure |
| Pygame | Window, drawing, keyboard/mouse events, fonts, clock, and display updates |
| `collections.deque` | FIFO queue used by BFS to explore grid cells in order |
| `random` | Shuffling possible wall locations and selecting exits and visual themes |
| `sys` | Exiting the program after the game loop |

The zombie sprite is drawn from shapes in Pygame, so the game does not rely on external image assets.

## 4. Game design and features

- The board is a 10 × 10 grid. The player starts at the top-left cell.
- The exit is selected from a set of cells near the bottom-right corner.
- Walls are placed randomly, with different target wall counts by difficulty.
- The game checks that the player can reach the exit and that a route exists for the enemy to reach the player's starting position. It also rejects wall placements that make the player-to-exit route longer than 29 cells.
- The game offers Easy, Medium, and Hard modes:

| Difficulty | Time limit | Target walls | Enemy starting cell |
|---|---:|---:|---|
| Easy | 45 seconds | 12 | (9, 0) |
| Medium | 35 seconds | 23 | (8, 0) |
| Hard | 30 seconds | 32 | (7, 0) |

- The player moves one cell at a time using arrow keys or WASD. Movement is restricted by the grid boundary and walls.
- After each legal player move, the enemy moves one cell along its newly calculated shortest path to the player.
- The player wins by reaching the exit. The game ends if the enemy catches the player or the timer reaches zero.
- A new scenario can be generated without leaving the selected difficulty. The game also supports returning to the level-selection screen.
- Four visual themes are available, and the generator avoids repeating the immediately previous theme.

## 5. Artificial Intelligence technique and algorithm

### Technique: uninformed graph search

The enemy uses **Breadth-First Search (BFS)**, a classical uninformed search technique. The grid is treated as a graph:

- Each walkable cell is a node.
- An edge connects cells that are directly adjacent vertically or horizontally.
- Walls and cells outside the board cannot be traversed.
- Every move has the same cost: one cell.

BFS uses a first-in, first-out queue. It explores all cells one step from the starting cell before exploring cells two steps away, and continues outward in layers. On this unweighted grid, the first path found to the target has the minimum number of moves.

### How the enemy uses BFS

1. A legal player move updates the player's cell.
2. The game calls `find_path_bfs()` with the enemy's current cell as the start and the player's new cell as the goal.
3. BFS searches around walls and records which cell each discovered cell came from.
4. The function reconstructs the path from the goal back to the start.
5. The enemy moves to the second cell in that path—the next cell after its current position.
6. The search is repeated after the next legal player move, so the enemy responds to the player's latest position.

### Pseudocode

```text
BFS(start, goal):
    queue = [start]
    predecessor[start] = none

    while queue is not empty:
        current = remove the oldest cell from queue

        if current is goal:
            stop searching

        for each up, down, left, and right neighbor:
            if neighbor is inside the grid, not a wall,
               and has not been visited:
                predecessor[neighbor] = current
                add neighbor to the end of queue

    if goal was not visited:
        return no path

    reconstruct and return the path from start to goal
```

For a graph with `V` walkable cells and `E` neighbor connections, BFS takes **O(V + E)** time and **O(V)** additional memory. Here the board is small and fixed at 100 cells, so each search is bounded by that grid.

### Procedural generation algorithm

The maze generator uses randomness with pathfinding-based checks:

1. Select a non-repeating theme and an exit cell.
2. Build a shuffled list of candidate cells, excluding the player start, enemy start, and exit.
3. Try adding candidate cells as walls until the difficulty's target wall count is reached.
4. After each attempted wall, run BFS to check that the player can still reach the exit within the route-length limit and that the enemy has a route to the player's starting position.
5. Remove a wall that violates either condition.

This makes the layout unpredictable while filtering out mazes that fail the generator's basic playability rules.

## 6. Main program components

- **`find_path_bfs()`** — searches for and reconstructs a shortest path through the grid.
- **`generate_scenario()`** — selects the exit and theme and creates a maze while checking routes.
- **`draw_menu()` and `draw_game()`** — render the menu, maze, status panel, timer, controls, and end screen.
- **`create_zombie_sprite()`** — draws the enemy sprite using Pygame shapes.
- **`main()`** — initializes Pygame, handles input and game states, updates the timer and characters, and runs the display loop.

The program uses a simple state-based flow: menu, playing, win, caught, and time-up states.

## 7. Strengths and limitations

### Strengths

- BFS is simple to explain and guarantees a shortest path when every move has equal cost.
- The enemy recalculates its path as the player moves, so pursuit adapts to the player's current location.
- Scenario generation combines randomness with reachability checks.
- The game has no external art requirement for its zombie sprite.

### Limitations

- The enemy uses a shortest-path pursuit strategy; it does not predict the player's future moves or learn from previous games.
- BFS is appropriate for this small, unweighted grid, but larger maps or maps with different movement costs may call for other algorithms, such as A* or Dijkstra's algorithm.
- The maze checks route length and reachability, but those checks do not prove that every generated scenario is equally difficult or always winnable against the enemy and timer.
- The game is single-player and has no saved scores or persistent player progression.

## 8. Possible future improvements

- Add A* pathfinding and compare its number of explored cells with BFS.
- Add enemy behaviors with different strategies, such as patrol or interception.
- Measure maze difficulty using route length, branching, and player escape opportunities.
- Add a score system, best-time record, sound effects, and more levels.
- Add automated tests for BFS paths, wall placement, and scenario reachability.

## 9. Conclusion

AI Escape Grid combines a graphical game loop, grid-based movement, randomized level generation, and classical AI search. Its main AI component is BFS, which allows the enemy to pursue the player along a shortest route through an unweighted maze. The project is a clear demonstration of how graph-search algorithms can be applied in an interactive application.

## Short presentation script

“My project is called AI Escape Grid. It is a maze game developed in Python using Pygame. The player has to reach an exit in a randomly generated 10-by-10 maze while avoiding an enemy and a countdown timer. The AI technique used is Breadth-First Search, or BFS. The maze is represented as a graph, and BFS checks neighboring cells layer by layer while ignoring walls. Because each move has the same cost, BFS finds a shortest route. After every valid player move, the enemy recalculates its route and moves one cell toward the player. The maze generator also uses random wall placement and BFS checks to preserve basic routes. This project uses search-based AI, not machine learning.”
