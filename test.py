import math

def compute_call_probabilities(call_attempts):
    total = sum(call_attempts)
    return [c / total for c in call_attempts]

def erlang_b(c, A):
    if c == 0:
        return 1.0
    B = 1.0
    for k in range(1, c+1):
        B = (A * B) / (A * B + k)
    return B

def check_neighbors(assign,neighbors):
    for cell, neighs in neighbors.items():
        for n in neighs:
            if set(assign[cell]) & set(assign[n]):
                return False
    return True

def compute_blocking(assign,call_attempts, call_duration,cells):
    per_cell_block = []
    total_prob = 0
    p_i = compute_call_probabilities(call_attempts)
    for idx, cell in enumerate(cells):
        distinct_channels = len(set(assign[cell]))  # remove duplicates if any
        traffic = call_attempts[idx] * call_duration
        B_i = erlang_b(distinct_channels, traffic)
        per_cell_block.append(B_i)
        total_prob += p_i[idx] * B_i
    return per_cell_block, total_prob

def main():
    call_attempts = [2, 5, 8, 9, 11]  # mean calls per minute per cell
    call_duration = 1.5               # minutes
    cells = [1, 2, 3, 4, 5]

    neighbors = {
        1: [2, 3],
        2: [1, 3,],
        3: [1, 2, 4,5],
        4: [3, 5],
        5: [3, 4]
    }
 #
    channel_assignment = {
    1: [1,2,3,4,5,6,7,8,9,10,11],
    2: [16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35],
    3: [36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,12,13,14,15],
    4: [1,2,3,4,5,6,7,8,9,10,11,51,52,53],
    5: [16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,54,55,56,57,58,59,60]
}

    # Check neighbor constraint
    if not check_neighbors(channel_assignment, neighbors):
        print("Warning: Neighbor cells share channels!")

    # Compute probabilities
    p_i = compute_call_probabilities(call_attempts)
    per_cell_block, overall_block = compute_blocking(channel_assignment, call_attempts, call_duration, cells)

    # Display results
    print("Cell Probabilities (p_i):")
    for i, prob in enumerate(p_i, start=1):
        print(f"Cell {i}: {prob:.4f}")

    print("\nPer-cell Blocking Probabilities:")
    for i, B in enumerate(per_cell_block, start=1):
        print(f"Cell {i}: {B:.4f}")

    print(f"\nOverall Blocking Probability: {overall_block:.4f}")
if __name__ == "__main__":
    main()