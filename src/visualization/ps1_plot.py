import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx


def plot_correlation_heatmap(corr_matrix):
    """
    Visualizes the cell-to-cell congestion correlation matrix.
    """
    plt.figure(figsize=(12, 10))
    sns.heatmap(
        corr_matrix,
        cmap="coolwarm",
        center=0,
        square=True,
        cbar_kws={"label": "Congestion Correlation"}
    )
    plt.title("Cell-to-Cell Congestion Correlation Heatmap (PS1 Evidence)")
    plt.tight_layout()
    plt.show()


def plot_topology_graph(G, link_mapping):
    """
    Visualizes inferred fronthaul topology as a graph.
    """
    pos = nx.spring_layout(G, seed=42)

    colors = ["red", "blue", "green", "orange"]
    node_colors = []

    for node in G.nodes:
        assigned = False
        for idx, cells in enumerate(link_mapping.values()):
            if node in cells:
                node_colors.append(colors[idx % len(colors)])
                assigned = True
                break
        if not assigned:
            node_colors.append("gray")

    plt.figure(figsize=(12, 10))
    nx.draw(
        G,
        pos,
        with_labels=True,
        node_color=node_colors,
        node_size=800,
        edge_color="gray",
        font_size=9
    )
    plt.title("Inferred Fronthaul Topology Graph (PS1 Output)")
    plt.show()
