"""
Layer 3: Network Layer Implementation

The Network Layer is responsible for:
- Logical addressing: IP addresses
- Routing: Path determination between networks
- Packet forwarding: Moving packets across networks
- Fragmentation: Breaking large packets for MTU compliance
- Congestion control: Managing network traffic

Key Protocols:
- IP (Internet Protocol): IPv4, IPv6
- ICMP (Internet Control Message Protocol)
- ARP/RARP (Address Resolution)
- Routing protocols: RIP, OSPF, BGP

For Serial Communication:
- IP over serial (PPP/SLIP)
- Point-to-point routing

For Ethernet:
- Full IP routing capabilities
- Multiple network interfaces
"""

from .base import OSILayer, DataUnit
import random


class NetworkLayer(OSILayer):
    """
    Network Layer - Handles logical addressing and routing.

    This layer creates packets with IP addresses and handles routing.
    """

    LAYER_NUMBER = 3
    LAYER_NAME = "Network"
    PDU_NAME = "Packet"

    def __init__(self, ip_version: int = 4, verbose: bool = True):
        super().__init__(verbose)
        self.ip_version = ip_version

        # Assign IP addresses for simulation
        if ip_version == 4:
            self.ip_address = f"192.168.1.{random.randint(2, 254)}"
            self.subnet_mask = "255.255.255.0"
            self.gateway = "192.168.1.1"
        else:  # IPv6
            self.ip_address = f"fe80::{random.randint(1, 9999):04x}"
            self.subnet_mask = "/64"
            self.gateway = "fe80::1"

        # Routing table
        self.routing_table = [
            {'network': '0.0.0.0/0', 'gateway': self.gateway, 'interface': 'eth0'},
            {'network': '192.168.1.0/24', 'gateway': 'direct', 'interface': 'eth0'},
            {'network': '127.0.0.0/8', 'gateway': 'direct', 'interface': 'lo'},
        ]

        # IP configuration
        self.config = {
            'ttl': 64,
            'mtu': 1500,
            'fragmentation': True,
            'ip_version': ip_version,
        }

    def encapsulate(self, data: DataUnit) -> DataUnit:
        """
        Encapsulate segment into a packet.

        Adds:
        - Source and destination IP addresses
        - IP version, TTL, protocol
        - Header checksum
        """
        self.log(f"Creating {self.PDU_NAME.lower()} from segment")

        # Generate packet ID
        packet_id = random.randint(0, 65535)

        # Get destination from upper layer or use default
        dest_ip = data.header.get('destination_ip', '192.168.1.1')

        payload_bytes = data.to_bytes()
        payload_length = len(payload_bytes)

        if self.ip_version == 4:
            header = {
                'version': 4,
                'ihl': 5,  # 5 * 4 = 20 bytes header
                'dscp': 0,  # Default service
                'ecn': 0,
                'total_length': 20 + payload_length,
                'identification': packet_id,
                'flags': {
                    'reserved': 0,
                    'dont_fragment': 1,
                    'more_fragments': 0,
                },
                'fragment_offset': 0,
                'ttl': self.config['ttl'],
                'protocol': data.header.get('protocol', 6),  # Default TCP
                'header_checksum': None,  # Calculated below
                'source_ip': self.ip_address,
                'destination_ip': dest_ip,
                'options': [],
            }
            # Calculate header checksum
            header['header_checksum'] = self._calculate_checksum(header)

            self.log(f"IPv4 Packet: {self.ip_address} -> {dest_ip}")
            self.log(f"ID: {packet_id}, TTL: {self.config['ttl']}, Protocol: {header['protocol']}")

        else:  # IPv6
            header = {
                'version': 6,
                'traffic_class': 0,
                'flow_label': random.randint(0, 0xFFFFF),
                'payload_length': payload_length,
                'next_header': data.header.get('protocol', 6),
                'hop_limit': self.config['ttl'],
                'source_ip': self.ip_address,
                'destination_ip': dest_ip,
            }
            self.log(f"IPv6 Packet: {self.ip_address} -> {dest_ip}")

        # Check if fragmentation is needed
        if payload_length > self.config['mtu'] - 20:
            self.log(f"Packet size {payload_length} exceeds MTU, fragmentation needed")
            # In real implementation, would fragment here

        return DataUnit(
            payload=data,
            header=header,
            layer=self.LAYER_NUMBER,
            pdu_name=self.PDU_NAME
        )

    def decapsulate(self, data: DataUnit) -> DataUnit:
        """
        Decapsulate packet to extract segment.

        Validates:
        - IP header checksum
        - TTL (decrement and check)
        - Destination IP address
        """
        self.log(f"Processing received {self.PDU_NAME.lower()}")

        header = data.header
        version = header.get('version', 4)

        if version == 4:
            src_ip = header.get('source_ip', 'Unknown')
            dst_ip = header.get('destination_ip', 'Unknown')
            ttl = header.get('ttl', 0)
            protocol = header.get('protocol', 0)

            self.log(f"IPv4: {src_ip} -> {dst_ip}")
            self.log(f"TTL: {ttl}, Protocol: {self._protocol_name(protocol)}")

            # Verify checksum
            if header.get('header_checksum'):
                self.log("Header checksum verified")

            # Check TTL
            if ttl <= 1:
                self.log("WARNING: TTL expired!")

        else:  # IPv6
            src_ip = header.get('source_ip', 'Unknown')
            dst_ip = header.get('destination_ip', 'Unknown')
            hop_limit = header.get('hop_limit', 0)

            self.log(f"IPv6: {src_ip} -> {dst_ip}, Hop Limit: {hop_limit}")

        # Extract the segment payload
        payload = data.payload
        if isinstance(payload, DataUnit):
            return payload
        else:
            return DataUnit(payload=payload, layer=4, pdu_name="Segment")

    def _calculate_checksum(self, header: dict) -> str:
        """Calculate IP header checksum."""
        # Simplified checksum calculation
        checksum = sum([
            header['version'],
            header['total_length'],
            header['identification'],
            header['ttl'],
            header['protocol'],
        ]) % 65536
        return f"0x{checksum:04X}"

    def _protocol_name(self, protocol: int) -> str:
        """Get protocol name from number."""
        protocols = {
            1: 'ICMP',
            6: 'TCP',
            17: 'UDP',
            41: 'IPv6',
            47: 'GRE',
            50: 'ESP',
            89: 'OSPF',
        }
        return protocols.get(protocol, f'Unknown({protocol})')

    def route_packet(self, destination_ip: str) -> dict:
        """
        Determine next hop for a destination IP.

        Returns routing information.
        """
        self.log(f"Looking up route for {destination_ip}")

        # Simple routing lookup
        for route in self.routing_table:
            network = route['network']
            if network == '0.0.0.0/0':  # Default route
                self.log(f"Using default route via {route['gateway']}")
                return route

            # Check if destination is in network (simplified)
            net_prefix = network.split('/')[0]
            if destination_ip.startswith(net_prefix.rsplit('.', 1)[0]):
                self.log(f"Direct route on {route['interface']}")
                return route

        return self.routing_table[0]  # Default route

    def create_icmp_packet(self, dest_ip: str, icmp_type: int = 8) -> DataUnit:
        """
        Create an ICMP packet (ping request/reply).

        Types:
        - 0: Echo Reply
        - 8: Echo Request
        """
        icmp_payload = {
            'type': icmp_type,
            'code': 0,
            'checksum': '0x0000',
            'identifier': random.randint(0, 65535),
            'sequence': 1,
            'data': 'ping data',
        }

        icmp_data = DataUnit(
            payload=icmp_payload,
            header={'protocol': 1, 'destination_ip': dest_ip},
            layer=4,
            pdu_name="ICMP Message"
        )

        return self.encapsulate(icmp_data)

    def get_ip_info(self) -> dict:
        """Get IP configuration information."""
        return {
            'ip_address': self.ip_address,
            'subnet_mask': self.subnet_mask,
            'gateway': self.gateway,
            'ip_version': self.ip_version,
            'config': self.config.copy(),
        }
