import random
import math
import copy


# Erlang-B formula
def erlang_b(c, A):
    if c == 0:
        return 1.0
    B = 1.0
    for k in range(1, c + 1):
        B = (A * B) / (A * B + k)
    return B

# Compute overall blocking probability
def overall_blocking(assign,cells,call_attempts, call_duration,pi):
    total = 0
    per_cell = []
    for idx, cell in enumerate(cells):
        c_i = len(set(assign[cell]))  # Use distinct channels only
        A_i = call_attempts[idx] * call_duration
        B_i = erlang_b(c_i, A_i)
        per_cell.append(B_i)
        total += pi[idx] * B_i
    return total, per_cell

# Check neighbor constraints
def is_valid(assign,cells,neighbors):
    for cell in cells:
        for n in neighbors[cell]:
            if set(assign[cell]) & set(assign[n]):
                return False
    return True

def smart_initial_assignment(cells, neighbors, channels_total, call_attempts, min_channels_per_cell):
    assign = {c: [] for c in cells}
    channels = list(range(1, channels_total + 1))

    # Step 1: Give each cell its minimum channels first
    for c in cells:
        possible_channels = [ch for ch in channels if all(ch not in assign[n] for n in neighbors[c])]
        min_possible = min(min_channels_per_cell[c], len(possible_channels))
        for ch in possible_channels[:min_possible]:
            assign[c].append(ch)
            channels.remove(ch)  # mark as used for this pass

    # Step 2: Assign remaining channels greedily for reuse
    for ch in channels:
        for c in cells:
            if all(ch not in assign[n] for n in neighbors[c]):
                assign[c].append(ch)
                break
    return assign


def perturb(assign, cells, neighbors, channels_total, min_channels_per_cell):
    new_assign = copy.deepcopy(assign)
    action = random.random()
    
    if action < 0.4:
        # Add channel
        ch = random.randint(1, channels_total)
        possible_cells = [c for c in cells if all(ch not in new_assign[n] for n in neighbors[c]) and ch not in new_assign[c]]
        if possible_cells:
            c = random.choice(possible_cells)
            new_assign[c].append(ch)
            
    elif action < 0.7:
        # Move channel from one cell to another
        ch = random.randint(1, channels_total)
        current_cells = [c for c in cells if ch in new_assign[c]]
        if current_cells:
            from_cell = random.choice(current_cells)
            possible_cells = [c for c in cells if c != from_cell and all(ch not in new_assign[n] for n in neighbors[c]) and ch not in new_assign[c]]
            min_possible = min(min_channels_per_cell[from_cell], len(new_assign[from_cell]))
            if possible_cells and len(new_assign[from_cell]) > min_possible:
                to_cell = random.choice(possible_cells)
                new_assign[from_cell].remove(ch)
                new_assign[to_cell].append(ch)
                
    else:
        # Swap channels between two cells
        ch1, ch2 = random.sample(range(1, channels_total+1), 2)
        cells_ch1 = [c for c in cells if ch1 in new_assign[c]]
        cells_ch2 = [c for c in cells if ch2 in new_assign[c]]
        if cells_ch1 and cells_ch2:
            c1 = random.choice(cells_ch1)
            c2 = random.choice(cells_ch2)
            min_possible_c1 = min(min_channels_per_cell[c1], len(new_assign[c1]))
            min_possible_c2 = min(min_channels_per_cell[c2], len(new_assign[c2]))
            if (c1 != c2 and all(ch1 not in new_assign[n] for n in neighbors[c2])
                and all(ch2 not in new_assign[n] for n in neighbors[c1])
                and ch2 not in new_assign[c1] and ch1 not in new_assign[c2]
                and len(new_assign[c1]) >min_possible_c1
                and len(new_assign[c2]) > min_possible_c2):
                new_assign[c1].remove(ch1)
                new_assign[c2].remove(ch2)
                new_assign[c1].append(ch2)
                new_assign[c2].append(ch1)

    # Deduplicate each cell
    for c in cells:
        new_assign[c] = list(set(new_assign[c]))
    return new_assign


