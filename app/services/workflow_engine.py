def has_reject_cycle(stages) -> bool:
    """
    Detects cycles in the reject-routing graph using DFS-style pointer chasing.
    Each stage has at most ONE outgoing reject edge (on_reject_target_sequence),
    so we simply follow the chain from each stage and watch for repeats.
    """
    # Build a lookup: sequence_order -> its reject target sequence
    reject_map = {s.sequence_order: s.on_reject_target_sequence for s in stages}

    for start_seq in reject_map:
        visited = set()
        current = start_seq
        while current is not None:
            if current in visited:
                return True  # revisited a node in this chain -> cycle
            visited.add(current)
            current = reject_map.get(current)

    return False