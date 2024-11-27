import socket
import threading
import time

def send_flow(flow_id, destination_ip, port, duration):
    """Send packets for a single flow."""
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    for attempt in range(3):  # Retry up to 3 times
        try:
            client_socket.connect((destination_ip, port))
            break
        except ConnectionRefusedError:
            print(f"Flow {flow_id}: Connection refused, retrying...")
            time.sleep(1)
    else:
        print(f"Flow {flow_id}: Failed to connect after retries.")
        return

    start_time = time.time()
    packet_count = 0
    while time.time() - start_time < duration:
        timestamp = time.time()
        message = f"{flow_id}|{packet_count}|{timestamp}"
        client_socket.sendall(message.encode())
        packet_count += 1
        time.sleep(0.1)  # 10 packets per second
    client_socket.close()
    print(f"Flow {flow_id} completed: Sent {packet_count} packets.")


def receive_packets(port):
    """Receive packets sent back by the receiver."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("127.0.0.1", port))
    server_socket.listen(5)

    conn, addr = server_socket.accept()
    print(f"Connected back by {addr}")

    received_data = []
    while True:
        data = conn.recv(1024)
        if not data:  # Connection closed by the receiver
            break
        message = data.decode()
        received_data.append(message)

    conn.close()
    server_socket.close()

    print("\nReceived Packets (First 5 shown):")
    for packet in received_data[:5]:
        print(f"  {packet}")
    print(f"Total received packets: {len(received_data)}")


def main():
    destination_ip = "127.0.0.1"  # Use localhost for testing
    send_port = 5000
    receive_port = 5001
    duration = 10  # Duration in seconds for each flow
    num_flows = int(input("Enter the number of flows: "))

    # Sending flows
    threads = []
    for flow_id in range(1, num_flows + 1):
        thread = threading.Thread(target=send_flow, args=(flow_id, destination_ip, send_port, duration))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    # Receiving response
    receive_packets(receive_port)

if __name__ == "__main__":
    main()
