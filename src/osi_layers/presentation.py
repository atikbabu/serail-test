"""
Layer 6: Presentation Layer Implementation

The Presentation Layer is responsible for:
- Data translation: Converting between data formats
- Encryption/Decryption: Securing data for transmission
- Compression/Decompression: Reducing data size
- Character encoding: ASCII, EBCDIC, Unicode conversion

Key Functions:
- Format conversion (e.g., JPEG, GIF, MPEG)
- Data encryption (SSL/TLS at this layer conceptually)
- Data compression (gzip, deflate)
- Serialization (JSON, XML, Protocol Buffers)

Common Standards:
- MIME types
- SSL/TLS (encryption aspects)
- JPEG, PNG, GIF (image formats)
- ASCII, UTF-8, UTF-16 (text encoding)
"""

from .base import OSILayer, DataUnit
import json
import base64
import zlib
import hashlib


class PresentationLayer(OSILayer):
    """
    Presentation Layer - Handles data representation.

    This layer handles encoding, encryption, and compression
    of application data.
    """

    LAYER_NUMBER = 6
    LAYER_NAME = "Presentation"
    PDU_NAME = "Data"

    def __init__(self, verbose: bool = True):
        super().__init__(verbose)

        # Configuration
        self.config = {
            'encoding': 'utf-8',
            'encryption': None,  # None, 'xor', 'base64'
            'compression': None,  # None, 'zlib'
            'format': 'json',  # json, xml, binary
        }

        # Encryption key (simple XOR key for demonstration)
        self.encryption_key = b'SECRET_KEY_12345'

    def encapsulate(self, data: DataUnit) -> DataUnit:
        """
        Encapsulate application data with presentation formatting.

        Performs:
        - Serialization (to chosen format)
        - Compression (if enabled)
        - Encryption (if enabled)
        - Encoding
        """
        self.log(f"Processing {self.PDU_NAME.lower()} for presentation")

        # Get the raw application data
        app_data = data.payload if not isinstance(data.payload, DataUnit) else data.payload.payload

        # Step 1: Serialize the data
        serialized = self._serialize(app_data)
        self.log(f"Serialized to {self.config['format']}: {len(serialized)} bytes")

        # Step 2: Compress if enabled
        if self.config['compression']:
            serialized = self._compress(serialized)
            self.log(f"Compressed with {self.config['compression']}: {len(serialized)} bytes")

        # Step 3: Encrypt if enabled
        if self.config['encryption']:
            serialized = self._encrypt(serialized)
            self.log(f"Encrypted with {self.config['encryption']}")

        # Step 4: Encode
        encoded = self._encode(serialized)

        header = {
            'content_type': self._get_content_type(app_data),
            'encoding': self.config['encoding'],
            'compression': self.config['compression'],
            'encryption': self.config['encryption'],
            'format': self.config['format'],
            'original_size': len(str(app_data)),
            'processed_size': len(encoded),
            'checksum': self._calculate_checksum(encoded),
        }

        self.log(f"Content-Type: {header['content_type']}")
        self.log(f"Size: {header['original_size']} -> {header['processed_size']} bytes")

        return DataUnit(
            payload=encoded,
            header=header,
            layer=self.LAYER_NUMBER,
            pdu_name=self.PDU_NAME
        )

    def decapsulate(self, data: DataUnit) -> DataUnit:
        """
        Decapsulate presentation data to extract application data.

        Performs:
        - Decoding
        - Decryption (if needed)
        - Decompression (if needed)
        - Deserialization
        """
        self.log(f"Processing received {self.PDU_NAME.lower()}")

        header = data.header
        encoded_data = data.payload

        # Verify checksum
        if header.get('checksum'):
            calculated = self._calculate_checksum(encoded_data)
            if calculated == header['checksum']:
                self.log("Checksum verified")
            else:
                self.log("WARNING: Checksum mismatch!")

        self.log(f"Content-Type: {header.get('content_type', 'unknown')}")

        # Step 1: Decode
        decoded = self._decode(encoded_data)

        # Step 2: Decrypt if needed
        if header.get('encryption'):
            self.config['encryption'] = header['encryption']
            decoded = self._decrypt(decoded)
            self.log(f"Decrypted ({header['encryption']})")

        # Step 3: Decompress if needed
        if header.get('compression'):
            self.config['compression'] = header['compression']
            decoded = self._decompress(decoded)
            self.log(f"Decompressed ({header['compression']})")

        # Step 4: Deserialize
        self.config['format'] = header.get('format', 'json')
        app_data = self._deserialize(decoded)
        self.log(f"Deserialized from {self.config['format']}")

        return DataUnit(
            payload=app_data,
            header={'content_type': header.get('content_type')},
            layer=7,
            pdu_name="Data"
        )

    def _serialize(self, data) -> bytes:
        """Serialize data to chosen format."""
        if self.config['format'] == 'json':
            return json.dumps(data, default=str).encode(self.config['encoding'])
        elif self.config['format'] == 'xml':
            # Simple XML serialization
            xml = f'<?xml version="1.0"?><data>{data}</data>'
            return xml.encode(self.config['encoding'])
        else:  # binary
            return str(data).encode(self.config['encoding'])

    def _deserialize(self, data: bytes):
        """Deserialize data from chosen format."""
        try:
            if self.config['format'] == 'json':
                return json.loads(data.decode(self.config['encoding']))
            elif self.config['format'] == 'xml':
                # Simple XML extraction
                text = data.decode(self.config['encoding'])
                start = text.find('<data>') + 6
                end = text.find('</data>')
                return text[start:end] if start > 5 and end > start else text
            else:
                return data.decode(self.config['encoding'])
        except Exception:
            return data

    def _compress(self, data: bytes) -> bytes:
        """Compress data using configured algorithm."""
        if self.config['compression'] == 'zlib':
            return zlib.compress(data)
        return data

    def _decompress(self, data: bytes) -> bytes:
        """Decompress data using configured algorithm."""
        if self.config['compression'] == 'zlib':
            try:
                return zlib.decompress(data)
            except Exception:
                return data
        return data

    def _encrypt(self, data: bytes) -> bytes:
        """Encrypt data using configured method."""
        if self.config['encryption'] == 'xor':
            # Simple XOR encryption for demonstration
            key = self.encryption_key
            encrypted = bytes([data[i] ^ key[i % len(key)] for i in range(len(data))])
            return encrypted
        elif self.config['encryption'] == 'base64':
            # Base64 encoding (not real encryption, for demo)
            return base64.b64encode(data)
        return data

    def _decrypt(self, data: bytes) -> bytes:
        """Decrypt data using configured method."""
        if self.config['encryption'] == 'xor':
            # XOR is symmetric
            key = self.encryption_key
            decrypted = bytes([data[i] ^ key[i % len(key)] for i in range(len(data))])
            return decrypted
        elif self.config['encryption'] == 'base64':
            return base64.b64decode(data)
        return data

    def _encode(self, data: bytes) -> bytes:
        """Encode data for transmission."""
        return data

    def _decode(self, data) -> bytes:
        """Decode received data."""
        if isinstance(data, str):
            return data.encode(self.config['encoding'])
        return data

    def _get_content_type(self, data) -> str:
        """Determine content type based on data."""
        if isinstance(data, dict):
            return 'application/json'
        elif isinstance(data, (list, tuple)):
            return 'application/json'
        elif isinstance(data, bytes):
            return 'application/octet-stream'
        else:
            return 'text/plain'

    def _calculate_checksum(self, data) -> str:
        """Calculate MD5 checksum of data."""
        if isinstance(data, str):
            data = data.encode()
        return hashlib.md5(data).hexdigest()[:8]

    def set_encoding(self, encoding: str):
        """Set the character encoding."""
        self.config['encoding'] = encoding
        self.log(f"Encoding set to: {encoding}")

    def set_encryption(self, method: str, key: bytes = None):
        """
        Set encryption method.

        Methods: None, 'xor', 'base64'
        """
        self.config['encryption'] = method
        if key:
            self.encryption_key = key
        self.log(f"Encryption set to: {method or 'disabled'}")

    def set_compression(self, method: str):
        """
        Set compression method.

        Methods: None, 'zlib'
        """
        self.config['compression'] = method
        self.log(f"Compression set to: {method or 'disabled'}")

    def set_format(self, format_type: str):
        """
        Set serialization format.

        Formats: 'json', 'xml', 'binary'
        """
        self.config['format'] = format_type
        self.log(f"Format set to: {format_type}")

    def get_presentation_info(self) -> dict:
        """Get current presentation layer configuration."""
        return {
            'config': self.config.copy(),
            'supported_encodings': ['utf-8', 'ascii', 'latin-1'],
            'supported_formats': ['json', 'xml', 'binary'],
            'supported_compression': [None, 'zlib'],
            'supported_encryption': [None, 'xor', 'base64'],
        }
