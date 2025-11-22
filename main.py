import random
import time
from typing import List, Dict

from utils import *
from construction import *

instances_path = "vrp_instances/"

instances = [ "instance1.vrp" ,"instance2.vrp", "instance3.vrp",
             "instance4.vrp", "instance5.vrp", "instance6.vrp",
             "instance7.vrp", "instance8.vrp"]

filename = instances_path + instances[0]

cvrp_instance: CVRPInstance = read_instance(filename)

constructed_solution1 = savings_constructive_heuristic(cvrp_instance)

constructed_solution2 = insertion_constructive_heuristic(cvrp_instance, lam=1)

constructed_solution3 = sweep_constructive_heuristic(cvrp_instance)

print(constructed_solution1)
print(constructed_solution2)
print(constructed_solution3)