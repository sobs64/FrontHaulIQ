# =========================
# FronthaulIQ Main Pipeline
# =========================

from ingestion.load_throughput import load_throughput_data
from ingestion.load_packet_stats import load_packet_stats
from alignment.time_shift import align_packet_loss
from topology.graph_builder import build_correlation_graph
from topology.clustering import detect_link_communities
from topology.infer_links import infer_link_mapping

from topology.congestion_events import extract_windowed_congestion_events
from topology.correlation import (
    build_congestion_matrix,
    compute_correlation_matrix
)

def main():
    print("🚀 Starting FronthaulIQ pipeline...\n")

    # -------------------------
    # Load raw data
    # -------------------------
    throughput_data = load_throughput_data("data/raw/throughput")
    packet_data = load_packet_stats("data/raw/packet_stats")

    print(f"Loaded throughput files: {len(throughput_data)}")
    print(f"Loaded packet stat files: {len(packet_data)}\n")

    # -------------------------
    # Debug: print keys
    # -------------------------
    throughput_cells = sorted(throughput_data.keys())
    packet_cells = sorted(packet_data.keys())

    print("📦 Throughput cell IDs:")
    print(throughput_cells, "\n")

    print("📦 Packet-stats cell IDs:")
    print(packet_cells, "\n")

    # -------------------------
    # Find common cells
    # -------------------------
    common_cells = sorted(set(throughput_cells) & set(packet_cells))

    if not common_cells:
        print("❌ ERROR: No matching cell IDs found.")
        return

    print(f"✅ Common cells found: {len(common_cells)}\n")

    # -------------------------
    # Time-shift alignment
    # -------------------------
    aligned_packet_data = {}

    print("⏱️  Detecting DU–RU time shift per cell...\n")

    for cell in common_cells:
        aligned_pkt, lag = align_packet_loss(
            throughput_data[cell],
            packet_data[cell]
        )

        aligned_packet_data[cell] = aligned_pkt
        print(f"   {cell}: lag = {lag} slots")

    print("\n✅ Time-shift alignment complete\n")

    # -------------------------
    # PS1: Congestion-event correlation
    # -------------------------
    print("📊 Building congestion-event correlation matrix...\n")

    

    event_data = {
        cell: extract_windowed_congestion_events(
            aligned_packet_data[cell],
            loss_threshold=1,
            window=5   # <-- key parameter
        )
        for cell in common_cells    
    }


    event_matrix = build_congestion_matrix(event_data)
    corr_matrix = compute_correlation_matrix(event_matrix)

    print("Event matrix shape:", event_matrix.shape)
    print("\nCorrelation matrix (rounded):")
    print(corr_matrix.round(2))

    print("\n🏁 PS1 (Topology Identification) correlation stage complete.")

        # -------------------------
    # PS1: Graph-based topology inference
    # -------------------------
    print("\n🕸️ Building correlation graph...")

    G = build_correlation_graph(
        corr_matrix,
        threshold=0.25   # noise-filtering threshold
    )

    print(f"Graph nodes: {G.number_of_nodes()}")
    print(f"Graph edges: {G.number_of_edges()}")

    communities = detect_link_communities(G, max_links=3)

    if not communities:
        print("❌ No communities detected. Try lowering threshold.")
        return

    link_mapping = infer_link_mapping(communities)

    print("\n🔗 Inferred Fronthaul Topology:")
    for link, cells in link_mapping.items():
        print(f"{link} → Cells: {cells}")

    print("\n🏁 PS1 TOPOLOGY IDENTIFICATION COMPLETE ✅")


if __name__ == "__main__":
    main()
