#!/usr/bin/env python3
"""
OSI Model Communication Demo - Standalone Version
Run this single file to see serial and ethernet communication through all OSI layers.

Usage: python osi_demo_standalone.py
"""

import json
import hashlib
import random
from datetime import datetime
from dataclasses import dataclass, field
from typing import Any

# ============================================================================
# DATA UNIT - Core data structure for all layers
# ============================================================================

@dataclass
class DataUnit:
    """Protocol Data Unit - represents data at any OSI layer."""
    payload: Any
    header: dict = field(default_factory=dict)
    trailer: dict = field(default_factory=dict)
    layer: int = 0
    pdu_name: str = "Data"

    def to_bytes(self) -> bytes:
        data = {
            'header': self.header,
            'payload': self.payload if isinstance(self.payload, (str, dict)) else str(self.payload),
            'trailer': self.trailer
        }
        return json.dumps(data).encode('utf-8')

    def get_size(self) -> int:
        return len(self.to_bytes())


# ============================================================================
# OSI LAYER IMPLEMENTATIONS
# ============================================================================

class Layer7_Application:
    """Application Layer - HTTP, Modbus protocols"""

    def encapsulate(self, data: Any, protocol: str = "HTTP") -> DataUnit:
        print(f"\n{'='*60}")
        print("LAYER 7 - APPLICATION")
        print(f"{'='*60}")

        if protocol == "HTTP":
            header = {
                'protocol': 'HTTP/1.1',
                'method': 'GET',
                'path': '/api/data',
                'host': 'example.com',
                'user_agent': 'OSI-Demo/1.0',
            }
            print(f"  Protocol: HTTP/1.1")
            print(f"  Method: GET /api/data")
        else:  # Serial/Modbus
            header = {
                'protocol': 'MODBUS',
                'function_code': 3,
                'unit_id': 1,
            }
            print(f"  Protocol: MODBUS RTU")
            print(f"  Function: Read Holding Registers")

        print(f"  Payload: {data}")
        return DataUnit(payload=data, header=header, layer=7, pdu_name="Data")


class Layer6_Presentation:
    """Presentation Layer - Encoding, encryption"""

    def encapsulate(self, data: DataUnit) -> DataUnit:
        print(f"\n{'='*60}")
        print("LAYER 6 - PRESENTATION")
        print(f"{'='*60}")

        # Serialize to JSON
        serialized = json.dumps(data.payload).encode('utf-8')

        header = {
            'encoding': 'utf-8',
            'format': 'JSON',
            'compression': None,
            'encryption': None,
            'original_size': len(str(data.payload)),
        }

        print(f"  Encoding: UTF-8")
        print(f"  Format: JSON")
        print(f"  Size: {header['original_size']} bytes")

        return DataUnit(payload=data, header=header, layer=6, pdu_name="Data")


class Layer5_Session:
    """Session Layer - Session management"""

    def __init__(self):
        self.session_id = f"SES-{random.randint(10000, 99999)}"

    def encapsulate(self, data: DataUnit) -> DataUnit:
        print(f"\n{'='*60}")
        print("LAYER 5 - SESSION")
        print(f"{'='*60}")

        header = {
            'session_id': self.session_id,
            'dialog_mode': 'full-duplex',
            'sync_point': 1,
            'timestamp': datetime.now().isoformat(),
        }

        print(f"  Session ID: {self.session_id}")
        print(f"  Dialog Mode: Full-duplex")
        print(f"  Sync Point: 1")

        return DataUnit(payload=data, header=header, layer=5, pdu_name="Data")


class Layer4_Transport:
    """Transport Layer - TCP/UDP"""

    def __init__(self, protocol: str = "TCP"):
        self.protocol = protocol
        self.seq_num = random.randint(1000, 9999)

    def encapsulate(self, data: DataUnit, dest_port: int = 80) -> DataUnit:
        print(f"\n{'='*60}")
        print(f"LAYER 4 - TRANSPORT ({self.protocol})")
        print(f"{'='*60}")

        src_port = random.randint(49152, 65535)

        if self.protocol == "TCP":
            header = {
                'source_port': src_port,
                'destination_port': dest_port,
                'sequence_number': self.seq_num,
                'ack_number': 0,
                'flags': {'SYN': False, 'ACK': True, 'PSH': True, 'FIN': False},
                'window_size': 65535,
                'checksum': f"0x{random.randint(0, 65535):04X}",
            }
            print(f"  Source Port: {src_port}")
            print(f"  Dest Port: {dest_port}")
            print(f"  Sequence: {self.seq_num}")
            print(f"  Flags: ACK, PSH")
            print(f"  Window: 65535")
        else:  # UDP
            header = {
                'source_port': src_port,
                'destination_port': dest_port,
                'length': data.get_size() + 8,
                'checksum': f"0x{random.randint(0, 65535):04X}",
            }
            print(f"  Source Port: {src_port}")
            print(f"  Dest Port: {dest_port}")
            print(f"  Length: {header['length']}")

        return DataUnit(payload=data, header=header, layer=4, pdu_name="Segment")


