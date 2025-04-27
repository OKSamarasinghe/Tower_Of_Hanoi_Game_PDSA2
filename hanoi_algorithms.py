"""
Tower of Hanoi Algorithm Implementations
This module provides different algorithms for solving the Tower of Hanoi puzzle
with both 3-peg and 4-peg variants.
"""

def recursive_hanoi(n, source, target, auxiliary):
    """
    Recursive solution for the 3-peg Tower of Hanoi.
    
    Args:
        n: Number of disks
        source: Source peg name
        target: Target peg name
        auxiliary: Auxiliary peg name
        
    Returns:
        List of (source, target) move tuples
    """
    if n == 0:
        return []
    if n == 1:
        return [(source, target)]
        
    # Move n-1 disks from source to auxiliary
    moves = recursive_hanoi(n-1, source, auxiliary, target)
    
    # Move the largest disk from source to target
    moves.append((source, target))
    
    # Move n-1 disks from auxiliary to target
    moves.extend(recursive_hanoi(n-1, auxiliary, target, source))
    
    return moves

def iterative_hanoi(n, source, target, auxiliary):
    """
    Iterative solution for the 3-peg Tower of Hanoi.
    
    Args:
        n: Number of disks
        source: Source peg name
        target: Target peg name
        auxiliary: Auxiliary peg name
        
    Returns:
        List of (source, target) move tuples
    """
    moves = []
    
    # Initialize pegs
    pegs = {
        source: list(reversed(range(1, n + 1))),  # Source peg with all disks
        auxiliary: [],  # Empty auxiliary peg
        target: []      # Empty target peg
    }
    
    # For even number of disks, swap the auxiliary and target pegs
    if n % 2 == 0:
        target, auxiliary = auxiliary, target
        
    # Total moves needed: 2^n - 1
    total_moves = 2 ** n - 1
    
    for i in range(1, total_moves + 1):
        if i % 3 == 1:
            # Move between source and target
            move_between(pegs, source, target, moves)
        elif i % 3 == 2:
            # Move between source and auxiliary
            move_between(pegs, source, auxiliary, moves)
        elif i % 3 == 0:
            # Move between auxiliary and target
            move_between(pegs, auxiliary, target, moves)
            
    return moves

def move_between(pegs, a, b, moves):
    """
    Helper function to move a disk between two pegs based on the rules.
    
    Args:
        pegs: Dictionary representing the current state of pegs
        a: First peg name
        b: Second peg name
        moves: List to append the move to
    """
    if not pegs[a] and not pegs[b]:
        # Both pegs are empty, do nothing
        return
    elif not pegs[a]:
        # First peg is empty, move from second to first
        pegs[a].append(pegs[b].pop())
        moves.append((b, a))
    elif not pegs[b]:
        # Second peg is empty, move from first to second
        pegs[b].append(pegs[a].pop())
        moves.append((a, b))
    elif pegs[a][-1] < pegs[b][-1]:
        # Top disk of first peg is smaller, move from first to second
        pegs[b].append(pegs[a].pop())
        moves.append((a, b))
    else:
        # Top disk of second peg is smaller, move from second to first
        pegs[a].append(pegs[b].pop())
        moves.append((b, a))

def frame_stewart(n, pegs, source, target):
    """
    Frame-Stewart algorithm for the 4-peg Tower of Hanoi.
    
    This algorithm is more efficient than the standard algorithm for 4+ pegs.
    The Frame-Stewart algorithm divides the problem into two parts:
    1. Move k disks from source to intermediate peg
    2. Move n-k disks from source to target using standard algorithm
    3. Move k disks from intermediate to target
    
    Args:
        n: Number of disks
        pegs: List of peg names
        source: Source peg name
        target: Target peg name
        
    Returns:
        List of (source, target) move tuples
    """
    if n == 0:
        return []
    if n == 1:
        return [(source, target)]
        
    # Find intermediate pegs (not source or target)
    intermediate_pegs = [p for p in pegs if p != source and p != target]
    
    # For 4 pegs, the optimal k is approximately sqrt(n)
    if len(pegs) == 4:
        # Simple heuristic for optimal k value
        import math
        k = int(math.sqrt(n))
    else:
        # For more pegs, we'll use a more complex formula
        # but this is sufficient for our purposes
        k = n // 2
    
    moves = []
    
    # Step 1: Move k disks from source to intermediate peg
    moves.extend(frame_stewart(k, pegs, source, intermediate_pegs[0]))
    
    # Step 2: Move n-k disks from source to target using remaining pegs
    remaining_pegs = [source, target] + intermediate_pegs[1:]
    moves.extend(recursive_hanoi(n - k, source, target, remaining_pegs[2]))
    
    # Step 3: Move k disks from intermediate to target
    moves.extend(frame_stewart(k, pegs, intermediate_pegs[0], target))
    
    return moves

def calculate_min_moves(n, pegs):
    """
    Calculate the minimum number of moves required.
    
    Args:
        n: Number of disks
        pegs: Number of pegs
        
    Returns:
        Minimum number of moves
    """
    if pegs == 3:
        # Standard formula for 3 pegs: 2^n - 1
        return 2 ** n - 1
    elif pegs == 4:
        # Approximate for 4 pegs
        if n <= 1:
            return n
        
        # Use dynamic programming to find optimal solution
        # This is a simple implementation of Frame-Stewart algorithm
        min_moves = float('inf')
        for k in range(1, n):
            moves = (2 * calculate_min_moves(k, pegs) + 
                    calculate_min_moves(n - k, 3))
            min_moves = min(min_moves, moves)
        return min_moves
    else:
        raise ValueError("Only 3 or 4 pegs are supported")