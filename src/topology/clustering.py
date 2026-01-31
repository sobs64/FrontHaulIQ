import networkx as nx
from networkx.algorithms.community import greedy_modularity_communities

def detect_link_communities(G: nx.Graph, max_links=3):
    """
    Detects link-sharing communities from a correlation graph.

    Args:
        G: NetworkX graph (nodes=cells, edges=correlation)
        max_links: expected number of fronthaul links

    Returns:
        List of sets of cell IDs
    """
    if G.number_of_edges() == 0:
        print("⚠️ Warning: Graph has no edges. Cannot detect communities.")
        return []

    communities = list(greedy_modularity_communities(G))

    # Sort communities by size (largest first)
    communities = sorted(communities, key=len, reverse=True)

    return communities[:max_links]
