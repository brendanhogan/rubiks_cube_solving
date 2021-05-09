
import numpy as np
from typing import List, Tuple



class InterfaceSolver():

    """
    Informal interface for solving class needed to interact with rubiks
    environment.

    """

    def __init__(self, depth:int, possible_moves: List[str]) -> None:
        """
        Will be passed depth, i.e. number of backwards turns cube has been
        randomly shuffled from solved.

        Additionally will be passed the list of acceptable moves that should
        be returned by the get_action method. Can be upper or lower case
        characters but must be in possible_moves. Each character corresponds to
        a face of the cube, upper case is a clockwise turn, lower case is
        counter clockwise, will be passed as all upper case.
        """
        pass

    def get_name(self) -> str:
        """
        Each solver will have an associated button in the GUI, this text will
        be what is displayed on the button.
        """

    def clear(self) -> None:
        """
        Will be called before every fresh solve. Can use to reset any necessary
        parameters.
        """
        pass

    def get_action(self, cube_state:np.array) -> Tuple[str,bool]:
        """
        Will be passed cube state as a 6x3x3 np.array, where the first index
        represents the 6 sides of the cube, and the 2nd and 3rd index form a
        3x3 table representing each of the 9 faces on one side of the cube. Each
        entry has an integer value {0,5} representing a color. A solved cube is
        when for each side, each 3x3 matrix only contains one value. Can assume
        cube_state results from taking previous action on previous cube_state.

        Must return character from possible_moves passed in init, can be upper
        or lower case as described above.

        Also must return boolean value indicating if solver is terminating
        (True), or not (False). If terminating can either provide action and it
        will be executed and then terminate, or can pass action as None, and
        solving will be terminated without any action.

        """
        pass


def find_shortest_path(node_1,node_2):
    """
    Given two nodes indicated by a string of their move sequence from the start
    node (forward moves only), this method returns the shortest move sequence
    from node_1 to node_2.
    """
    # Change to lists
    node_1 = list(node_1)
    node_1_common = node_1.copy()
    node_2 = list(node_2)
    node_2_common = node_2.copy()
    # Get length of smaller
    small_length = min(len(node_1),len(node_2))
    # get to smallest common parent node
    for i in range(small_length):
        if (node_1[i] == node_2[i]):
            # then pop because they are the same
            node_1_common.pop(0)
            node_2_common.pop(0)
        else:
            # as soon as this isn't true cant get any closer parent node
            break
    # Now generate path by reversing path to node_1, and follow path to node_2
    shortest_path = [x.lower() for x in node_1_common[::-1]]
    shortest_path.extend(node_2_common)
    return shortest_path



class DepthFirstSearch(InterfaceSolver):

    """
    Implements a depth first search algorithm bounded by depth provided.

    """

    def __init__(self, depth, possible_moves):
        self.depth = depth
        self.possible_moves = possible_moves

    def get_name(self):
        return "DFS"

    def depth_first_search(self,current_move,depth):
        # If past max depth just retun
        if depth < 0:
            return
        # Otherwise append move to list (or if empty/starting do nothing)
        if not len(current_move) == 0:
            self.moves_to_make.append(current_move)
        # Now go through each possible move/node from here recursively
        for m in self.possible_moves:
            self.depth_first_search(m,depth-1)
        # Now before return, undo current move
        if not len(current_move) == 0:
            self.moves_to_make.append(current_move.lower())
        return

    def clear(self):
        """
        Because depth bounded and possible moves do not change, can pre-compute
        all actions, and then will terminate via main if solved, or here if out
        of pre-computed moves.
        """
        # Make list of all moves using recursive depth first search
        self.moves_to_make = []
        self.depth_first_search("",self.depth)
        # Reverse string so that popping is constant time
        self.moves_to_make.reverse()

    def get_action(self, cube_state):
        """
        If only one move left provide last action and terminate, otherwise,
        pop
        Get action based off current index, increment index, and return
        """
        terminating = False
        if len(self.moves_to_make) == 1:
            terminating = True
        return self.moves_to_make.pop(), terminating


