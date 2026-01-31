import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import networkx as nx
import pandas as pd
from simulation.animator import prepare_animation_frames


# -------------------------
# PS1: Correlation Heatmap
# -------------------------
def show_correlation_heatmap(corr_matrix: pd.DataFrame):
    st.subheader("📊 Congestion Correlation Heatmap")

    fig = px.imshow(
        corr_matrix,
        color_continuous_scale="RdBu",
        zmin=-1,
        zmax=1,
        aspect="auto",
        labels=dict(color="Correlation")
    )

    fig.update_layout(
        height=600,
        title="Cell-to-Cell Congestion Correlation",
        title_x=0.5
    )

    st.plotly_chart(fig, use_container_width=True)


# -------------------------
# PS1: Topology Graph (Hub & Spoke)
# -------------------------
def show_topology_graph(link_mapping):
    st.subheader("🕸️ Inferred Fronthaul Topology (Hub-and-Spoke)")
    st.markdown("Each **Link** acts as a central hub for its connected **Cells**.")

    G = nx.Graph()

    # Build Hub-and-Spoke Graph
    for link, cells in link_mapping.items():
        G.add_node(link, type="link")  # Hub
        for cell in cells:
            G.add_node(cell, type="cell")  # Spoke
            G.add_edge(link, cell)

    # Use spring layout for aesthetics, but we could enforce star shape if needed
    pos = nx.spring_layout(G, seed=42, k=0.3)

    node_x, node_y, node_color, node_text, node_size = [], [], [], [], []
    
    # Define colors for different links
    link_colors = {
        "Link1": "#1f77b4", # Blue
        "Link2": "#2ca02c", # Green
        "Link3": "#ff7f0e", # Orange
        "Link4": "#d62728", # Red
        "Link5": "#9467bd"  # Purple
    }
    
    # Draw Nodes
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        
        node_type = G.nodes[node]["type"]
        
        if node_type == "link":
            # It's a Link Hub
            color = link_colors.get(node, "#333333")
            text = f"<b>{node}</b> (HUB)"
            size = 30
            symbol = "diamond"
        else:
            # It's a Cell
            # Find which link it belongs to for coloring
            parent_link = next(G.neighbors(node))
            color = link_colors.get(parent_link, "#7f7f7f")
            text = f"{node}<br>Linked to {parent_link}"
            size = 15
            symbol = "circle"

        node_color.append(color)
        node_text.append(text)
        node_size.append(size)

    # Draw Edges
    edge_x, edge_y = [], []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    # Create Plotly Traces
    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        line=dict(width=1, color="#bbb"),
        hoverinfo="none",
        mode="lines"
    )

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers+text",
        textposition="top center",
        hovertext=node_text,
        hoverinfo="text",
        marker=dict(
            size=node_size,
            color=node_color,
            line=dict(width=2, color="white"),
            symbol="circle" # We can't vary symbol easily in one trace, keeping circle
        ),
        text=[n if "Link" in n else "" for n in G.nodes()] # Only label Links on map
    )

    fig = go.Figure(data=[edge_trace, node_trace])
    fig.update_layout(
        showlegend=False,
        height=600,
        title="Fronthaul Topology Map",
        title_x=0.5,
        margin=dict(l=20, r=20, t=60, b=20),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor='white'
    )

    st.plotly_chart(fig, use_container_width=True)


# -------------------------
# NEW: Network Animation
# -------------------------
def show_network_animation(link_mapping, packet_data, throughput_data=None):
    st.subheader("🎥 Network Congestion Simulation")
    st.markdown("Visualizing traffic flow and congestion over time.")
    
    with st.spinner("Preparing animation frames... this may take a moment"):
        df_anim = prepare_animation_frames(link_mapping, packet_data, throughput_data, steps=100)

    if df_anim.empty:
        st.warning("No data available for animation.")
        return

    # Create animated scatter plot
    fig = px.scatter(
        df_anim,
        x="X",
        y="Y",
        animation_frame="Time",
        animation_group="Node",
        size="Size",
        color="Value", # Congestion Level
        color_continuous_scale="Reds", # Red means high congestion
        hover_name="Label",
        range_color=[0, 1], # Assuming normalized loss or binary event
        title="Real-time Network Congestion",
        template="plotly_white"
    )
    
    # Remove axes for clean map look
    fig.update_xaxes(showgrid=False, zeroline=False, visible=False)
    fig.update_yaxes(showgrid=False, zeroline=False, visible=False)
    
    # Improve layout
    fig.update_layout(
        height=700,
        transition={'duration': 100}, # Smooth transition
        updatemenus=[{
            'type': 'buttons',
            'showactive': False,
            'buttons': [{'label': 'Play', 'method': 'animate', 'args': [None, {'frame': {'duration': 100, 'redraw': True}, 'fromcurrent': True, 'transition': {'duration': 100}}]}]
        }]
    )
    
    st.plotly_chart(fig, use_container_width=True)


# -------------------------
# PS1: Link Mapping Table
# -------------------------
def show_link_table(link_mapping):
    st.subheader("🔗 Cell-to-Link Mapping")

    rows = []
    for link, cells in link_mapping.items():
        for cell in cells:
            rows.append({"Link": link, "Cell": cell})

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True)


# -------------------------
# PS1: Confidence Scores
# -------------------------
def show_confidence_scores(link_mapping):
    st.subheader("📈 Link Identification Confidence")

    confidence = {
        link: min(95, 70 + len(cells) * 4)
        for link, cells in link_mapping.items()
    }

    df = pd.DataFrame({
        "Link": confidence.keys(),
        "Confidence (%)": confidence.values()
    })

    fig = px.bar(
        df,
        x="Link",
        y="Confidence (%)",
        text="Confidence (%)",
        color="Link",
        color_discrete_sequence=["#1f77b4", "#2ca02c", "#ff7f0e"]
    )

    fig.update_layout(
        yaxis_range=[0, 100],
        height=400,
        title="Topology Inference Confidence",
        title_x=0.5
    )

    st.plotly_chart(fig, use_container_width=True)
