from typing import List, Dict

from utils import *


def savings_constructive_heuristic(cvrp_instance: CVRPInstance) -> List[List[int]]:
    
    # Maps each node to its current route
    # Each route is represented as [0, ..., last customer]
    node_to_route: List[List[int]] = [[0,i] for i in range(1,cvrp_instance.nnodes)] # List of routes
    
    # Stores pairs of nodes whose connection (when possible) is worth it
    savings: Dict[Tuple[int, int], float] = {} 
    
    nnodes = cvrp_instance.nnodes
    for i in range(1, nnodes - 1):
        for j in range(i + 1, nnodes):
            c_0i = cvrp_instance.distance_matrix[0][i]
            c_0j = cvrp_instance.distance_matrix[0][j]
            c_ij = cvrp_instance.distance_matrix[i][j]
            saving = c_0i + c_0j - c_ij
        
            if (saving >= 0): #in case saving == 0, you might at least reduce num_vehicles by 1
                savings[(i, j)] = saving
    
    # Sort in decreasing order with respect to saving
    sorted_savings = sorted(savings.items(), key=lambda item: item[1], reverse=True)
    
    not_endpoints = set() # node is here => not an endpoint of its route anymore
    
    for candidate in sorted_savings:
        v1_idx = candidate[0][0] - 1
        v2_idx = candidate[0][1] - 1
        if (v1_idx in not_endpoints) or (v2_idx in not_endpoints):
            continue
        route1 = node_to_route[v1_idx]; route2 = node_to_route[v2_idx]
        if route1 is route2:
            continue
        new_route = merge_routes(route1, route2, v1_idx, v2_idx)
        if check_route_feasibility(new_route, cvrp_instance):
            if (len(route1) > 2):
                not_endpoints.add(v1_idx)
            if (len(route2) > 2):
                not_endpoints.add(v2_idx)
            for node in new_route[1:]:
                node_to_route[node - 1] = new_route
           
            
    # Constructs final solution:
    seen = set()
    final_solution = []

    for route in node_to_route:
        if id(route) not in seen:   # check identity, not value
            final_solution.append(route)
            seen.add(id(route))
          
    return final_solution
            
    
def merge_routes(route1: List[int], route2: List[int],
                 v1_idx: int, v2_idx: int) -> List[int]:
    
    new_route = [0]
    
    for route, v_idx in zip([route1, route2],[v1_idx, v2_idx]):
        if route[1] == v_idx:
            new_route.extend(route[1:])
        else:
            new_route.extend(reversed(route))
            del new_route[-1]
            
    return new_route
        
    
        
        
    