"""
Layer 2: Data Link Layer Implementation

The Data Link Layer is responsible for:
- Framing: Encapsulating packets into frames
- Physical addressing: MAC addresses
- Error detection: CRC, checksums
- Flow control: Preventing buffer overflow
- Access control: CSMA/CD for Ethernet

Sublayers:
- LLC (Logical Link Control): Flow control, error checking
- MAC (Media Access Control): Physical addressing, media access

For Serial Communication:
- HDLC, PPP, SLIP protocols
- Simple framing with flags and escape sequences

For Ethernet:
- IEEE 802.3 frame format
- MAC addressing (48-bit)
- FCS (Frame Check Sequence)
"""

from .base import OSILayer, DataUnit
import hashlib
import random


class DataLinkLayer(OSILayer):
    """
    Data Link Layer - Handles framing and physical addressing.

    This layer creates frames with MAC addresses and error detection.
    """

    LAYER_NUMBER = 2
    LAYER_NAME = "Data Link"
    PDU_NAME = "Frame"

    def __init__(self, protocol: str = "ethernet", verbose: bool = True):
        super().__init__(verbose)
        self.protocol = protocol

        # Generate simulated MAC address
        self.mac_address = self._generate_mac()

        # Protocol-specific configurations
        if protocol == "serial":
            self.config = {
                'protocol': 'HDLC',
                'flag': '7E',  # HDLC flag
                'escape': '7D',
                'max_frame_size': 1500,
            }
        else:  # ethernet
            self.config = {
                'protocol': 'IEEE 802.3',
                'max_frame_size': 1518,  # bytes
                'min_frame_size': 64,    # bytes
                'ethertype': '0800',     # IPv4
            }

    def _generate_mac(self) -> str:
        """Generate a random MAC address for simulation."""
        mac = [random.randint(0, 255) for _ in range(6)]
        # Set locally administered bit
        mac[0] = (mac[0] | 0x02) & 0xFE
        return ':'.join(f'{b:02X}' for b in mac)

    def encapsulate(self, data: DataUnit) -> DataUnit:
        """
        Encapsulate packet into a frame.

        Adds:
        - Source and destination MAC addresses
        - Frame type/length
        - Error detection (FCS/CRC)
        """
        self.log(f"Creating {self.PDU_NAME.lower()} from packet")

        payload_bytes = data.to_bytes()

        if self.protocol == "serial":
            # HDLC-style framing
            header = {
                'protocol': 'HDLC',
                'flag_start': '0x7E',
                'address': '0xFF',  # Broadcast
                'control': '0x03',  # Unnumbered Information
                'sequence': random.randint(0, 255),
            }
            # Calculate CRC-16
            crc = self._calculate_crc(payload_bytes)
            trailer = {
                'fcs': crc,
                'flag_end': '0x7E',
            }
            self.log(f"HDLC frame: Address=0xFF, Control=0x03, FCS={crc}")

        else:  # Ethernet
            dest_mac = "FF:FF:FF:FF:FF:FF"  # Broadcast for demo
            header = {
                'destination_mac': dest_mac,
                'source_mac': self.mac_address,
                'ethertype': self.config['ethertype'],
                'vlan_tag': None,
                'frame_length': len(payload_bytes) + 18,  # +14 header +4 FCS
            }
            # Calculate FCS (CRC-32 simulation)
            fcs = self._calculate_fcs(payload_bytes)
            trailer = {
                'fcs': fcs,
                'padding_bytes': max(0, 46 - len(payload_bytes)),
            }
            self.log(f"Ethernet frame: {self.mac_address} -> {dest_mac}")
            self.log(f"EtherType: 0x{self.config['ethertype']}, FCS: {fcs}")

        return DataUnit(
            payload=data,  # Encapsulate the packet
            header=header,
            trailer=trailer,
            layer=self.LAYER_NUMBER,
            pdu_name=self.PDU_NAME
        )

    def decapsulate(self, data: DataUnit) -> DataUnit:
        """
        Decapsulate frame to extract packet.

        Validates:
        - FCS/CRC for error detection
        - MAC address filtering
        """
        self.log(f"Processing received {self.PDU_NAME.lower()}")

        header = data.header
        trailer = data.trailer

        # Verify FCS
        if 'fcs' in trailer:
            self.log(f"Verifying FCS: {trailer['fcs']}")
            # In real implementation, would recalculate and compare

        if self.protocol == "serial":
            self.log(f"HDLC frame received, sequence: {header.get('sequence', 'N/A')}")
        else:
            src_mac = header.get('source_mac', 'Unknown')
            dst_mac = header.get('destination_mac', 'Unknown')
            self.log(f"Ethernet frame: {src_mac} -> {dst_mac}")

            # Check if frame is for us (or broadcast)
            if dst_mac not in [self.mac_address, "FF:FF:FF:FF:FF:FF"]:
                self.log("Frame not addressed to us, discarding")

        # Extract the packet payload
        payload = data.payload
        if isinstance(payload, DataUnit):
            return payload
        else:
            return DataUnit(payload=payload, layer=3, pdu_name="Packet")

    def _calculate_crc(self, data: bytes) -> str:
        """Calculate CRC-16 for HDLC frames."""
        # Simplified CRC calculation using hash
        hash_val = hashlib.md5(data).hexdigest()[:4]
        return f"0x{hash_val.upper()}"

    def _calculate_fcs(self, data: bytes) -> str:
        """Calculate FCS (CRC-32) for Ethernet frames."""
        # Simplified FCS calculation
        hash_val = hashlib.md5(data).hexdigest()[:8]
        return f"0x{hash_val.upper()}"

    def get_mac_address(self) -> str:
        """Get the MAC address of this interface."""
        return self.mac_address

    def set_mac_address(self, mac: str):
        """Set a custom MAC address."""
        self.mac_address = mac

    def create_arp_frame(self, target_ip: str) -> DataUnit:
        """Create an ARP request frame (Ethernet only)."""
        if self.protocol != "ethernet":
            raise ValueError("ARP is only available for Ethernet")

        arp_payload = {
            'hardware_type': 1,  # Ethernet
            'protocol_type': '0x0800',  # IPv4
            'operation': 1,  # Request
            'sender_mac': self.mac_address,
            'sender_ip': '192.168.1.100',
            'target_mac': '00:00:00:00:00:00',
            'target_ip': target_ip,
        }

        header = {
            'destination_mac': 'FF:FF:FF:FF:FF:FF',
            'source_mac': self.mac_address,
            'ethertype': '0806',  # ARP
        }

        return DataUnit(
            payload=arp_payload,
            header=header,
            layer=self.LAYER_NUMBER,
            pdu_name="ARP Frame"
        )
