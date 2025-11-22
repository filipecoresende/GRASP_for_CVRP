from typing import List, Dict
import math

from utils import *


def savings_constructive_heuristic(cvrp_instance: CVRPInstance) -> List[List[int]]:
    
    # Maps each node to its current route
    # Each route is represented as (route load, [0, ..., last customer])
    node_to_route: List[Tuple[int, List[int]]] = [(cvrp_instance.demands[i],[0,i]) for i in range(1, cvrp_instance.nnodes)] # List of routes
    
    # Stores pairs of nodes whose connection (when possible) is worth it
    savings: Dict[Tuple[int, int], float] = {} 
    
    nnodes = cvrp_instance.nnodes
    for i in range(1, nnodes - 1):
        for j in range(i + 1, nnodes):
            c_0i = cvrp_instance.distance_matrix[0][i]
            c_0j = cvrp_instance.distance_matrix[0][j]
            c_ij = cvrp_instance.distance_matrix[i][j]
            saving = c_0i + c_0j - c_ij
        
            if (saving >= 0): #in case saving == 0, you might at least reduce number of vehicles by 1
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
        if route1[0] + route2[0] <= cvrp_instance.capacity: 
            new_route = _merge_routes(route1, route2, v1_idx, v2_idx)
            if (len(route1[1]) > 2):
                not_endpoints.add(v1_idx)
            if (len(route2[1]) > 2):
                not_endpoints.add(v2_idx)
            for node in new_route[1][1:]:
                node_to_route[node - 1] = new_route
           
            
    # Constructs final solution:
    seen = set()
    final_solution = []

    for route in node_to_route:
        if id(route) not in seen:   # check identity, not value
            final_solution.append(route[1])
            seen.add(id(route))
          
    return final_solution
            
    
def _merge_routes(route1: Tuple[int, List[int]], route2: Tuple[int, List[int]],
                 v1_idx: int, v2_idx: int) -> List[int]:
    
    load = route1[0] + route2[0]
    new_route = (load,[0])
    
    for route, v_idx in zip([route1, route2],[v1_idx, v2_idx]):
        if route[1][1] == v_idx + 1:
            new_route[1].extend(route[1][1:])
        else:
            new_route[1].extend(reversed(route[1]))
            del new_route[1][-1]
            
    return new_route
        
    
def insertion_constructive_heuristic(instance: CVRPInstance, lam: float = 1.0):
    """
    Implement the Mole & Jameson (1976) sequential insertion constructive heuristic.
    No local search step is included.

    Parameters
    ----------
    instance : CVRPInstance
        CVRP problem instance.
    lam : float
        λ (lambda) parameter controlling how strongly the heuristic penalizes
        breaking an existing edge (i, j) in the current route.
        
        - If lam = 1, the insertion cost equals the true extra distance.
        - If lam > 1, breaking the edge (i, j) is penalized more heavily,
          making insertions more conservative (routes stay more stable/compact).
        - If lam < 1, breaking (i, j) is penalized less, encouraging more flexible
          or aggressive insertions early in route construction.

        The insertion criterion is:
            α(i, k, j) = dist[i][k] + dist[k][j] - lam * dist[i][j]
        and the customer/position with the lowest α is selected.
    """

    n = instance.nnodes
    depot = instance.depot
    capacity = instance.capacity
    demands = instance.demands
    dist = instance.distance_matrix

    unrouted = set(range(1, n))  # all customer nodes (excluding depot)
    routes = []

    # Heuristic loop: build routes one by one
    while unrouted:

        # ---- Select initial seed customer (choose farthest or simply first) ----
        # Here: pick the customer with largest demand first (better stability)
        seed = max(unrouted, key=lambda x: demands[x])
        
        # Initialize new route
        route = [depot, seed]
        load = demands[seed]
        unrouted.remove(seed)

        # ---- Sequential insertion phase ----
        while True:
            best_customer = None
            best_pos = None
            best_alpha = float('inf')

            # Try all unrouted customers
            for u in unrouted:
                if load + demands[u] > capacity:
                    continue  # cannot add this customer

                # Try all insertion positions (i, j) in the route
                for pos in range(len(route) - 1):
                    i = route[pos]
                    j = route[pos + 1]

                    alpha = dist[i][u] + dist[u][j] - lam * dist[i][j]

                    if alpha < best_alpha:
                        best_alpha = alpha
                        best_customer = u
                        best_pos = pos + 1

            if best_customer is None:
                break  # Cannot insert more customers in this route

            # Insert best customer
            route.insert(best_pos, best_customer)
            load += demands[best_customer]
            unrouted.remove(best_customer)

        # Add constructed route
        routes.append(route)

    return routes
        

def sweep_constructive_heuristic(instance: CVRPInstance) -> List[List[int]]:
    """
    Implements the Sweep Algorithm for the CVRP.
    
    1. Calculates polar angles for all customers relative to the depot.
    2. Sorts customers by angle.
    3. Greedily builds routes respecting capacity constraints.
    """
    
    # 1. Get Depot Coordinates
    depot_x, depot_y = instance.coords[instance.depot]
    
    # 2. Calculate Polar Angles for all customers
    # Store as list of tuples: (customer_index, angle)
    customer_angles: List[Tuple[int, float]] = []
    
    # Iterate over nodes, skipping the depot (index 0)
    for i in instance.nodes:
        if i == instance.depot:
            continue
            
        x, y = instance.coords[i]
        
        # math.atan2 returns value between -pi and pi
        angle = math.atan2(y - depot_y, x - depot_x)
        customer_angles.append((i, angle))
    
    # 3. Sort customers by angle (sweeping motion)
    customer_angles.sort(key=lambda x: x[1])
    
    # 4. Construct Routes (Clustering)
    routes: List[List[int]] = []
    current_route: List[int] = [instance.depot]
    current_load = 0
    
    for customer_idx, _ in customer_angles:
        demand = instance.demands[customer_idx]
        
        # Check if adding this customer exceeds capacity
        if current_load + demand <= instance.capacity:
            # Add to current route
            current_route.append(customer_idx)
            current_load += demand
        else:
            # 1. Close the current route
            routes.append(current_route)
            
            # 2. Start a new route with the depot and the current customer
            current_route = [instance.depot, customer_idx]
            current_load = demand
            
    # Append the last route if it has customers
    if len(current_route) > 1:
        routes.append(current_route)
        
    return routes

