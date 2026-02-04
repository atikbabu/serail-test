"""
Ethernet Communication Demonstration

Demonstrates how data flows through all 7 OSI layers
for Ethernet (IEEE 802.3) communication.

Ethernet communication characteristics:
- Multi-point network (bus/star topology)
- High speeds (10 Mbps - 100 Gbps)
- Used in LANs, data centers, enterprise networks
- Full TCP/IP protocol stack support
"""

from ..osi_layers import (
    DataUnit,
    PhysicalLayer,
    DataLinkLayer,
    NetworkLayer,
    TransportLayer,
    SessionLayer,
    PresentationLayer,
    ApplicationLayer,
)
import socket


class EthernetCommunicationDemo:
    """
    Demonstrates Ethernet communication through OSI layers.

    This class shows how data is encapsulated as it travels
    down the OSI stack for Ethernet transmission, and decapsulated
    when received.
    """

    def __init__(self, verbose: bool = True):
        self.verbose = verbose

        # Initialize all layers for Ethernet communication
        self.layers = {
            7: ApplicationLayer(protocol="HTTP", verbose=verbose),
            6: PresentationLayer(verbose=verbose),
            5: SessionLayer(verbose=verbose),
            4: TransportLayer(protocol="TCP", verbose=verbose),
            3: NetworkLayer(ip_version=4, verbose=verbose),
            2: DataLinkLayer(protocol="ethernet", verbose=verbose),
            1: PhysicalLayer(medium_type="ethernet", verbose=verbose),
        }

    def demonstrate_send(self, message: str, dest_ip: str = "192.168.1.1",
                        dest_port: int = 80, protocol: str = "HTTP") -> dict:
        """
        Demonstrate sending data through all OSI layers for Ethernet.

        Shows the complete encapsulation process from Layer 7 to Layer 1.

        Args:
            message: The application data to send
            dest_ip: Destination IP address
            dest_port: Destination port
            protocol: Application protocol (HTTP, DNS, etc.)

        Returns:
            Dictionary containing data at each layer
        """
        print("\n" + "=" * 70)
        print("ETHERNET COMMUNICATION - SENDING DATA THROUGH OSI LAYERS")
        print("=" * 70)

        # Set application protocol
        self.layers[7].set_protocol(protocol)

        layer_data = {}

        # Prepare HTTP request data
        if protocol == "HTTP":
            app_data = {
                'method': 'GET',
                'path': '/api/data',
                'host': dest_ip,
                'port': dest_port,
                'body': message,
                'headers': {
                    'Content-Type': 'text/plain',
                    'Accept': 'application/json',
                }
            }
        else:
            app_data = message

        print(f"\n📤 Original Message: '{message}'")
        print(f"   Destination: {dest_ip}:{dest_port}")
        print(f"   Protocol: {protocol}")
        print()

        # Layer 7: Application Layer
        print("-" * 70)
        print(f"LAYER 7 - APPLICATION LAYER ({protocol})")
        print("-" * 70)
        current_data = self.layers[7].encapsulate(app_data)
        # Add destination info for lower layers
        current_data.header['destination_ip'] = dest_ip
        current_data.header['destination_port'] = dest_port
        layer_data[7] = {
            'name': 'Application',
            'pdu': 'Data',
            'protocol': protocol,
            'data': current_data,
            'description': f'{protocol} request with headers and payload',
        }
        self._print_layer_details(current_data)

        # Layer 6: Presentation Layer
        print("\n" + "-" * 70)
        print("LAYER 6 - PRESENTATION LAYER (Encoding/Encryption)")
        print("-" * 70)
        current_data = self.layers[6].encapsulate(current_data)
        layer_data[6] = {
            'name': 'Presentation',
            'pdu': 'Data',
            'protocol': 'TLS/SSL (conceptually)',
            'data': current_data,
            'description': 'Data encoded, optionally encrypted and compressed',
        }
        self._print_layer_details(current_data)

        # Layer 5: Session Layer
        print("\n" + "-" * 70)
        print("LAYER 5 - SESSION LAYER (Connection Management)")
        print("-" * 70)
        current_data = self.layers[5].encapsulate(current_data)
        layer_data[5] = {
            'name': 'Session',
            'pdu': 'Data',
            'protocol': 'NetBIOS/RPC',
            'data': current_data,
            'description': 'Session established with sync points',
        }
        self._print_layer_details(current_data)

        # Layer 4: Transport Layer
        print("\n" + "-" * 70)
        print("LAYER 4 - TRANSPORT LAYER (TCP)")
        print("-" * 70)
        # Pass port information to transport layer
        current_data.header['destination_port'] = dest_port
        current_data = self.layers[4].encapsulate(current_data)
        layer_data[4] = {
            'name': 'Transport',
            'pdu': 'Segment',
            'protocol': 'TCP',
            'data': current_data,
            'description': 'TCP segment with ports, sequence numbers, flags',
        }
        self._print_layer_details(current_data)

        # Layer 3: Network Layer
        print("\n" + "-" * 70)
        print("LAYER 3 - NETWORK LAYER (IP)")
        print("-" * 70)
        current_data.header['destination_ip'] = dest_ip
        current_data = self.layers[3].encapsulate(current_data)
        layer_data[3] = {
            'name': 'Network',
            'pdu': 'Packet',
            'protocol': 'IPv4',
            'data': current_data,
            'description': 'IP packet with source/dest addresses, TTL',
        }
        self._print_layer_details(current_data)

        # Layer 2: Data Link Layer
        print("\n" + "-" * 70)
        print("LAYER 2 - DATA LINK LAYER (Ethernet)")
        print("-" * 70)
        current_data = self.layers[2].encapsulate(current_data)
        layer_data[2] = {
            'name': 'Data Link',
            'pdu': 'Frame',
            'protocol': 'IEEE 802.3',
            'data': current_data,
            'description': 'Ethernet frame with MAC addresses, EtherType, FCS',
        }
        self._print_layer_details(current_data)

        # Layer 1: Physical Layer
        print("\n" + "-" * 70)
        print("LAYER 1 - PHYSICAL LAYER (100BASE-TX)")
        print("-" * 70)
        current_data = self.layers[1].encapsulate(current_data)
        layer_data[1] = {
            'name': 'Physical',
            'pdu': 'Bits',
            'protocol': '100BASE-TX',
            'data': current_data,
            'description': 'Bit stream with preamble, 4B/5B encoding',
        }
        self._print_layer_details(current_data)

        # Physical transmission statistics
        print("\n" + "=" * 70)
        print("PHYSICAL TRANSMISSION (Ethernet)")
        print("=" * 70)
        bits = current_data.payload
        stats = self.layers[1].simulate_transmission(bits)
        print(f"   Bits to transmit: {stats['bits_transmitted']}")
        print(f"   Transmission time: {stats['transmission_time_seconds']*1000000:.2f} µs")
        print(f"   Speed: 100 Mbps (Fast Ethernet)")
        print(f"   Encoding: 4B/5B + MLT-3")
        print(f"   Medium: Cat5e UTP cable")

        return layer_data

    def demonstrate_receive(self, bits: str) -> dict:
        """
        Demonstrate receiving data through all OSI layers.

        Shows the complete decapsulation process from Layer 1 to Layer 7.
        """
        print("\n" + "=" * 70)
        print("ETHERNET COMMUNICATION - RECEIVING DATA THROUGH OSI LAYERS")
        print("=" * 70)

        layer_data = {}

        current_data = DataUnit(
            payload=bits,
            header={'medium': 'ethernet', 'encoding': '4B/5B'},
            layer=1,
            pdu_name="Bits"
        )

        print(f"\n📥 Received {len(bits)} bits from Ethernet interface")
        print()

        # Decapsulate through all layers
        for layer_num in range(1, 7):
            print("-" * 70)
            print(f"LAYER {layer_num} -> {layer_num + 1}: "
                  f"{self.layers[layer_num].LAYER_NAME} to {self.layers[layer_num + 1].LAYER_NAME}")
            print("-" * 70)
            current_data = self.layers[layer_num].decapsulate(current_data)
            layer_data[layer_num] = {'processed': current_data}
            self._print_layer_details(current_data)
            print()

        # Final application data
        print("-" * 70)
        print("LAYER 7: Application Layer - Final Data")
        print("-" * 70)
        final_data = self.layers[7].decapsulate(current_data)
        layer_data[7] = {'processed': final_data}
        print(f"   📨 Received Application Data: {final_data}")

        return layer_data

    def demonstrate_tcp_handshake(self, dest_ip: str = "192.168.1.1",
                                  dest_port: int = 80) -> list:
        """
        Demonstrate TCP three-way handshake through OSI layers.

        Shows SYN -> SYN-ACK -> ACK exchange.
        """
        print("\n" + "=" * 70)
        print("TCP THREE-WAY HANDSHAKE DEMONSTRATION")
        print("=" * 70)

        transport = self.layers[4]
        segments = transport.simulate_three_way_handshake(dest_port)

        print("\n📡 Handshake Complete!")
        print(f"   Connection established to {dest_ip}:{dest_port}")

        return segments

    def demonstrate_arp_resolution(self, target_ip: str = "192.168.1.1") -> DataUnit:
        """
        Demonstrate ARP (Address Resolution Protocol).

        Shows how IP addresses are resolved to MAC addresses.
        """
        print("\n" + "=" * 70)
        print("ARP RESOLUTION DEMONSTRATION")
        print("=" * 70)

        print(f"\n🔍 Resolving IP {target_ip} to MAC address...")

        # Create ARP request
        data_link = self.layers[2]
        arp_frame = data_link.create_arp_frame(target_ip)

        print(f"\n📤 ARP Request:")
        print(f"   Who has {target_ip}? Tell {data_link.mac_address}")
        print(f"   Broadcast to: FF:FF:FF:FF:FF:FF")
        self._print_layer_details(arp_frame)

        # Simulate ARP response
        print(f"\n📥 ARP Reply (simulated):")
        resolved_mac = "AA:BB:CC:DD:EE:FF"
        print(f"   {target_ip} is at {resolved_mac}")

        return arp_frame

    def demonstrate_dns_query(self, domain: str = "example.com") -> DataUnit:
        """
        Demonstrate DNS query through OSI layers.
        """
        print("\n" + "=" * 70)
        print("DNS QUERY DEMONSTRATION")
        print("=" * 70)

        # Set to DNS protocol
        self.layers[7].set_protocol("DNS")

        print(f"\n🔍 Resolving domain: {domain}")

        dns_query = self.layers[7].create_dns_query(domain, 'A')
        print(f"\n📤 DNS Query:")
        self._print_layer_details(dns_query)

        # Simulate DNS response
        print(f"\n📥 DNS Response (simulated):")
        print(f"   {domain} -> 93.184.216.34")

        return dns_query

    def _print_layer_details(self, data: DataUnit):
        """Print details about data at current layer."""
        print(f"   PDU Type: {data.pdu_name}")
        print(f"   Header: {data.header}")
        if data.trailer:
            print(f"   Trailer: {data.trailer}")

        payload = data.payload
        if isinstance(payload, DataUnit):
            print(f"   Payload: [Encapsulated {payload.pdu_name}]")
        elif isinstance(payload, str) and len(payload) > 100:
            print(f"   Payload: {payload[:100]}... ({len(payload)} chars)")
        else:
            print(f"   Payload: {payload}")

        print(f"   Size: {data.get_size()} bytes")

    def get_ethernet_layer_summary(self) -> list:
        """Get a summary of all layers for Ethernet communication."""
        return [
            {
                'layer': 7,
                'name': 'Application',
                'ethernet_protocol': 'HTTP, FTP, SMTP, DNS',
                'function': 'User applications, web browsing, email',
                'pdu': 'Data',
            },
            {
                'layer': 6,
                'name': 'Presentation',
                'ethernet_protocol': 'TLS/SSL, MIME, JPEG',
                'function': 'Encryption, compression, format conversion',
                'pdu': 'Data',
            },
            {
                'layer': 5,
                'name': 'Session',
                'ethernet_protocol': 'NetBIOS, RPC, SQL',
                'function': 'Session management, dialog control',
                'pdu': 'Data',
            },
            {
                'layer': 4,
                'name': 'Transport',
                'ethernet_protocol': 'TCP, UDP',
                'function': 'Reliable delivery, port multiplexing',
                'pdu': 'Segment/Datagram',
            },
            {
                'layer': 3,
                'name': 'Network',
                'ethernet_protocol': 'IP, ICMP, ARP',
                'function': 'Logical addressing, routing',
                'pdu': 'Packet',
            },
            {
                'layer': 2,
                'name': 'Data Link',
                'ethernet_protocol': 'IEEE 802.3',
                'function': 'MAC addressing, framing, error detection',
                'pdu': 'Frame',
            },
            {
                'layer': 1,
                'name': 'Physical',
                'ethernet_protocol': '100BASE-TX, 1000BASE-T',
                'function': 'Bit transmission, signaling, cable specs',
                'pdu': 'Bits',
            },
        ]

    def compare_with_serial(self) -> dict:
        """
        Compare Ethernet and Serial communication at each layer.

        Returns comparison data for display.
        """
        return {
            7: {
                'layer': 'Application',
                'ethernet': 'HTTP, FTP, SMTP (rich protocols)',
                'serial': 'Modbus, DNP3 (industrial)',
                'difference': 'Ethernet supports more complex protocols',
            },
            6: {
                'layer': 'Presentation',
                'ethernet': 'Full TLS/SSL encryption',
                'serial': 'Basic encoding, simple encryption',
                'difference': 'Ethernet has stronger security options',
            },
            5: {
                'layer': 'Session',
                'ethernet': 'Full session management',
                'serial': 'Transaction IDs only',
                'difference': 'Ethernet supports complex sessions',
            },
            4: {
                'layer': 'Transport',
                'ethernet': 'TCP/UDP with full features',
                'serial': 'Simplified or none',
                'difference': 'Ethernet has robust flow control',
            },
            3: {
                'layer': 'Network',
                'ethernet': 'Full IP routing',
                'serial': 'Point-to-point (PPP/SLIP)',
                'difference': 'Ethernet supports complex networks',
            },
            2: {
                'layer': 'Data Link',
                'ethernet': 'IEEE 802.3, CSMA/CD',
                'serial': 'HDLC/PPP framing',
                'difference': 'Ethernet handles multiple devices',
            },
            1: {
                'layer': 'Physical',
                'ethernet': '100Mbps+, 4B/5B encoding',
                'serial': '115200 baud max, NRZ',
                'difference': 'Ethernet is much faster',
            },
        }

    def send_real_packet(self, dest_ip: str, dest_port: int, message: str) -> bool:
        """
        Send a real TCP packet over the network.

        This uses actual sockets for network communication.

        Args:
            dest_ip: Destination IP address
            dest_port: Destination port
            message: Message to send

        Returns:
            True if successful
        """
        print(f"\n📤 Sending real packet to {dest_ip}:{dest_port}")

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(5.0)
                sock.connect((dest_ip, dest_port))
                sock.sendall(message.encode())
                print("✅ Packet sent successfully")
                return True
        except Exception as e:
            print(f"❌ Failed to send: {e}")
            return False
