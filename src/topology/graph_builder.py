import networkx as nx
import numpy as np
import pandas as pd

def build_correlation_graph(corr_matrix: pd.DataFrame, threshold=0.25):
    """
    Builds a weighted graph from correlation matrix.

    Nodes = cells
    Edges = correlation strength (above threshold)
    """
    G = nx.Graph()

    # Add nodes
    for cell in corr_matrix.columns:
        G.add_node(cell)

    # Add edges
    for i in corr_matrix.index:
        for j in corr_matrix.columns:
            if i >= j:
                continue

            weight = corr_matrix.loc[i, j]
            if abs(weight) >= threshold:
                G.add_edge(i, j, weight=weight)

    return G
