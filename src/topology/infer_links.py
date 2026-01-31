def infer_link_mapping(communities):
    """
    Assigns Link1, Link2, Link3 labels.

    Returns:
        dict[link_name] -> list of cells
    """
    link_mapping = {}

    for idx, community in enumerate(communities, start=1):
        link_mapping[f"Link{idx}"] = sorted(list(community))

    return link_mapping
