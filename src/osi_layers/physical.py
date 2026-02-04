"""
Layer 1: Physical Layer Implementation

The Physical Layer is responsible for:
- Transmission and reception of raw bit streams over physical medium
- Defining electrical, mechanical, and procedural specifications
- Bit synchronization and encoding (NRZ, Manchester, etc.)
- Physical topology (bus, star, ring, mesh)
- Transmission modes (simplex, half-duplex, full-duplex)

For Serial Communication:
- RS-232, RS-485, UART signals
- Baud rate, data bits, parity, stop bits

For Ethernet:
- 10BASE-T, 100BASE-TX, 1000BASE-T
- Electrical signaling on copper or light on fiber
"""

from .base import OSILayer, DataUnit
import time


class PhysicalLayer(OSILayer):
    """
    Physical Layer - Handles raw bit transmission.

    This layer converts frames into electrical/optical signals
    for serial or ethernet transmission.
    """

    LAYER_NUMBER = 1
    LAYER_NAME = "Physical"
    PDU_NAME = "Bits"

    def __init__(self, medium_type: str = "ethernet", verbose: bool = True):
        super().__init__(verbose)
        self.medium_type = medium_type

        # Physical layer parameters
        if medium_type == "serial":
            self.config = {
                'baud_rate': 9600,
                'data_bits': 8,
                'parity': 'N',
                'stop_bits': 1,
                'encoding': 'NRZ',
                'voltage_high': 12.0,
                'voltage_low': -12.0,
            }
        else:  # ethernet
            self.config = {
                'standard': '100BASE-TX',
                'speed_mbps': 100,
                'encoding': '4B/5B + MLT-3',
                'cable_type': 'Cat5e UTP',
                'max_segment': 100,  # meters
            }

        self.signal_buffer = []

    def encapsulate(self, data: DataUnit) -> DataUnit:
        """
        Convert frame to bit stream for transmission.

        Physical layer adds:
        - Preamble (synchronization)
        - Start frame delimiter
        - Signal encoding information
        """
        self.log(f"Converting frame to {self.PDU_NAME.lower()}")

        # Get the raw bytes from the frame
        raw_bytes = data.to_bytes()

        # Convert to bit representation
        bits = self._bytes_to_bits(raw_bytes)

        # Add physical layer signaling
        if self.medium_type == "serial":
            # Serial: Add start/stop bits for each byte (UART framing)
            framed_bits = self._add_uart_framing(bits)
            preamble = "10101010"  # Sync pattern
        else:
            # Ethernet: Add preamble and SFD
            preamble = "10101010" * 7  # 7 bytes of preamble
            sfd = "10101011"  # Start Frame Delimiter
            framed_bits = preamble + sfd + bits

        header = {
            'medium': self.medium_type,
            'encoding': self.config.get('encoding'),
            'preamble_length': len(preamble),
            'total_bits': len(framed_bits),
            'signal_type': 'electrical' if self.medium_type != 'fiber' else 'optical',
        }

        if self.medium_type == "serial":
            header['baud_rate'] = self.config['baud_rate']
            header['uart_config'] = f"{self.config['data_bits']}{self.config['parity']}{self.config['stop_bits']}"
        else:
            header['speed_mbps'] = self.config['speed_mbps']
            header['standard'] = self.config['standard']

        self.log(f"Prepared {len(framed_bits)} bits for transmission")
        self.log(f"Medium: {self.medium_type}, Encoding: {self.config.get('encoding')}")

        return DataUnit(
            payload=framed_bits,
            header=header,
            layer=self.LAYER_NUMBER,
            pdu_name=self.PDU_NAME
        )

    def decapsulate(self, data: DataUnit) -> DataUnit:
        """
        Convert received bit stream back to frame.

        Physical layer removes:
        - Preamble and synchronization
        - Signal decoding
        """
        self.log(f"Receiving {self.PDU_NAME.lower()} from medium")

        bits = data.payload

        # Remove physical layer framing
        if self.medium_type == "serial":
            # Remove UART framing (start/stop bits)
            data_bits = self._remove_uart_framing(bits)
        else:
            # Remove Ethernet preamble (56 bits) and SFD (8 bits)
            data_bits = bits[64:] if len(bits) > 64 else bits

        # Convert bits back to bytes
        raw_bytes = self._bits_to_bytes(data_bits)

        self.log(f"Extracted {len(raw_bytes)} bytes from signal")

        # Reconstruct the frame
        try:
            frame = DataUnit.from_bytes(raw_bytes, layer=2)
            frame.pdu_name = "Frame"
        except Exception:
            frame = DataUnit(payload=raw_bytes, layer=2, pdu_name="Frame")

        return frame

    def _bytes_to_bits(self, data: bytes) -> str:
        """Convert bytes to binary string representation."""
        return ''.join(format(byte, '08b') for byte in data)

    def _bits_to_bytes(self, bits: str) -> bytes:
        """Convert binary string to bytes."""
        # Pad to multiple of 8
        padded = bits + '0' * (8 - len(bits) % 8) if len(bits) % 8 else bits
        bytes_list = [int(padded[i:i+8], 2) for i in range(0, len(padded), 8)]
        return bytes(bytes_list)

    def _add_uart_framing(self, bits: str) -> str:
        """Add UART start and stop bits to each byte."""
        framed = ""
        for i in range(0, len(bits), 8):
            byte_bits = bits[i:i+8]
            if len(byte_bits) == 8:
                # Start bit (0) + data bits + stop bit (1)
                framed += "0" + byte_bits + "1"
        return framed

    def _remove_uart_framing(self, bits: str) -> str:
        """Remove UART start and stop bits."""
        data = ""
        for i in range(0, len(bits), 10):
            frame = bits[i:i+10]
            if len(frame) >= 9:
                # Extract data bits (skip start bit, take 8 data bits)
                data += frame[1:9]
        return data

    def simulate_transmission(self, bits: str) -> dict:
        """
        Simulate physical transmission with timing information.

        Returns transmission statistics.
        """
        bit_count = len(bits)

        if self.medium_type == "serial":
            baud_rate = self.config['baud_rate']
            transmission_time = bit_count / baud_rate
            signal_type = "RS-232 voltage levels"
        else:
            speed_bps = self.config['speed_mbps'] * 1_000_000
            transmission_time = bit_count / speed_bps
            signal_type = self.config['encoding']

        return {
            'bits_transmitted': bit_count,
            'transmission_time_seconds': transmission_time,
            'signal_type': signal_type,
            'medium': self.medium_type,
        }

    def get_physical_config(self) -> dict:
        """Get current physical layer configuration."""
        return {
            'medium_type': self.medium_type,
            'config': self.config.copy()
        }
