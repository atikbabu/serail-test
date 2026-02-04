"""
Base classes for OSI layer implementation.
"""

from dataclasses import dataclass, field
from typing import Any, Optional
from enum import IntEnum
import json


class LayerNumber(IntEnum):
    """OSI Layer numbers."""
    PHYSICAL = 1
    DATA_LINK = 2
    NETWORK = 3
    TRANSPORT = 4
    SESSION = 5
    PRESENTATION = 6
    APPLICATION = 7


@dataclass
class DataUnit:
    """
    Represents a Protocol Data Unit (PDU) at any OSI layer.

    Each layer has its own PDU name:
    - Layer 7 (Application): Data
    - Layer 6 (Presentation): Data
    - Layer 5 (Session): Data
    - Layer 4 (Transport): Segment/Datagram
    - Layer 3 (Network): Packet
    - Layer 2 (Data Link): Frame
    - Layer 1 (Physical): Bits
    """
    payload: Any
    header: dict = field(default_factory=dict)
    trailer: dict = field(default_factory=dict)
    layer: int = 0
    pdu_name: str = "Data"

    def to_bytes(self) -> bytes:
        """Convert PDU to bytes representation."""
        data = {
            'header': self.header,
            'payload': self.payload if isinstance(self.payload, (str, dict))
                       else str(self.payload),
            'trailer': self.trailer
        }
        return json.dumps(data).encode('utf-8')

    @classmethod
    def from_bytes(cls, data: bytes, layer: int = 0) -> 'DataUnit':
        """Create PDU from bytes."""
        parsed = json.loads(data.decode('utf-8'))
        return cls(
            payload=parsed.get('payload', ''),
            header=parsed.get('header', {}),
            trailer=parsed.get('trailer', {}),
            layer=layer
        )

    def get_size(self) -> int:
        """Get total size of PDU in bytes."""
        return len(self.to_bytes())

    def __str__(self) -> str:
        header_str = json.dumps(self.header) if self.header else "{}"
        trailer_str = json.dumps(self.trailer) if self.trailer else "{}"
        payload_str = str(self.payload)[:50] + "..." if len(str(self.payload)) > 50 else str(self.payload)
        return f"[{self.pdu_name}] Header: {header_str} | Payload: {payload_str} | Trailer: {trailer_str}"


class OSILayer:
    """
    Base class for OSI layer implementations.

    Each layer encapsulates data from the layer above (when sending)
    and decapsulates data for the layer above (when receiving).
    """

    LAYER_NUMBER: int = 0
    LAYER_NAME: str = "Base"
    PDU_NAME: str = "Data"

    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.stats = {
            'packets_sent': 0,
            'packets_received': 0,
            'bytes_sent': 0,
            'bytes_received': 0
        }

    def encapsulate(self, data: DataUnit) -> DataUnit:
        """
        Encapsulate data from upper layer by adding header/trailer.
        Override in subclasses to add layer-specific headers.
        """
        raise NotImplementedError("Subclasses must implement encapsulate()")

    def decapsulate(self, data: DataUnit) -> DataUnit:
        """
        Decapsulate data for upper layer by removing header/trailer.
        Override in subclasses to process layer-specific headers.
        """
        raise NotImplementedError("Subclasses must implement decapsulate()")

    def process_send(self, data: DataUnit) -> DataUnit:
        """Process data being sent down the stack."""
        self.stats['packets_sent'] += 1
        result = self.encapsulate(data)
        self.stats['bytes_sent'] += result.get_size()
        return result

    def process_receive(self, data: DataUnit) -> DataUnit:
        """Process data being received up the stack."""
        self.stats['packets_received'] += 1
        self.stats['bytes_received'] += data.get_size()
        return self.decapsulate(data)

    def log(self, message: str):
        """Log layer activity if verbose mode is enabled."""
        if self.verbose:
            print(f"  [Layer {self.LAYER_NUMBER} - {self.LAYER_NAME}] {message}")

    def get_layer_info(self) -> dict:
        """Get information about this layer."""
        return {
            'number': self.LAYER_NUMBER,
            'name': self.LAYER_NAME,
            'pdu_name': self.PDU_NAME,
            'stats': self.stats.copy()
        }

    def __str__(self) -> str:
        return f"Layer {self.LAYER_NUMBER}: {self.LAYER_NAME} ({self.PDU_NAME})"
