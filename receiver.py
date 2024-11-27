import socket
import threading
import time

def receive_packets(port, send_back_port, target_ip):
    """Receive packets and send them back to the sender."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("127.0.0.1", port))
    server_socket.listen(5)

    conn, addr = server_socket.accept()
    print(f"Connected by {addr}")

    flow_data = {}
    start_time = time.time()

    while True:
        data = conn.recv(1024)
        if not data:
            break
        message = data.decode()
        flow_id, packet_id, timestamp = message.split("|")
        flow_id = int(flow_id)

        if flow_id not in flow_data:
            flow_data[flow_id] = []

        flow_data[flow_id].append((int(packet_id), float(timestamp)))

    conn.close()
    server_socket.close()

    # Calculate metrics
    for flow_id, packets in flow_data.items():
        packets.sort()
        delays = [packets[i][1] - packets[i - 1][1] for i in range(1, len(packets))]
        jitter = [abs(delays[i] - delays[i - 1]) for i in range(1, len(delays))]
        print(f"\nFlow {flow_id}:")
        print(f"  Total Packets: {len(packets)}")
        print(f"  Average Delay: {sum(delays) / len(delays) if delays else 0:.4f} seconds")
        print(f"  Average Jitter: {sum(jitter) / len(jitter) if jitter else 0:.4f} seconds")

    # Sending back packets
    send_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    send_socket.connect((target_ip, send_back_port))
    for flow_id, packets in flow_data.items():
        for packet in packets:
            message = f"{flow_id}|{packet[0]}|{packet[1]}"
            send_socket.sendall(message.encode())
    send_socket.close()
    print("\nSent packets back to the sender.")

def main():
    receive_port = 5000
    send_back_port = 5001
    target_ip = "127.0.0.1"  # Use localhost for testing

    print("Receiver is waiting for packets...")
    receive_packets(receive_port, send_back_port, target_ip)

if __name__ == "__main__":
    main()
