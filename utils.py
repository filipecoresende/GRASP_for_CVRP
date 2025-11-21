from typing import List, Tuple, Optional
from math import sqrt, floor

# Type alias for clarity
Coordinates = List[Tuple[float, float]]

class CVRPInstance:
    def __init__(self, coords: Coordinates, demands: List[int], capacity: int):
        self.nnodes: int = len(coords)
        self.coords: Coordinates = coords
        self.demands: List[int] = demands
        self.capacity: int = capacity
        self.depot: int = 0  # Assuming the first node is the depot
        self.nodes: List[int] = list(range(self.nnodes))
        self.distance_matrix: List[List[float]] = self._compute_distance_matrix()

    def _compute_distance_matrix(self) -> List[List[int]]:
        """
        Compute Euclidean distance matrix between nodes.
        """
        n = self.nnodes
        dist = [[0.0] * n for _ in range(n)]
        for i in range(n):
            xi, yi = self.coords[i]
            for j in range(n):
                xj, yj = self.coords[j]
                dist[i][j] = floor(sqrt((xi - xj)**2 + (yi - yj)**2))
        return dist

    def __str__(self) -> str:
        return (f"CVRPInstance(num_nodes={self.nnodes}, "
                f"capacity={self.capacity}, depot={self.depot})")

def read_instance(filename: str) -> CVRPInstance:
    """
    Reads a CVRP instance file and returns coordinates, demands, and vehicle capacity.
    Assumes a single depot at the first node.
    """
    coords: Coordinates = []
    demands: List[int] = []
    capacity: Optional[int] = None

    with open(filename) as f:
        mode: Optional[str] = None
        for line in f:
            line = line.strip()
            if line.startswith('CAPACITY'):
                capacity = int(line.split(':')[1])
            elif line.startswith('NODE_COORD_SECTION'):
                mode = 'coords'
                continue
            elif line.startswith('DEMAND_SECTION'):
                mode = 'demands'
                continue
            elif line.startswith('DEPOT_SECTION'):
                break  # We assume first node is depot
            if mode == 'coords':
                parts = line.split()
                x, y = float(parts[1]), float(parts[2])
                coords.append((x, y))
            elif mode == 'demands':
                parts = line.split()
                d = int(parts[1])
                demands.append(d)

    if capacity is None:
        raise ValueError("Instance file missing CAPACITY.")
    
    return CVRPInstance(coords, demands, capacity)

# Checks whether the tour respects vehicle capacity
def check_route_feasibility(route: List[int], cvrp_instance: CVRPInstance) -> bool:
    
    total_demand = 0
    for customer in route[1:]:
        total_demand += cvrp_instance.demands[customer]
        
    if total_demand > cvrp_instance.capacity:
        return False
    
    return True
    
