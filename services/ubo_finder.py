def find_ubos(entity, visited=None, layer=0):
    """
    Recursively discover UBOs in a company structure.
    
    RETURNS:
        ubos: List[str] – list of ultimate beneficial owners (individuals)
        paths: List[List[str]] – ownership paths from top company → UBO
        max_layer: int – maximum depth of ownership chain
    """

    if visited is None:
        visited = set()

    ubos = []
    paths = []
    current_name = entity.get("company_name") or entity.get("name", "UNKNOWN_ENTITY")

    # Prevent infinite loops (circular ownership)
    if current_name in visited:
        return [], [], layer
    visited.add(current_name)

    shareholders = entity.get("shareholders", [])
    if not shareholders:
        # No shareholders – company is orphan, no UBO detectable
        return [], [], layer

    max_layer = layer

    for sh in shareholders:
        sh_name = sh.get("name", "UNKNOWN_SHAREHOLDER")
        sh_type = sh.get("type", "unknown")

        # CASE 1 — Individual → this is a UBO
        if sh_type == "individual":
            ubos.append(sh_name)
            paths.append([sh_name])
            max_layer = max(max_layer, layer + 1)

        # CASE 2 — Company → recurse deeper
        elif sh_type == "company":
            sub = sh.get("sub_entity")

            # If sub_entity missing → cannot recurse but still track
            if not sub:
                continue

            deeper_ubos, deeper_paths, deeper_layer = find_ubos(
                sub,
                visited,
                layer + 1
            )

            ubos.extend(deeper_ubos)

            # Add current company to paths
            for p in deeper_paths:
                paths.append([sh_name] + p)

            max_layer = max(max_layer, deeper_layer)

    # Cleanup duplicates
    ubos = list(set(ubos))

    return ubos, paths, max_layer
