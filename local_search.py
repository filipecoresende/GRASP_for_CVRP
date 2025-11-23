from typing import List, Dict
from utils import CVRPInstance
from math import sqrt, ceil

def local_search(sol: List[List[int]], I: CVRPInstance):

    def evaluate_removal(prev, rem, next):
        return (
            - I.distance_matrix[prev][rem]
            - I.distance_matrix[rem][next]
            + I.distance_matrix[prev][next]
        )
    
    def evaluate_insertion(prev, ins, next):
        return (
            - I.distance_matrix[prev][next]
            + I.distance_matrix[prev][ins]
            + I.distance_matrix[ins][next]
        )
    
    def evaluate_2_opt(i, j, prev, next):
        return (
            - I.distance_matrix[prev][i]
            - I.distance_matrix[j][next]
            + I.distance_matrix[prev][j]
            + I.distance_matrix[i][next]
        )

    def reinsertion(r_1, r_2, sol, TL, capacity_usage):
        route_1 = sol[r_1]
        route_2 = sol[r_2]
        l_r1 = len(route_1)
        l_r2 = len(route_2)

        best_delta = float('inf')
        best_pos = -1
        best_destination = -1
        for r_pos in range(1, len(route_1)):
            if route_1[r_pos] in TL:
                continue
            for i_pos in range(1, len(route_2)):
                if route_2[i_pos] in TL:
                    continue
                prev_r1 = route_1[r_pos-1]
                next_r1 = route_1[(r_pos+1)%l_r1]
                prev_r2 = route_2[i_pos-1]
                next_r2 = route_2[i_pos%l_r2]
                delta_cost = (
                    evaluate_removal(prev_r1, route_1[r_pos], next_r1)
                    + evaluate_insertion(prev_r2, route_1[r_pos], next_r2)
                )

                if I.demands[route_1[r_pos]] <= I.capacity - capacity_usage[r_2] and delta_cost < best_delta:
                    best_delta = delta_cost
                    best_pos = r_pos
                    best_destination = i_pos

        # if best_delta < 0:
        #     print(f"{best_delta} by {best_pos} to {best_destination}")
        return best_delta, best_pos, best_destination

    def two_opt(r, sol, TL):
        route = sol[r]

        best_delta = float('inf')
        best_i = -1
        best_j = -1
        for i in range(1, len(route)-1):
            if route[i] in TL:
                continue
            for j in range(i+1, len(route)):
                if route[j] in TL or (i==1 and j==len(route)-1):
                    continue
                prev = i-1
                next = (j+1)%len(route)
                delta_cost = evaluate_2_opt(route[i], route[j], route[prev], route[next])

                if delta_cost < best_delta:
                    best_delta = delta_cost
                    best_i = i
                    best_j = j

        # if True or best_delta < 0:
        #     print(f"{best_delta} {best_i} and {best_j}")
        return best_delta, best_i, best_j

    def intra_swap(r, sol, TL):
        route = sol[r]

        best_delta = float('inf')
        best_i = -1
        best_j = -1
        for i in range(1, len(route)-1):
            if route[i] in TL:
                continue
            for j in range(i+2, len(route)):
                if route[j] in TL:
                    continue
                prev_i = route[i-1]
                next_i = route[(i+1)%len(route)]
                prev_j = route[j-1]
                next_j = route[(j+1)%len(route)]
                delta_cost = (
                    evaluate_removal(prev_i, route[i], next_i)
                    + evaluate_insertion(prev_j, route[i], next_j)
                    + evaluate_removal(prev_j, route[j], next_j)
                    + evaluate_insertion(prev_i, route[j], next_i)
                )

                if delta_cost < best_delta:
                    best_delta = delta_cost
                    best_i = i
                    best_j = j

        # if True or best_delta < 0:
        #     print(f"{r}:{best_delta} {best_i} and {best_j}")
        return best_delta, best_i, best_j

    def inter_swap(r_1, r_2, sol, TL, capacity_usage):
        route_1 = sol[r_1]
        route_2 = sol[r_2]
        l_r1 = len(route_1)
        l_r2 = len(route_2)

        best_delta = float('inf')
        best_pos = -1
        best_destination = -1
        for i in range(1, len(route_1)):
            if route_1[i] in TL:
                continue
            for j in range(1, len(route_2)):
                if route_2[j] in TL:
                    continue
                prev_r1 = route_1[i-1]
                next_r1 = route_1[(i+1)%l_r1]
                prev_r2 = route_2[j-1]
                next_r2 = route_2[(j+1)%l_r2]
                delta_cost = (
                    evaluate_removal(prev_r1, route_1[i], next_r1)
                    + evaluate_insertion(prev_r2, route_1[i], next_r2)
                    + evaluate_removal(prev_r2, route_2[j], next_r2)
                    + evaluate_insertion(prev_r1, route_2[j], next_r1)
                )

                if (
                    I.demands[route_1[i]] <= I.capacity - capacity_usage[r_2] + I.demands[route_2[j]]
                    and I.demands[route_2[j]] <= I.capacity - capacity_usage[r_1] + I.demands[route_1[i]]
                    and delta_cost < best_delta
                ):
                    best_delta = delta_cost
                    best_pos = i
                    best_destination = j

        # if best_delta < 0:
        #     print(f"{best_delta} by {best_pos} to {best_destination}")
        return best_delta, best_pos, best_destination

    def break_route(r, sol, TL):
        route = sol[r]

        best_delta = float('inf')
        best_i = -1
        best_j = -1
        for i in range(2, len(route)):
            prev = route[i-1]
            next = route[i]
            delta_cost = evaluate_insertion(prev, 0, next)

            if delta_cost < best_delta:
                best_delta = delta_cost
                best_i = i
                best_j = i

        # if True or best_delta < 0:
        #     print(f"{best_delta} {best_i} and {best_j}")
        return best_delta, best_i, best_j

    TL = [-1 for i in range(ceil(sqrt(I.nnodes)) * 2)]

    capacity_usage = [0 for i in range(len(sol))]
    for i, route in enumerate(sol):
        for node in route[1:]:
            capacity_usage[i] += I.demands[node]

    stop = False
    iter = 0

    while not stop:
        sel_r1 = -1
        sel_r2 = -1
        sel_delta = float('inf')
        sel_i = -1
        sel_j = -1
        sel_type = None

        # Evaluate reinsertions
        for r1 in range(len(sol)):
            for r2 in range(len(sol)):
                if  r1 != r2:
                    delta, pos, dest =  reinsertion(r1, r2, sol, TL, capacity_usage)
                    if delta < sel_delta:
                        sel_r1 = r1
                        sel_r2 = r2
                        sel_delta = delta
                        sel_i = pos
                        sel_j = dest
                        sel_type = 'reinsert'

        # # Evaluate 2-opt
        for r in range(len(sol)):
            delta, i, j = two_opt(r, sol, TL)
            if delta < sel_delta:
                sel_r1 = r
                sel_r2 = -1
                sel_delta = delta
                sel_i = i
                sel_j = j
                sel_type = '2-opt'

        # # Evaluate intra-swap
        for r in range(len(sol)):
            delta, i, j = intra_swap(r, sol, TL)
            if delta < sel_delta:
                sel_r1 = r
                sel_r2 = -1
                sel_delta = delta
                sel_i = i
                sel_j = j
                sel_type = 'intra-swap'

        # # Evaluate inter-swap
        for i in range(len(sol)):
            for j in range(i+1, len(sol)):
                delta, pos, dest =  inter_swap(i, j, sol, TL, capacity_usage)
                if delta < sel_delta:
                    sel_r1 = i
                    sel_r2 = j
                    sel_delta = delta
                    sel_i = pos
                    sel_j = dest
                    sel_type = 'inter-swap'

        # # Evaluate break-route
        for r in range(len(sol)):
            delta, i, j = break_route(r, sol, TL)
            if delta < sel_delta:
                sel_r1 = r
                sel_r2 = -1
                sel_delta = delta
                sel_i = i
                sel_j = j
                sel_type = 'break-route'

        # Temp
        if sel_delta >= 0:
            print("Local optimum")
            break

        if sel_type == 'reinsert':
            v1 = sol[sel_r1][sel_i]

            del sol[sel_r1][sel_i]
            capacity_usage[sel_r1] -= I.demands[v1]

            sol[sel_r2].insert(sel_j, v1)
            capacity_usage[sel_r2] += I.demands[v1]

            if len(sol[sel_r1] == 1):
                del sol[sel_r1]
                del capacity_usage[sel_r1]

            print(f"{sel_r1}: {v1} {sel_i}, {sel_r2}: {v1} {sel_j}, delta: {sel_delta}")

            TL = TL[2:] + [v1, -1]

        elif sel_type == '2-opt':
            v1 = sol[sel_r1][sel_i]
            v2 = sol[sel_r1][sel_j]

            sol[sel_r1] = sol[sel_r1][:sel_i] + sol[sel_r1][sel_i:sel_j+1][::-1] + sol[sel_r1][sel_j+1:]

            print(f"{sel_r1}: {sel_i} {sel_j}, delta: {sel_delta}")

            TL = TL[2:] + [v1, v2]

        elif sel_type == 'intra-swap':
            v1 = sol[sel_r1][sel_i]
            v2 = sol[sel_r1][sel_j]

            sol[sel_r1][sel_i] = v2
            sol[sel_r1][sel_j] = v1

            print(f"{sel_r1}: {sel_i} {sel_j}, delta: {sel_delta}")

            TL = TL[2:] + [v1, v2]

        elif sel_type == 'inter-swap':
            v1 = sol[sel_r1][sel_i]
            v2 = sol[sel_r2][sel_j]

            sol[sel_r1][sel_i] = v2
            sol[sel_r2][sel_j] = v1

            capacity_usage[sel_r1] += I.demands[v2] - I.demands[v1] 
            capacity_usage[sel_r2] += I.demands[v1] - I.demands[v2]

            print(f"{sel_r1}: {sel_i}, {sel_r2}:{sel_j}, delta: {sel_delta}")

            TL = TL[2:] + [v1, v2]

        elif sel_type == 'break-route':
            sol.append([0] + sol[sel_r1][sel_i:])
            sol[sel_r1] = sol[sel_r1][:sel_i]

            new_capacity = 0
            for node in sol[-1][1:]:
                new_capacity += I.demands[node]
            
            capacity_usage.append(new_capacity)
            capacity_usage[sel_r1] -= new_capacity

            print(f"{sel_r1}: {sel_i}, delta: {sel_delta}")

            TL = TL[2:] + [sol[-1][1], sol[-1][-1]]
            
        else:
            print("No valid moviments found")
            break

        print(TL)

        iter += 1
        stop = True if iter > 100 else stop

    # print(capacity_usage)
    # print(I.capacity)

    return sol