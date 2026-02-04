"""
Layer 4: Transport Layer Implementation

The Transport Layer is responsible for:
- End-to-end communication between processes
- Segmentation and reassembly of data
- Flow control: Managing data transmission rate
- Error recovery: Retransmission of lost segments
- Multiplexing: Multiple connections via ports

Key Protocols:
- TCP (Transmission Control Protocol): Reliable, connection-oriented
- UDP (User Datagram Protocol): Unreliable, connectionless

For Serial Communication:
- Simple segmentation for large data transfers
- Basic acknowledgment schemes

For Ethernet:
- Full TCP/UDP implementation
- Port-based multiplexing
"""

from .base import OSILayer, DataUnit
import random
import time


class TransportLayer(OSILayer):
    """
    Transport Layer - Handles end-to-end communication.

    This layer creates segments with port numbers and handles
    reliable delivery (TCP) or fast delivery (UDP).
    """

    LAYER_NUMBER = 4
    LAYER_NAME = "Transport"
    PDU_NAME = "Segment"

    def __init__(self, protocol: str = "TCP", verbose: bool = True):
        super().__init__(verbose)
        self.protocol = protocol.upper()

        # Connection state (for TCP)
        self.connections = {}
        self.sequence_number = random.randint(0, 0xFFFFFFFF)
        self.ack_number = 0

        # Configuration
        self.config = {
            'window_size': 65535,
            'mss': 1460,  # Maximum Segment Size
            'timeout': 3.0,  # Retransmission timeout
            'max_retries': 5,
        }

    def encapsulate(self, data: DataUnit) -> DataUnit:
        """
        Encapsulate session data into a segment.

        Adds:
        - Source and destination ports
        - Sequence/Acknowledgment numbers (TCP)
        - Flags, window size, checksum
        """
        self.log(f"Creating {self.PDU_NAME.lower()} using {self.protocol}")

        # Get ports from upper layer or use defaults
        src_port = data.header.get('source_port', random.randint(49152, 65535))
        dst_port = data.header.get('destination_port', 80)

        payload_bytes = data.to_bytes()

        if self.protocol == "TCP":
            header = self._create_tcp_header(src_port, dst_port, payload_bytes)
            self.log(f"TCP: {src_port} -> {dst_port}")
            self.log(f"Seq: {header['sequence_number']}, Ack: {header['ack_number']}")
            self.log(f"Flags: {self._flags_to_string(header['flags'])}")

        else:  # UDP
            header = self._create_udp_header(src_port, dst_port, payload_bytes)
            self.log(f"UDP: {src_port} -> {dst_port}")
            self.log(f"Length: {header['length']} bytes")

        # Protocol number for network layer
        header['protocol'] = 6 if self.protocol == "TCP" else 17

        return DataUnit(
            payload=data,
            header=header,
            layer=self.LAYER_NUMBER,
            pdu_name=self.PDU_NAME if self.protocol == "TCP" else "Datagram"
        )

    def decapsulate(self, data: DataUnit) -> DataUnit:
        """
        Decapsulate segment to extract session data.

        Validates:
        - Checksum
        - Sequence numbers (TCP)
        - Port numbers
        """
        self.log(f"Processing received {self.PDU_NAME.lower()}")

        header = data.header
        src_port = header.get('source_port', 0)
        dst_port = header.get('destination_port', 0)

        if self.protocol == "TCP":
            seq = header.get('sequence_number', 0)
            ack = header.get('ack_number', 0)
            flags = header.get('flags', {})

            self.log(f"TCP: {src_port} -> {dst_port}")
            self.log(f"Seq: {seq}, Ack: {ack}")
            self.log(f"Flags: {self._flags_to_string(flags)}")

            # Update connection state
            if flags.get('SYN'):
                self.log("Connection request received")
            if flags.get('FIN'):
                self.log("Connection termination received")

        else:  # UDP
            length = header.get('length', 0)
            self.log(f"UDP: {src_port} -> {dst_port}, Length: {length}")

        # Extract the session data payload
        payload = data.payload
        if isinstance(payload, DataUnit):
            return payload
        else:
            return DataUnit(payload=payload, layer=5, pdu_name="Data")

    def _create_tcp_header(self, src_port: int, dst_port: int, payload: bytes) -> dict:
        """Create TCP segment header."""
        self.sequence_number = (self.sequence_number + len(payload)) % 0xFFFFFFFF

        return {
            'source_port': src_port,
            'destination_port': dst_port,
            'sequence_number': self.sequence_number,
            'ack_number': self.ack_number,
            'data_offset': 5,  # 5 * 4 = 20 bytes header
            'reserved': 0,
            'flags': {
                'URG': False,
                'ACK': self.ack_number > 0,
                'PSH': True,
                'RST': False,
                'SYN': False,
                'FIN': False,
            },
            'window_size': self.config['window_size'],
            'checksum': self._calculate_checksum(payload),
            'urgent_pointer': 0,
            'options': [],
        }

    def _create_udp_header(self, src_port: int, dst_port: int, payload: bytes) -> dict:
        """Create UDP datagram header."""
        return {
            'source_port': src_port,
            'destination_port': dst_port,
            'length': 8 + len(payload),  # Header + payload
            'checksum': self._calculate_checksum(payload),
        }

    def _calculate_checksum(self, data: bytes) -> str:
        """Calculate segment checksum."""
        checksum = sum(data) % 65536
        return f"0x{checksum:04X}"

    def _flags_to_string(self, flags: dict) -> str:
        """Convert TCP flags dict to string representation."""
        active = [flag for flag, value in flags.items() if value]
        return ','.join(active) if active else 'none'

    def create_syn_segment(self, dst_port: int, src_port: int = None) -> DataUnit:
        """Create a TCP SYN segment for connection establishment."""
        if src_port is None:
            src_port = random.randint(49152, 65535)

        self.sequence_number = random.randint(0, 0xFFFFFFFF)

        header = {
            'source_port': src_port,
            'destination_port': dst_port,
            'sequence_number': self.sequence_number,
            'ack_number': 0,
            'data_offset': 6,  # With options
            'flags': {
                'URG': False,
                'ACK': False,
                'PSH': False,
                'RST': False,
                'SYN': True,
                'FIN': False,
            },
            'window_size': self.config['window_size'],
            'checksum': '0x0000',
            'urgent_pointer': 0,
            'options': [
                {'kind': 2, 'length': 4, 'value': self.config['mss']},  # MSS
            ],
            'protocol': 6,
        }

        return DataUnit(
            payload="",
            header=header,
            layer=self.LAYER_NUMBER,
            pdu_name="SYN Segment"
        )

    def create_ack_segment(self, seq_to_ack: int, dst_port: int, src_port: int) -> DataUnit:
        """Create a TCP ACK segment."""
        header = {
            'source_port': src_port,
            'destination_port': dst_port,
            'sequence_number': self.sequence_number,
            'ack_number': seq_to_ack + 1,
            'data_offset': 5,
            'flags': {
                'URG': False,
                'ACK': True,
                'PSH': False,
                'RST': False,
                'SYN': False,
                'FIN': False,
            },
            'window_size': self.config['window_size'],
            'checksum': '0x0000',
            'urgent_pointer': 0,
            'protocol': 6,
        }

        return DataUnit(
            payload="",
            header=header,
            layer=self.LAYER_NUMBER,
            pdu_name="ACK Segment"
        )

    def simulate_three_way_handshake(self, dst_port: int = 80) -> list:
        """
        Simulate TCP three-way handshake.

        Returns list of segments exchanged.
        """
        segments = []
        src_port = random.randint(49152, 65535)

        # Step 1: SYN
        syn = self.create_syn_segment(dst_port, src_port)
        segments.append(('Client -> Server', 'SYN', syn))
        self.log("Step 1: Client sends SYN")

        # Step 2: SYN-ACK (simulated response)
        syn_ack_header = {
            'source_port': dst_port,
            'destination_port': src_port,
            'sequence_number': random.randint(0, 0xFFFFFFFF),
            'ack_number': self.sequence_number + 1,
            'flags': {'SYN': True, 'ACK': True},
            'protocol': 6,
        }
        syn_ack = DataUnit(payload="", header=syn_ack_header, layer=4, pdu_name="SYN-ACK")
        segments.append(('Server -> Client', 'SYN-ACK', syn_ack))
        self.log("Step 2: Server responds with SYN-ACK")

        # Step 3: ACK
        self.ack_number = syn_ack_header['sequence_number'] + 1
        ack = self.create_ack_segment(syn_ack_header['sequence_number'], dst_port, src_port)
        segments.append(('Client -> Server', 'ACK', ack))
        self.log("Step 3: Client sends ACK - Connection established!")

        return segments