class BreadthFirstSearch(InterfaceSolver):

    """
    Implements a breadth first search algorithm bounded by depth provided.

    """

    def __init__(self, depth, possible_moves):
        self.depth = depth
        self.possible_moves = possible_moves

    def get_name(self):
        return "BFS"

    def clear(self):
        """
        Because depth bounded and possible moves do not change, can pre-compute
        all actions, and then will terminate via main if solved, or here if out
        of pre-computed moves.
        """
        # Simulating going through and popping from list below, but just pop and
        # append to main list which will be used in action.
        save_moves_to_make = []
        track_moves_to_make = []
        track_moves_to_make.extend(self.possible_moves)
        save_moves_to_make.extend(self.possible_moves)
        while len(track_moves_to_make) > 0:
            # Get next move
            next_move = track_moves_to_make.pop(0)
            # Now go through neighbors of this next_move/node
            for m in self.possible_moves:
                to_append = next_move+m
                if len(to_append) > self.depth:
                    continue
                else:
                    track_moves_to_make.append(to_append)
                    save_moves_to_make.append(to_append)
        # Now make completed move list using shortest path between each
        self.moves_to_make = []
        for i in range(len(save_moves_to_make)):
            if i ==0:
                self.moves_to_make.append(save_moves_to_make[0])
            else:
                self.moves_to_make.extend(find_shortest_path(save_moves_to_make[i-1],save_moves_to_make[i]))
        # Reverse string so that popping is constant time
        self.moves_to_make.reverse()


    def get_action(self, cube_state):
        """
        If only one move left provide last action and terminate, otherwise,
        pop
        Get action based off current index, increment index, and return
        """
        terminating = False
        if len(self.moves_to_make) == 1:
            terminating = True
        return self.moves_to_make.pop(), terminating




class BestFirstSearch(InterfaceSolver):

    """
    Implements a best first search algorithm bounded by depth provided.

    Here the metric is used is percentage complete.
    For each side the number of squares with the same color as the center is
    computed. This metric is summed for each side anid is divide by the total
    number of cube faces.

    """

    def __init__(self, depth, possible_moves):
        self.depth = depth
        self.possible_moves = possible_moves

    def get_name(self):
        return "BestFS"

    def clear(self):
        self.cube_state_move = []
        self.cube_state_values = []
        self.actions = []
        self.possible_moves_for_node = []
        self.last_action = ""
        self.move_queue = []
        self.previous_node = ""

    def get_value(self,cube_state):
        total_equal = 0
        total = cube_state.size
        for i in range(6):
            center_val = cube_state[i,1,1]
            total_equal += np.sum(cube_state[i,:,:]==center_val)
        return float(total_equal)/total

    def get_action_nodes(self, cube_state):
        """
        Method to actually select next nodes given known values.
        """
        # 1. Get value of current cube_state, and append state and value, and nodes_moved_to
        self.cube_state_values.append(self.get_value(cube_state))
        self.cube_state_move.append(self.last_action)
        self.possible_moves_for_node.append(self.possible_moves.copy())
        if len(self.actions) == 0:
            self.actions.append("")
        # 2. Now find best current state
        ranked_idx = np.argsort(np.array(self.cube_state_values))[::-1]
        next_move = None
        for idx in ranked_idx:
            # If no more possible moves, just continue, if have move make it and break
            if len(self.possible_moves_for_node[idx]) == 0 or len(self.cube_state_move[idx])==self.depth:
                continue
            else:
                next_move = self.cube_state_move[idx] + self.possible_moves_for_node[idx].pop()
                break
        # 3. If next_move is still none, terminate, no more moves to make
        if next_move is None:
            return None
        # 4. Otherwise, save action and return
        self.last_action = next_move
        return next_move

    def get_action(self,cube_state):
        """
        Need wrapper method for node selection to process transitions between
        nodes.
        """
        terminating = False
        # 1. If move queue empty, calculate next node using method, find path and append
        if len(self.move_queue) == 0:
            next_node = self.get_action_nodes(cube_state)
            if next_node is None:
                self.move_queue.append(None)
                terminating = True
            else:
                node_path = find_shortest_path(self.previous_node,next_node)
                self.move_queue.extend(node_path)
            self.previous_node = next_node

        # 2. Set previous node, pop and take action
        return self.move_queue.pop(0), terminating








#
