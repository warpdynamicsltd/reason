def isomorphic_functions(f1, f2, domain):
    value_map = {}  # Maps values of f1 to values in f2
    mapped_vals = set()  # Keeps track of already mapped values in dict2

    for x in domain:
        val1 = f1(x)
        val2 = f2(x)

        if val1 not in value_map:
            # If we've already used val2 for another val1, it's not 1-to-1
            if val2 in mapped_vals:
                return False
            # Create new mapping
            value_map[val1] = val2
            mapped_vals.add(val2)
        else:
            # If an existing mapping doesn't match the current value, fail
            if value_map[val1] != val2:
                return False

    return True


def isomorphic_dicts(dict1, dict2):
    """
    Check if two dictionaries dict1 and dict2 are isomorphic.

    They are isomorphic if:
    1. They have the same set of keys.
    2. There is a one-to-one mapping between values in dict1 and values in dict2.

    Example:
        dict1 = {1: "a", 2: "b", 3: "a"}
        dict2 = {1: "x", 2: "y", 3: "x"}  # -> True (mapping: a -> x, b -> y)

        dict1 = {1: "a", 2: "b", 3: "b"}
        dict2 = {1: "x", 2: "y", 3: "z"}  # -> False (b maps to both y and z)
    """
    # 1. Check if both dictionaries have the same set of keys
    if set(dict1.keys()) != set(dict2.keys()):
        return False

    return isomorphic_functions(lambda x: dict1[x], lambda x: dict2[x], dict1.keys())
