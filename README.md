# CVRP Heuristics & Local Search Solver

This project implements various algorithms to solve the **Capacitated Vehicle Routing Problem (CVRP)**. It includes constructive heuristics to generate initial solutions and a local search metaheuristic (Tabu Search) to optimize routing costs.

## 📋 Features

### Constructive Heuristics
Generates initial feasible solutions using one of three methods:
* **Clarke-Wright Savings:** Merges routes based on distance savings.
* **Sequential Insertion:** Inserts customers into routes based on a weighted cost function.
* **Sweep Algorithm:** Clusters customers based on polar angles relative to the depot.

### Local Search (Metaheuristic)
Improves the initial solution using a Tabu Search-based approach with the following operators:
* **Reinsertion:** Moves a customer from one route to another.
* **2-Opt:** Reverses a segment of a route to remove crossing edges.
* **Intra-Swap:** Swaps two customers within the same route.
* **Inter-Swap:** Swaps two customers between different routes.
* **Break Route:** Splits a route into two.

## 📂 Project Structure

```text
.
├── vrp_instances/           # Folder containing .vrp instance files
├── results/                 # Output folder for solution files
├── construction.py          # Implementation of constructive heuristics
├── local_search.py          # Implementation of Tabu Search/Local Search
├── utils.py                 # Data structures (CVRPInstance) and file readers
├── graphics.py              # Script to analyze and plot result CSVs
├── main.py                  # Main entry point to run the solver
└── README.md
```

## ⚙️ Installation

The core solver relies primarily on Python's standard library. However, the graphics analysis script requires `pandas`.

```bash
pip install pandas
```
Ensure you have a folder named `results` created in your root directory, as the script attempts to write output files there.

## 🚀 Usage

Run the `main.py` script from the terminal. It requires 4 command-line arguments:

```bash
python main.py <instance_index> <algorithm_id> <periodic_break> <tau_reduction>
```

### Arguments

1.  **`<instance_index>`** (int): Index of the file to load from the `instances` list (0-7).
2.  **`<algorithm_id>`** (str): The constructive heuristic to use:
    * `"0"`: Savings Algorithm
    * `"1"`: Insertion Algorithm
    * `"2"`: Sweep Algorithm (default for any other input)
3.  **`<periodic_break>`** (int): `1` to enable periodic breaks in the local search, `0` to disable.
4.  **`<tau_reduction>`** (int): `1` to enable dynamic Tabu list reduction, `0` to disable.

### 📝 Note on Instance Format
The project expects `.vrp` files containing `CAPACITY`, `NODE_COORD_SECTION`, and `DEMAND_SECTION` headers.

### Example

To run **Instance 0** using the Insertion Heuristic, with Periodic Breaks enabled and Tau Reduction disabled:

```bash
python main.py 0 1 1 0
```

## 📊 Output

* **Console:** Prints the initial solution, improved solution, and costs.
* **Files:** Saves a summary to `results/instance_<id>_<config>.out` containing execution time and final cost.
* **Analysis:** You can use `graphics.py` to process generated CSV results and calculate performance profiles (Tau values).


## References

* Cordeau, J.-F., Laporte, G., Savelsbergh, M. W. P., & Vigo, D. (2007). Chapter 6: Vehicle Routing. In Handbooks in Operations Research and Management Science (pp. 367–428). Elsevier. https://doi.org/10.1016/S0927-0507(06)14006-2

* Feo, T. A., & Resende, M. G. C. (1995). Greedy Randomized Adaptive Search Procedures. Journal of Global Optimization, 6, 109–133. https://doi.org/10.1007/BF01096763