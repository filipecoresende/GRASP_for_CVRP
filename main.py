import random
import time
from typing import List, Dict
from sys import argv

from utils import *
from construction import *
from local_search import local_search

instances_path = "vrp_instances/"

instances = [ "instance1.vrp" ,"instance2.vrp", "instance3.vrp",
             "instance4.vrp", "instance5.vrp", "instance6.vrp",
             "instance7.vrp", "instance8.vrp"]

inst = int(argv[1])
filename = instances_path + instances[inst]
construction = argv[2]
time_limit = 60 * 30
start_time = time.perf_counter()

cvrp_instance: CVRPInstance = read_instance(filename)

if construction == "0":
    constructed_solution = savings_constructive_heuristic(cvrp_instance)
elif construction == "1":
    constructed_solution = insertion_constructive_heuristic(cvrp_instance, lam=1)
else:
    constructed_solution = sweep_constructive_heuristic(cvrp_instance)

improved_solution, cost, time_best, total_time = local_search(constructed_solution, cvrp_instance, start_time, time_limit)

print(filename)
print(construction)

print("Initial solution:")
print(constructed_solution)
print("Improved solution")
print(improved_solution)

with open(f"results/instance_{inst+1}_{construction}.out", 'w') as file:
        # The .write() method writes the string to the file
        file.write(f"{inst+1};{construction};{total_time};{cost};{time_best}\n")