class Layer3_Network:
    """Network Layer - IP"""

    def __init__(self):
        self.src_ip = f"192.168.1.{random.randint(2, 254)}"

    def encapsulate(self, data: DataUnit, dest_ip: str = "192.168.1.1") -> DataUnit:
        print(f"\n{'='*60}")
        print("LAYER 3 - NETWORK (IPv4)")
        print(f"{'='*60}")

        header = {
            'version': 4,
            'header_length': 20,
            'ttl': 64,
            'protocol': 6,  # TCP
            'source_ip': self.src_ip,
            'destination_ip': dest_ip,
            'identification': random.randint(0, 65535),
            'checksum': f"0x{random.randint(0, 65535):04X}",
        }

        print(f"  Source IP: {self.src_ip}")
        print(f"  Dest IP: {dest_ip}")
        print(f"  TTL: 64")
        print(f"  Protocol: TCP (6)")

        return DataUnit(payload=data, header=header, layer=3, pdu_name="Packet")


class Layer2_DataLink:
    """Data Link Layer - Ethernet/HDLC"""

    def __init__(self, protocol: str = "ethernet"):
        self.protocol = protocol
        self.mac = ':'.join(f'{random.randint(0,255):02X}' for _ in range(6))

    def encapsulate(self, data: DataUnit) -> DataUnit:
        print(f"\n{'='*60}")
        if self.protocol == "ethernet":
            print("LAYER 2 - DATA LINK (Ethernet IEEE 802.3)")
        else:
            print("LAYER 2 - DATA LINK (HDLC)")
        print(f"{'='*60}")

        if self.protocol == "ethernet":
            dest_mac = "FF:FF:FF:FF:FF:FF"  # Broadcast
            header = {
                'destination_mac': dest_mac,
                'source_mac': self.mac,
                'ethertype': '0x0800',  # IPv4
            }
            fcs = hashlib.md5(data.to_bytes()).hexdigest()[:8]
            trailer = {'fcs': f"0x{fcs.upper()}"}

            print(f"  Source MAC: {self.mac}")
            print(f"  Dest MAC: {dest_mac}")
            print(f"  EtherType: 0x0800 (IPv4)")
            print(f"  FCS: 0x{fcs.upper()}")
        else:  # HDLC for serial
            header = {
                'flag': '0x7E',
                'address': '0xFF',
                'control': '0x03',
            }
            crc = hashlib.md5(data.to_bytes()).hexdigest()[:4]
            trailer = {'fcs': f"0x{crc.upper()}", 'flag_end': '0x7E'}

            print(f"  Flag: 0x7E")
            print(f"  Address: 0xFF (Broadcast)")
            print(f"  Control: 0x03")
            print(f"  FCS: 0x{crc.upper()}")

        return DataUnit(payload=data, header=header, trailer=trailer, layer=2, pdu_name="Frame")


class Layer1_Physical:
    """Physical Layer - Bits"""

    def __init__(self, medium: str = "ethernet"):
        self.medium = medium

    def encapsulate(self, data: DataUnit) -> DataUnit:
        print(f"\n{'='*60}")
        if self.medium == "ethernet":
            print("LAYER 1 - PHYSICAL (100BASE-TX)")
        else:
            print("LAYER 1 - PHYSICAL (RS-232)")
        print(f"{'='*60}")

        # Convert to bits
        raw_bytes = data.to_bytes()
        bits = ''.join(format(byte, '08b') for byte in raw_bytes)

        if self.medium == "ethernet":
            preamble = "10101010" * 7
            sfd = "10101011"
            full_bits = preamble + sfd + bits

            header = {
                'encoding': '4B/5B + MLT-3',
                'speed': '100 Mbps',
                'medium': 'Cat5e UTP',
                'preamble_bits': 56,
                'sfd_bits': 8,
            }

            print(f"  Encoding: 4B/5B + MLT-3")
            print(f"  Speed: 100 Mbps")
            print(f"  Preamble: 56 bits")
            print(f"  SFD: 10101011")
            print(f"  Data bits: {len(bits)}")
            print(f"  Total bits: {len(full_bits)}")
        else:  # Serial
            # Add UART framing (start + 8 data + stop for each byte)
            framed_bits = ""
            for i in range(0, len(bits), 8):
                byte_bits = bits[i:i+8]
                framed_bits += "0" + byte_bits + "1"  # Start=0, Stop=1

            header = {
                'encoding': 'NRZ',
                'baud_rate': 9600,
                'config': '8N1',
                'voltage_high': '+12V',
                'voltage_low': '-12V',
            }
            full_bits = framed_bits

            print(f"  Encoding: NRZ (Non-Return-to-Zero)")
            print(f"  Baud Rate: 9600")
            print(f"  Config: 8N1 (8 data, No parity, 1 stop)")
            print(f"  Voltage: +12V/-12V (RS-232)")
            print(f"  Data bits: {len(bits)}")
            print(f"  With UART framing: {len(full_bits)} bits")

        return DataUnit(payload=full_bits, header=header, layer=1, pdu_name="Bits")


