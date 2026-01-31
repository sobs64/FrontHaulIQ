
from ingestion.load_packet_stats import load_packet_stats
from alignment.time_shift import align_packet_loss
from ingestion.load_throughput import load_throughput_data

def check_size():
    throughput = load_throughput_data("data/raw/throughput")
    packets = load_packet_stats("data/raw/packet_stats")
    
    cells = sorted(set(throughput) & set(packets))
    if not cells:
        print("No common cells")
        return

    print(f"Common cells: {len(cells)}")
    
    # Check slots in first cell
    first_cell = cells[0]
    print(f"Cell {first_cell} packet data shape: {packets[first_cell].shape}")
    print(f"Min slot: {packets[first_cell]['slot'].min()}")
    print(f"Max slot: {packets[first_cell]['slot'].max()}")

if __name__ == "__main__":
    check_size()