def simulated_annealing(cells,neighbors,channels_total,call_attempts,call_dur,p_i,min_channels,iterations=50000, T_start=1.0, T_end=0.001, alpha=0.995):
    current = smart_initial_assignment(cells,neighbors,channels_total,call_attempts, min_channels)
    current_block, _ = overall_blocking(current,cells,call_attempts, call_dur,p_i)
    best = copy.deepcopy(current) 
    best_block = current_block 
    T = T_start 
    for it in range(iterations):
        new_assign = perturb(current,cells,neighbors,channels_total,min_channels)
        if not is_valid(new_assign,cells,neighbors): 
            continue 
        new_block, _ = overall_blocking(new_assign,cells,call_attempts, call_dur,p_i) 
        delta = new_block - current_block 
        if delta < 0 or random.random() < math.exp(-delta / T): 
            current = new_assign 
            current_block = new_block 
            if new_block < best_block: 
                best = copy.deepcopy(new_assign)
                best_block = new_block 
                T = max(T * alpha, T_end) 
    return best, best_block


def minimum_blocking(minimum_blocking,min_channels_per_cell,p_i,cells,neighbors,call_attempts,call_duration):
    no_channels= 10
    overall_blocking_val = 1.0
    trials = 5
    runs=100000
    while overall_blocking_val >minimum_blocking:
        min_channels_per_cell = {
            1: max(1, int(p_i[0]*no_channels)),
            2: max(1, int(p_i[1]*no_channels)),
            3: max(1, int(p_i[2]*no_channels)),
            4: max(1, int(p_i[3]*no_channels)),
            5: max(1, int(p_i[4]*no_channels)),
        }
        
        for _ in range(trials):
            best_distribution, per_cell_distribution = simulated_annealing(cells,neighbors,no_channels,call_attempts,call_duration,p_i,min_channels_per_cell,runs)
            overall_blocking_val, indiv_block_vals = overall_blocking(best_distribution,cells,call_attempts, call_duration,p_i)
            print(f"Trying with {no_channels} channels: Blocking = {overall_blocking_val}, min channels per cell: {min_channels_per_cell}")
            if overall_blocking_val <= minimum_blocking:
                break
         # Increase channels if target not reached
        if overall_blocking_val > minimum_blocking:
            diff_ratio = abs(overall_blocking_val - minimum_blocking)
            add_channels = int(max(40* diff_ratio,1))
            print(f"Not reached minimum blocking. Increasing channels by {add_channels} to {no_channels + add_channels}.")
            no_channels += add_channels

    return no_channels, overall_blocking_val, indiv_block_vals,best_distribution




def main():
    # Parameters
    call_attempts = [2, 5, 8, 9, 11]  # per cell
    call_duration = 1.5
    cells = [1, 2, 3, 4, 5]
    channels_total = 50
    no_iterations = 100000
    # Neighbor dictionary
    neighbors = {
        1: [2, 3],
        2: [1, 3],
        3: [1, 2, 4, 5],
        4: [3, 5],
        5: [3, 4]
    }

   

    # Call probability per cell
    total_calls = sum(call_attempts)
    p_i = [x / total_calls for x in call_attempts]
     # Minimal channels per cell based on load
    min_channels_per_cell = {
        1: int(p_i[0]*channels_total),   # low traffic
        2:  int(p_i[1]*channels_total),
        3:  int(p_i[2]*channels_total),
        4: int(p_i[3]*channels_total),
        5:  int(p_i[4]*channels_total),# highest traffic
    }
    print(f"Minimum channels per cell based on load: {min_channels_per_cell}")
    best_assignment, best_blocking = simulated_annealing(cells,neighbors,channels_total,call_attempts,call_duration,p_i,min_channels_per_cell,no_iterations)

    # Print per-cell blocking
    overall, per_cell_block = overall_blocking(best_assignment,cells,call_attempts, call_duration,p_i)
    print("Best Channel Assignment and Blocking per Cell:")
    for idx, c in enumerate(cells):
        print(f"Cell {c}: Channels {best_assignment[c]}, Blocking Probability: {per_cell_block[idx]:.6f}")
    print(f"\nOverall Blocking Probability: {overall:.6f}")
    
    min_blocks = 0.01
    no_channels, overall_blocking_val,indiv_block, per_cell_distribution = minimum_blocking(min_blocks,min_channels_per_cell,p_i,cells,neighbors,call_attempts,call_duration)
    print(f"\nMinimum number of channels to achieve blocking < {min_blocks}: {no_channels}")
    print(f"Overall Blocking Probability with {no_channels} channels: {overall_blocking_val:.6f}")
    for idx, c in enumerate(cells):
        print(f"Cell {c}: Channels {per_cell_distribution[c]}, Blocking Probability: {indiv_block[idx]:.6f}")
    print(f"\nOverall Blocking Probability: {overall_blocking_val:.6f}")
    
if __name__ == "__main__":
    main()