# ============================================================================
# DEMONSTRATION FUNCTIONS
# ============================================================================

def demonstrate_ethernet(message: str):
    """Demonstrate Ethernet/TCP-IP communication through all OSI layers."""
    print("\n" + "=" * 70)
    print("       ETHERNET COMMUNICATION - DATA FLOW THROUGH OSI LAYERS")
    print("=" * 70)
    print(f"\n📤 Original Message: '{message}'")
    print(f"   Destination: 192.168.1.1:80 (HTTP)")

    # Initialize layers
    L7 = Layer7_Application()
    L6 = Layer6_Presentation()
    L5 = Layer5_Session()
    L4 = Layer4_Transport("TCP")
    L3 = Layer3_Network()
    L2 = Layer2_DataLink("ethernet")
    L1 = Layer1_Physical("ethernet")

    # Encapsulate through all layers
    data = L7.encapsulate(message, "HTTP")
    data = L6.encapsulate(data)
    data = L5.encapsulate(data)
    data = L4.encapsulate(data, dest_port=80)
    data = L3.encapsulate(data, dest_ip="192.168.1.1")
    data = L2.encapsulate(data)
    data = L1.encapsulate(data)

    print("\n" + "=" * 70)
    print("                    TRANSMISSION COMPLETE")
    print("=" * 70)
    print(f"  Total bits to transmit: {len(data.payload)}")
    print(f"  Transmission time @ 100Mbps: {len(data.payload)/100000000*1000000:.2f} µs")
    print("=" * 70)


def demonstrate_serial(message: str):
    """Demonstrate Serial/RS-232 communication through all OSI layers."""
    print("\n" + "=" * 70)
    print("        SERIAL COMMUNICATION - DATA FLOW THROUGH OSI LAYERS")
    print("=" * 70)
    print(f"\n📤 Original Message: '{message}'")
    print(f"   Protocol: Modbus RTU over RS-232")

    # Initialize layers
    L7 = Layer7_Application()
    L6 = Layer6_Presentation()
    L5 = Layer5_Session()
    L4 = Layer4_Transport("TCP")  # Simplified for serial
    L3 = Layer3_Network()
    L2 = Layer2_DataLink("serial")
    L1 = Layer1_Physical("serial")

    # Encapsulate through all layers
    data = L7.encapsulate(message, "MODBUS")
    data = L6.encapsulate(data)
    data = L5.encapsulate(data)
    data = L4.encapsulate(data, dest_port=502)  # Modbus port
    data = L3.encapsulate(data)
    data = L2.encapsulate(data)
    data = L1.encapsulate(data)

    print("\n" + "=" * 70)
    print("                    TRANSMISSION COMPLETE")
    print("=" * 70)
    print(f"  Total bits to transmit: {len(data.payload)}")
    print(f"  Transmission time @ 9600 baud: {len(data.payload)/9600*1000:.2f} ms")
    print("=" * 70)


def show_osi_model():
    """Display the OSI model structure."""
    print("\n" + "=" * 60)
    print("              OSI REFERENCE MODEL")
    print("=" * 60)

    layers = [
        (7, "Application", "Data", "HTTP, FTP, SMTP, Modbus"),
        (6, "Presentation", "Data", "TLS/SSL, JPEG, ASCII"),
        (5, "Session", "Data", "NetBIOS, RPC, SQL"),
        (4, "Transport", "Segment", "TCP, UDP"),
        (3, "Network", "Packet", "IP, ICMP, ARP"),
        (2, "Data Link", "Frame", "Ethernet, HDLC, PPP"),
        (1, "Physical", "Bits", "RS-232, 100BASE-TX"),
    ]

    for num, name, pdu, protocols in layers:
        print(f"┌{'─' * 56}┐")
        print(f"│ Layer {num}: {name:<14} │ PDU: {pdu:<8} │ {protocols:<15} │")
        print(f"└{'─' * 56}┘")
        if num > 1:
            print(f"          {'↓' * 5}    {'↑' * 5}")
    print()


