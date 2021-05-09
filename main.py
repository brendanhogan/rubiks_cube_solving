
import random
import argparse
import functools
import numpy as np
from PIL import Image
from pylab import pause
from graphviz import Digraph
from matplotlib import widgets
import matplotlib.pyplot as plt

import solvers
from MagicCube import cube_interactive



class ModifiedCube(cube_interactive.Cube):
    """
    In order to use added functionailty in ModifiedInteractiveCube, need to
    override class call in Cube, to instead call ModifiedInteractiveCube.

    """
    def draw_interactive(self):
        fig = plt.figure(figsize=(5, 5))
        self.ModifiedInteractiveCube = ModifiedInteractiveCube(self,args.cube_visuals_off,args.tree_visuals_off,args.depth)
        fig.add_axes(self.ModifiedInteractiveCube)
        return fig


class ModifiedInteractiveCube(cube_interactive.InteractiveCube):
    """
    In order to introduce additional solving functionailty and visualization,
    need to override some class methods

    """

    def __init__(self, cube, visualize_cube=True, visualize_tree=True, depth=2):
        super().__init__(cube)

        # Initialize matrices that will track cube position
        self._setup_cube_state()

        # Track if should visualize cube while solving, and state tree
        self.visualize_cube = visualize_cube
        self.visualize_tree = visualize_tree

        # Set depth to search and to shuffle
        self.depth = depth

        # Initialize variable tracking moves made by solvers
        self.solver_moves = []

        # Initialize variable of all possible moves of cube
        self.possible_moves = ['R','D','U','L','B','F']

        # Track if cube has been shuffled or not
        self.shuffled = False

        # Track number of solvers added, maximum 3
        self.number_of_solvers = 0
        self.solvers = []

        # Track buttons/solvers
        self._ax_solve = []
        self._btn_solve = []

        # Remove text
        self.figure.texts[0].set_visible(False)


    def _key_press(self,event):
        """Disallow manual turning."""
        pass

    def add_solver(self,new_solver_class):
        """
        If over max solvers (3) print error, otherwise will instantiate solver,
        append to solver list and add button.
        """
        if self.number_of_solvers > 2:
            print("Max number of solvers")
            return
        # Instantiate
        new_solver = new_solver_class(self.depth, self.possible_moves.copy())
        name = new_solver.get_name()
        # Append
        self.solvers.append(new_solver)
        # Make button
        left = 0.55 - self.number_of_solvers*.2
        self._ax_solve.append(self.figure.add_axes([left, 0.05, 0.2, 0.075]))
        self._btn_solve.append(widgets.Button(self._ax_solve[-1], name))
        self._btn_solve[-1].on_clicked(functools.partial(self._button_clicked, s_id=self.number_of_solvers))
        # Increment
        self.number_of_solvers += 1

    def _button_clicked(self, mouse_click, s_id=0, *args):
        self._solve_cube(s_id)


    def _shuffle_cube(self,*args):
        """
        Method that shuffles cube for given number of turns (backwards turns
        only). Also clears solver_moves to track new solver.

        If cube is already shuffled prints error and returns without shuffling
        again.
        """
        if self.shuffled:
            print("Cube already shuffled")
            return
        shuffle_moves = random.choices(self.possible_moves,k=self.depth)
        for move in shuffle_moves:
            # Only make backwards moves
            self.rotate_face(move.lower())
        self.shuffled = True

        # Clear tracking variables
        self.solver_moves = []
        self.color_tree_dict = {}


    def _initialize_widgets(self):
        """
        Override buttons
        """

        self._ax_reset = self.figure.add_axes([0.75, 0.05, 0.2, 0.075])
        self._btn_reset = widgets.Button(self._ax_reset, 'Shuffle Cube')
        self._btn_reset.on_clicked(self._shuffle_cube)


    def _setup_cube_state(self):
        """
        Cube's position internally will be stored as 6 3x3 matrics. Where each
        color is assigned an integer 0-5.
        """
        self.cube_state = np.ones((6,3,3))
        for i in range(6):
            self.cube_state[i,:,:] *= i


    def rotate_face(self, turn, layer=0, steps=10):
        turns = 1 if turn.isupper() else -1
        # If selected visualize cube turning
        if self.visualize_cube:
            for i in range(steps):
                self.cube.rotate_face(turn.upper(), turns / steps, layer=layer)
                self._draw_cube()
                pause(0.01)
        # Update internal cube state
        self.update_cube_state(turn.upper(), np.sign(turns))

    def update_cube_state(self,face,dir):
        if face == "F":
            if dir == 1:
                temp = self.cube_state[4,0,:].copy()
                self.cube_state[4,0,:] = self.cube_state[3,0,:]
                self.cube_state[3,0,:] = self.cube_state[2,0,:]
                self.cube_state[2,0,:] = self.cube_state[1,0,:]
                self.cube_state[1,0,:] = temp
                self.cube_state[0] = np.rot90(self.cube_state[0],k=3)
            else:
                temp = self.cube_state[4,0,:].copy()
                self.cube_state[4,0,:] = self.cube_state[1,0,:]
                self.cube_state[1,0,:] = self.cube_state[2,0,:]
                self.cube_state[2,0,:] = self.cube_state[3,0,:]
                self.cube_state[3,0,:] = temp
                self.cube_state[0] = np.rot90(self.cube_state[0],k=1)

        if face == "L":
            if dir == 1:
                temp = self.cube_state[0,:,0].copy()
                self.cube_state[0,:,0] = np.flip(self.cube_state[2,:,2])
                self.cube_state[2,:,2] = self.cube_state[5,:,2]
                self.cube_state[5,:,2] = np.flip(self.cube_state[4,:,0])
                self.cube_state[4,:,0] = temp
                self.cube_state[1] = np.rot90(self.cube_state[1],k=3)
            else:
                temp = self.cube_state[0,:,0].copy()
                self.cube_state[0,:,0] = self.cube_state[4,:,0]
                self.cube_state[4,:,0] = np.flip(self.cube_state[5,:,2])
                self.cube_state[5,:,2] = self.cube_state[2,:,2]
                self.cube_state[2,:,2] = np.flip(temp)
                self.cube_state[1] = np.rot90(self.cube_state[1],k=1)
        if face == "U":
            if dir == 1:
                temp = self.cube_state[0,0,:].copy()
                self.cube_state[0,0,:] = self.cube_state[3,:,2]
                self.cube_state[3,:,2] = self.cube_state[5,0,:]
                self.cube_state[5,0,:] = np.flip(self.cube_state[1,:,0])
                self.cube_state[1,:,0] = np.flip(temp)
                self.cube_state[2] = np.rot90(self.cube_state[2],k=3)
            else:
                temp = self.cube_state[0,0,:].copy()
                self.cube_state[0,0,:] = np.flip(self.cube_state[1,:,0])
                self.cube_state[1,:,0] = np.flip(self.cube_state[5,0,:])
                self.cube_state[5,0,:] = self.cube_state[3,:,2]
                self.cube_state[3,:,2] = temp
                self.cube_state[2] = np.rot90(self.cube_state[2],k=1)

        if face == "R":
            if dir == 1:
                temp = self.cube_state[0,:,2].copy()
                self.cube_state[0,:,2] = self.cube_state[4,:,2]
                self.cube_state[4,:,2] = np.flip(self.cube_state[5,:,0])
                self.cube_state[5,:,0] = self.cube_state[2,:,0]
                self.cube_state[2,:,0] = np.flip(temp)
                self.cube_state[3] = np.rot90(self.cube_state[3],k=3)

            else:
                temp = self.cube_state[0,:,2].copy()
                self.cube_state[0,:,2] = np.flip(self.cube_state[2,:,0])
                self.cube_state[2,:,0] = self.cube_state[5,:,0]
                self.cube_state[5,:,0] = np.flip(self.cube_state[4,:,2])
                self.cube_state[4,:,2] = temp
                self.cube_state[3] = np.rot90(self.cube_state[3],k=1)

        if face == "D":
            if dir == 1:
                temp = self.cube_state[0,2,:].copy()
                self.cube_state[0,2,:] = np.flip(self.cube_state[1,:,2])
                self.cube_state[1,:,2] = np.flip(self.cube_state[5,2,:])
                self.cube_state[5,2,:] = self.cube_state[3,:,0]
                self.cube_state[3,:,0] = temp
                self.cube_state[4] = np.rot90(self.cube_state[4],k=3)

            else:
                temp = self.cube_state[0,2,:].copy()
                self.cube_state[0,2,:] = self.cube_state[3,:,0]
                self.cube_state[3,:,0] = self.cube_state[5,2,:]
                self.cube_state[5,2,:] = np.flip(self.cube_state[1,:,2])
                self.cube_state[1,:,2] = np.flip(temp)
                self.cube_state[4] = np.rot90(self.cube_state[4],k=1)

        if face == "B":
            if dir == 1:
                temp = self.cube_state[2,2,:].copy()
                self.cube_state[2,2,:] = self.cube_state[3,2,:]
                self.cube_state[3,2,:] = self.cube_state[4,2,:]
                self.cube_state[4,2,:] = self.cube_state[1,2,:]
                self.cube_state[1,2,:] = temp
                self.cube_state[5] = np.rot90(self.cube_state[5],k=3)
            else:
                temp = self.cube_state[2,2,:].copy()
                self.cube_state[2,2,:] = self.cube_state[1,2,:]
                self.cube_state[1,2,:] = self.cube_state[4,2,:]
                self.cube_state[4,2,:] = self.cube_state[3,2,:]
                self.cube_state[3,2,:] = temp
                self.cube_state[5] = np.rot90(self.cube_state[5],k=1)

    def _is_solved(self):
        """
        Returns boolean if cube is solved or not.

        """
        solved = True
        for i in range(6):
            solved = solved and np.all(self.cube_state[i,:,:] == self.cube_state[i,0,0])
        return solved

    def _solve_cube(self,solver_num):
        """
        Run chosen solver until cube is solved or solver terminates.

        """
        # Setup second plotting window for tree if visualizing
        if self.visualize_tree:
            self.tree_fig = plt.figure(2)
            self.tree_ax = self.tree_fig.add_subplot(111)

        # Select solver
        solver = self.solvers[solver_num]

        # Tell solver starting a fresh solve
        solver.clear()

        # Iterate until solved or solver terminates
        solver_finished = False
        while not self._is_solved() and not solver_finished:
            # Get from solver, and if terminal state
            action, solver_finished = solver.get_action(self.cube_state)
            # If solver is out of moves continue and break loop
            if action is None:
                continue
            # Take action on cube
            self.rotate_face(action)
            # Update move list, and states
            self._update_moves(action)
            # Update tree
            self._update_tree()

        # If solved update shuffled
        if self._is_solved():
            self.shuffled = False
            print("Solved")


    def _make_tree(self,state_tree,node_val,depth):
        if depth == 0:
            return
        # Starting node is special case
        if node_val == '':
            if self.color_tree_dict["current"] == node_val:
                state_tree.node(node_val, "Start",color="yellow",style='filled')
            else:
                state_tree.node(node_val,"Start",color="grey",style='filled')
        for move in self.possible_moves:
            new_node = node_val+move
            # If is current node the color yellow
            if self.color_tree_dict["current"] == new_node:
                state_tree.node(new_node, new_node,color="yellow",style='filled')
            elif new_node in self.color_tree_dict:
                state_tree.node(new_node, new_node,color=self.color_tree_dict[new_node],style='filled')
            else:
                state_tree.node(new_node, new_node)
            state_tree.edge(node_val, new_node)
            self._make_tree(state_tree,new_node,depth-1)
        return


    def _update_tree(self):
        """
        If specified, visualize state tree, with colors indicating the following:
        Grey -> visited
        Yellow -> Current state
        Green -> Solved State
        """
        if not self.visualize_tree:
            return
        # Set current state to indicate which should be yellow, and set to be grey after
        self.color_tree_dict["current"] = ''.join(self.solver_moves)
        self.color_tree_dict[''.join(self.solver_moves)] = "grey"
        # If solved set to green and make current None so plots as green
        if self._is_solved():
            self.color_tree_dict[''.join(self.solver_moves)] = "green"
            self.color_tree_dict["current"] = None
        # Now make tree
        state_tree = Digraph()
        self._make_tree(state_tree,"",self.depth)
        # Now plot tree
        state_tree.render(filename="temp",cleanup=True,format='png')
        self.tree_ax.clear()
        im = plt.imread("temp.png")
        img = self.tree_ax.imshow(im)
        self.tree_ax.axis('off')
        plt.draw()


    def _update_moves(self,action):
        """
        Adds move to list tracking moves made by solver.

        If action and last move are same character, and opposite case then just
        pop, because they cancel.

        """
        if len(self.solver_moves)>0 and (action.upper() == self.solver_moves[-1].upper() and not action == self.solver_moves[-1]):
            self.solver_moves.pop()
        else:
            self.solver_moves.append(action)




if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process parameters for Rubiks Cube')
    parser.add_argument('--depth', '-d', type=int, default=2, help='depth for shuffling and solvers')
    parser.add_argument('--tree_visuals_off', '-tv', action='store_false')
    parser.add_argument('--cube_visuals_off', '-cv', action='store_false')
    args = parser.parse_args()

    # Generate cube object and iteraction
    rubiks_cube = ModifiedCube(3)
    rubiks_cube.draw_interactive()

    # Add solvers, can add custom solvers, see solvers.py
    rubiks_cube.ModifiedInteractiveCube.add_solver(solvers.DepthFirstSearch)
    rubiks_cube.ModifiedInteractiveCube.add_solver(solvers.BreadthFirstSearch)
    rubiks_cube.ModifiedInteractiveCube.add_solver(solvers.BestFirstSearch)

    # Render everything
    plt.show()






 #
