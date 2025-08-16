
from typing import Callable, Any, Dict
from orkes.graph.unit import Node,Edge
from orkes.graph.schema import NodePoolItem
from orkes.graph.unit import _EndNode

class GraphRunner:
    def __init__(self, nodes_pool: Dict[str, NodePoolItem], graph_state: Dict):
        self.graph_state = graph_state
        self.nodes_pool = nodes_pool

    #TODO: Modifications are returned as a new copy, not in-place mutation.
    def run(self, invoke_state):
        for key, value in invoke_state.items():
            if key in self.graph_state:
                self.graph_state[key] = value
        start_pool = self.nodes_pool['START']
        start_edges = start_pool.edge
        input_state = self.graph_state.copy()
        state = self.tranverse_graph(start_edges, input_state)

    #TODO: fix state only
    def tranverse_graph(self, current_edge: Edge, input_state: Dict):
        current_node = self.nodes_pool[current_edge.from_node].node
        result = current_node.execute(input_state)
        next_node = current_edge.to_node
        if not isinstance(next_node, _EndNode):
            result = self.tranverse_graph( next_node, result)
        else:
            return result



# Handle Brancing and merging state -> because state update only happen after node process done, no shared mutable object
# FAN IN FAN OUT STRATEGY, EVERY BRANCHING NODE NEED TO BE RETURNED
# In your example:
#     A
#     |
#     B
#    / \
#   C   D
#        \
#         E
# If E needs data from both C and D, you have two main options:

# Make E a "merge node" that accepts inputs from both C and D — i.e., edges C -> E and D -> E.

# E will receive two incoming states, merge them internally, then execute.

# Insert an explicit merge node (e.g., M):

#     C   D
#      \ /
#       M
#       |
#       E
# The merge node M merges C and D’s outputs.

# Then E runs with the combined state.