def show_comparison():
    """Show comparison between Serial and Ethernet at each layer."""
    print("\n" + "=" * 80)
    print("               SERIAL vs ETHERNET COMPARISON BY OSI LAYER")
    print("=" * 80)

    comparisons = [
        (7, "Application", "Modbus, Custom", "HTTP, FTP, DNS"),
        (6, "Presentation", "Binary/ASCII", "TLS/SSL, MIME"),
        (5, "Session", "Transaction IDs", "NetBIOS, RPC"),
        (4, "Transport", "Simplified", "TCP, UDP"),
        (3, "Network", "PPP/SLIP", "IPv4, IPv6"),
        (2, "Data Link", "HDLC", "IEEE 802.3"),
        (1, "Physical", "RS-232 (9600 baud)", "100BASE-TX (100 Mbps)"),
    ]

    print(f"\n{'Layer':<8} {'Name':<14} {'Serial':<20} {'Ethernet':<20}")
    print("-" * 70)

    for num, name, serial, ethernet in comparisons:
        print(f"{num:<8} {name:<14} {serial:<20} {ethernet:<20}")

    print("-" * 70)


def show_tcp_handshake():
    """Display TCP three-way handshake."""
    print("\n" + "=" * 50)
    print("       TCP THREE-WAY HANDSHAKE")
    print("=" * 50)
    print()
    print("    Client                     Server")
    print("      │                           │")
    print("      │───── SYN (seq=100) ──────>│")
    print("      │                           │")
    print("      │<──── SYN-ACK ────────────│")
    print("      │      (seq=300, ack=101)   │")
    print("      │                           │")
    print("      │───── ACK (ack=301) ──────>│")
    print("      │                           │")
    print("      │   Connection Established  │")
    print("      │                           │")
    print()


def show_frame_structures():
    """Display frame structures for Ethernet and HDLC."""
    print("\n" + "=" * 70)
    print("                    ETHERNET FRAME STRUCTURE")
    print("=" * 70)
    print()
    print("┌──────────┬──────────┬──────────┬──────────────────┬─────┐")
    print("│ Preamble │ Dest MAC │ Src MAC  │     Payload      │ FCS │")
    print("│ 8 bytes  │ 6 bytes  │ 6 bytes  │   46-1500 bytes  │ 4B  │")
    print("└──────────┴──────────┴──────────┴──────────────────┴─────┘")

    print("\n" + "=" * 70)
    print("                    HDLC FRAME STRUCTURE (Serial)")
    print("=" * 70)
    print()
    print("┌──────┬─────────┬─────────┬──────────────────┬─────┬──────┐")
    print("│ Flag │ Address │ Control │     Payload      │ FCS │ Flag │")
    print("│ 0x7E │ 1 byte  │ 1 byte  │   Variable       │ 2B  │ 0x7E │")
    print("└──────┴─────────┴─────────┴──────────────────┴─────┴──────┘")


def main_menu():
    """Interactive main menu."""
    print("\n" + "=" * 60)
    print("     OSI MODEL COMMUNICATION DEMONSTRATION")
    print("     Serial & Ethernet through all 7 layers")
    print("=" * 60)

    while True:
        print("\n" + "-" * 40)
        print("MAIN MENU")
        print("-" * 40)
        print("1. Show OSI Model Overview")
        print("2. Serial Communication Demo")
        print("3. Ethernet Communication Demo")
        print("4. Compare Serial vs Ethernet")
        print("5. TCP Handshake Diagram")
        print("6. Frame Structures")
        print("0. Exit")
        print("-" * 40)

        choice = input("Select option: ").strip()

        if choice == '1':
            show_osi_model()
        elif choice == '2':
            msg = input("Enter message (or press Enter for default): ").strip()
            demonstrate_serial(msg or "Hello Serial!")
        elif choice == '3':
            msg = input("Enter message (or press Enter for default): ").strip()
            demonstrate_ethernet(msg or "Hello Ethernet!")
        elif choice == '4':
            show_comparison()
        elif choice == '5':
            show_tcp_handshake()
        elif choice == '6':
            show_frame_structures()
        elif choice == '0':
            print("\nGoodbye! 👋")
            break
        else:
            print("Invalid option, try again.")

        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main_menu()
