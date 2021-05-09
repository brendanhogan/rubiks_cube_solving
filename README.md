# Rubik's Cube Solving Visualization
[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Implementation and visualization of Depth First Search, Breadth First Search, and Best First Search for the Rubik's Cube.

Additionally, this repository has the capability to design and add new solvers.

## Original Rubik's Visualization
All of the cube visualization and mechanics, and general GUI layout is directly from the [MagicCube](https://github.com/davidwhogg/MagicCube) repository. The original code from that repository is in the ```MagicCube``` directory completely unchanged with the original license. All of the added features to the original MagicCube are in ```main.py``` and ```solvers.py``` which override and add methods to the original classes in MagicCube.

## Added features

The added features are explained in depth below, but include the ability to directly model and track the cube numerically, create an interface for solvers to interact with the cube, as well as an informal class interface for those solvers, three solver implementations, and a visualization of the state tree structure explored by the solvers.

## Requirements

To install the necessary environment using CONDA:

```setup
conda env create --name rubiks --file=environment.yml
```

Or look at ``` environment.yml ``` for necessary packages and versions.

## Code Structure
As mentioned above, the code in ```MagicCube``` is directly sourced from the original repository, unedited.

The added functionality is contained in ```main.py``` and ```solvers.py```.

-```main.py``` loads environment, sets up the internal cube tracking, tree plotting and interaction with solvers

-```solvers.py``` provides an interface class that solvers need to interact with the cube, and three solver implementations

## Running Visualization
To start visualization, run:
```default
python main.py
```
By default, both the cube visualization and tree visualization are on, and the depth used for cube shuffling and tree depth is set to 2. However, those parameters can be altered via the command line by using any combination of the following command line arguments:
```command
python main.py --tree_visuals_off --cube_visuals_off --depth INT
```
The cube will be initiated in a solved state. To test solvers, user must first press ```Shuffle Cube```, which will randomly shuffle the cube using ```depth``` random counter clockwise turns. Then, press desired solver and watch solving process on cube and state tree exploration. The solvers provided will explore the entire state tree and are guaranteed to find the solution as they will explore the state tree to the same depth as it has been shuffled.

The tree visualizes each node reachable from the starting node given the depth. Each node is named a string, given by the sequence of moves required to reach that node from the starting node. The possible moves are 'R','D','U','L','B','F', which is a clockwise turn of the respective faces, and 'r','d','u','l','b','f' which is a counter clockwise turn i.e node 'R' in the tree is reached by moving the right face clockwise once from the start position, and the node 'RF' is reached by moving the right face clockwise once, followed by moving the front face clockwise once.

The tree colors the current node as yellow, visited nodes as grey, and the solution node as green once it is found.

## Demos
The tree GIFs are large and may lag behind cube GIFs.
Depth First Search    |  Breadth First Search   |   Best First Search
:-------------------------:|:-------------------------:|:-------------------------:
![Alt Text](figs/tree_dfs.gif)  |  ![Alt Text](figs/tree_bfs.gif) |![Alt Text](figs/tree_bestfs.gif)
![Alt Text](figs/cube_dfs.gif)  |  ![Alt Text](figs/cube_bfs.gif) |![Alt Text](figs/cube_bestfs.gif)

For Best First Search, as each node is explored it is given a numeric value of percentage solved. To calculate percentage solved, for each face of the cube the total number of squares that are the same color as the center square (which can never change faces) are summed. This is done for all faces, and summed over the entire cube. This value is then divided by 54 (6x3x3) to give percentage solved. This numeric is used to rank the nodes to explore i.e. nodes that are closer to being completed are explored first. In some cases this can lead to very fast solves. In some cases (especially with larger depths), the optimal move requires a non-optimal move according to this metric and it can be as slow or slower than Depth First Search or Breadth First Search.

## Adding Solvers
There are many additional solvers that could be used and demonstrated here. For example, simulated annealing, genetic algorithms, or more robust solvers such as Monte Carlo tree search using a learned heuristic function.

Should you want to develop a new solver, the script ```solvers.py``` offers a typed informal interface any solver should extend. It should be relatively easy to design your own solver and plug it into this interface. To add it to the GUI simply add the following after line 389 in ```main.py```

```rubiks_cube.ModifiedInteractiveCube.add_solver(solvers.YourSolverClass)```

and it will automatically be added to the GUI.
