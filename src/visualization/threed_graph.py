
import plotly.graph_objects as go
import networkx as nx

def generate_3d_topology(link_mapping):
    """
    Generates a 3D aesthetic topology figure using Plotly.
    
    Args:
        link_mapping (dict): Dictionary mapping Link IDs to Cells.
        
    Returns:
        plotly.graph_objects.Figure
    """
    # 1. Build Graph
    G = nx.Graph()
    for link, cells in link_mapping.items():
        G.add_node(link, type="link", group=link)
        for cell in cells:
            G.add_node(cell, type="cell", group=link)
            G.add_edge(link, cell)

    # 2. Compute 3D Layout
    # k=0.5 pushes nodes apart, dim=3 for 3D
    pos = nx.spring_layout(G, dim=3, seed=42, k=0.5)

    # 3. Extract Coordinates & Styles
    edge_x = []
    edge_y = []
    edge_z = []
    
    node_x = []
    node_y = []
    node_z = []
    node_color = []
    node_size = []
    node_text = []
    
    # Aesthetic Colors (Neon Palette)
    # Link1: Neon Blue, Link2: Neon Green, Link3: Neon Orange/Pink
    group_colors = {
        "Link1": "#00f3ff", # Cyan
        "Link2": "#39ff14", # Neon Green
        "Link3": "#ff00ff", # Magenta
        "Link4": "#ffff00", # Yellow
        "Link5": "#ff7700"  # Orange
    }
    
    # Edges
    for edge in G.edges():
        x0, y0, z0 = pos[edge[0]]
        x1, y1, z1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
        edge_z.extend([z0, z1, None])

    # Nodes
    for node in G.nodes():
        x, y, z = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_z.append(z)
        
        node_type = G.nodes[node]["type"]
        group = G.nodes[node]["group"]
        
        base_color = group_colors.get(group, "#ffffff")
        
        if node_type == "link":
            node_color.append(base_color)
            node_size.append(15) # Larger for Hubs
            node_text.append(f"<b>{node}</b> (Main Hub)")
        else:
            node_color.append(base_color)
            node_size.append(6) # Smaller for Cells
            node_text.append(f"{node}")

    # 4. Create Traces
    
    # Glow Effect: We draw nodes twice, once with blur? Plotly doesn't do blur easily.
    # Instead, we use marker line width to create a "halo"
    
    edge_trace = go.Scatter3d(
        x=edge_x, y=edge_y, z=edge_z,
        mode='lines',
        line=dict(color='#888888', width=2), # Semi-transparent grey
        opacity=0.3,
        hoverinfo='none'
    )

    node_trace = go.Scatter3d(
        x=node_x, y=node_y, z=node_z,
        mode='markers',
        marker=dict(
            size=node_size,
            color=node_color,
            line=dict(color='#ffffff', width=2), # White halo
            opacity=0.9
        ),
        text=node_text,
        hoverinfo='text'
    )

    # 5. Figure Layout
    fig = go.Figure(data=[edge_trace, node_trace])
    
    fig.update_layout(
        title="✨ Immersive 3D Topology",
        title_font_color="#ffffff",
        paper_bgcolor="#0e1117", # Streamlit dark theme bg match approx
        plot_bgcolor="#0e1117",
        showlegend=False,
        scene=dict(
            xaxis=dict(showbackground=False, visible=False),
            yaxis=dict(showbackground=False, visible=False),
            zaxis=dict(showbackground=False, visible=False),
            bgcolor="#0e1117"
        ),
        margin=dict(l=0, r=0, b=0, t=40),
        height=700
    )
    
    return fig
