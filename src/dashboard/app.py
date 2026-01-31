
import sys
from pathlib import Path
import networkx as nx

# Add src/ to Python path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_PATH = PROJECT_ROOT / "src"

sys.path.insert(0, str(SRC_PATH))



import streamlit as st

from ingestion.load_throughput import load_throughput_data
from ingestion.load_packet_stats import load_packet_stats
from alignment.time_shift import align_packet_loss
from topology.graph_builder import build_correlation_graph
from topology.clustering import detect_link_communities
from topology.infer_links import infer_link_mapping
from topology.congestion_events import extract_windowed_congestion_events
from topology.correlation import build_congestion_matrix, compute_correlation_matrix
from preprocessing.symbol_to_slot import convert_to_slot_level

from dashboard.ps1_views import (
    show_correlation_heatmap,
    show_topology_graph,
    show_link_table,
    show_confidence_scores
)

# New Simulation Imports
from simulation.congestion_state import build_congestion_state
from simulation.animate import render_simulation_ui
from visualization.threed_graph import generate_3d_topology


st.set_page_config(
    page_title="FronthaulIQ – PS1 Topology Intelligence",
    layout="wide"
)

st.title("📡 FronthaulIQ – Topology Intelligence (PS1)")
st.markdown(
    """
    **Automatically inferred fronthaul topology using congestion correlation
    and graph-based community detection.**
    """
)

# -------------------------
# Run PS1 pipeline (cached)
# -------------------------
@st.cache_data
def run_ps1():
    throughput = load_throughput_data("data/raw/throughput")
    packets = load_packet_stats("data/raw/packet_stats")

    cells = sorted(set(throughput) & set(packets))

    aligned = {}
    throughput_slot = {}
    
    for c in cells:
        aligned[c], _ = align_packet_loss(throughput[c], packets[c])
        # Convert throughput to slot level for animation consistency
        throughput_slot[c] = convert_to_slot_level(throughput[c])

    events = {
        c: extract_windowed_congestion_events(aligned[c], loss_threshold=1, window=5)
        for c in cells
    }

    event_matrix = build_congestion_matrix(events)
    corr = compute_correlation_matrix(event_matrix)

    G_corr = build_correlation_graph(corr, threshold=0.25)
    communities = detect_link_communities(G_corr, max_links=3)
    links = infer_link_mapping(communities)
    
    # Pre-build congestion state
    congestion_state = build_congestion_state(aligned)

    return corr, links, aligned, throughput_slot, congestion_state


corr_matrix, link_mapping, aligned_packets, throughput_data, congestion_state = run_ps1()

# -------------------------
# Dashboard Layout
# -------------------------

# Tabs for organize views
tab1, tab2, tab3, tab4 = st.tabs(["Topology & Analysis", "Simulation & Animation", "3D Immersive View", "Raw Data"])

with tab1:
    show_correlation_heatmap(corr_matrix)
    
    st.divider()
    
    show_topology_graph(link_mapping)
    
    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        show_link_table(link_mapping)
    with col2:
        show_confidence_scores(link_mapping)

with tab2:
    # Build G and pos explicitly for the simulation to ensure consistency
    # We reconstruct the Hub-Spoke graph here
    G_sim = nx.Graph()
    for link, cells in link_mapping.items():
        G_sim.add_node(link, type="link")  # Hub
        for cell in cells:
            G_sim.add_node(cell, type="cell")  # Spoke
            G_sim.add_edge(link, cell)
            
    pos_sim = nx.spring_layout(G_sim, seed=42, k=0.3)
    
    render_simulation_ui(G_sim, pos_sim, congestion_state)

with tab3:
    st.subheader("🌌 3D Network Topology")
    st.markdown("Interactive 3D view. **Drag to rotate, Scroll to zoom.**")
    fig_3d = generate_3d_topology(link_mapping)
    st.plotly_chart(fig_3d, use_container_width=True)

with tab4:
    st.dataframe(corr_matrix)
