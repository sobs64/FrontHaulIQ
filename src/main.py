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

from ps2.link_aggregation import aggregate_link_throughput
from ps2.capacity_estimation import (
    required_capacity_no_buffer,
    required_capacity_with_buffer
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
            window=5
        )
        for cell in common_cells
    }

    event_matrix = build_congestion_matrix(event_data)
    corr_matrix = compute_correlation_matrix(event_matrix)

    print("Event matrix shape:", event_matrix.shape)
    print("\nCorrelation matrix (rounded):")
    print(corr_matrix.round(2))

    print("\n🏁 PS1 correlation computation complete.\n")

    # -------------------------
    # PS1: Graph-based topology inference
    # -------------------------
    print("🕸️ Building correlation graph...")

    G = build_correlation_graph(
        corr_matrix,
        threshold=0.25
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

        # -------------------------
    # PS2: Capacity Estimation
    # -------------------------
    print("\n📈 PS2: Estimating fronthaul link capacities...\n")

    # Convert throughput to slot-level if not already
    from preprocessing.symbol_to_slot import convert_to_slot_level

    slot_throughput = {
        cell: convert_to_slot_level(throughput_data[cell])
        for cell in throughput_data
    }

    link_throughput = aggregate_link_throughput(
        slot_throughput,
        link_mapping
    )

    print("🔢 Required Capacity per Link:\n")

    for link, df in link_throughput.items():
        cap_no_buf = required_capacity_no_buffer(df)
        cap_buf = required_capacity_with_buffer(df)

        print(f"{link}:")
        print(f"  ▸ Required capacity (no buffer): {cap_no_buf:.2f} Gbps")
        print(f"  ▸ Required capacity (with buffer): {cap_buf:.2f} Gbps\n")



if __name__ == "__main__":
    main()
