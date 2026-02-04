"""
Layer 7: Application Layer Implementation

The Application Layer is responsible for:
- Providing network services directly to end-user applications
- Application protocols: HTTP, FTP, SMTP, DNS, etc.
- User authentication and authorization
- Quality of service
- Resource sharing

Key Protocols:
- HTTP/HTTPS: Web browsing
- FTP/SFTP: File transfer
- SMTP/POP3/IMAP: Email
- DNS: Domain name resolution
- DHCP: IP address assignment
- SSH/Telnet: Remote access
- SNMP: Network management

For Serial Communication:
- Custom application protocols
- Modbus, DNP3 (industrial protocols)

For Ethernet:
- Full range of TCP/IP application protocols
"""

from .base import OSILayer, DataUnit
import random
from datetime import datetime


class ApplicationLayer(OSILayer):
    """
    Application Layer - Provides network services to applications.

    This layer implements application-level protocols like HTTP,
    FTP, SMTP, and custom protocols for serial communication.
    """

    LAYER_NUMBER = 7
    LAYER_NAME = "Application"
    PDU_NAME = "Data"

    def __init__(self, protocol: str = "HTTP", verbose: bool = True):
        super().__init__(verbose)
        self.protocol = protocol.upper()

        # Protocol-specific configurations
        self.protocol_configs = {
            'HTTP': {
                'version': '1.1',
                'default_port': 80,
                'methods': ['GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'OPTIONS'],
            },
            'FTP': {
                'version': '1.0',
                'control_port': 21,
                'data_port': 20,
                'modes': ['active', 'passive'],
            },
            'SMTP': {
                'version': '1.0',
                'default_port': 25,
                'commands': ['HELO', 'MAIL', 'RCPT', 'DATA', 'QUIT'],
            },
            'DNS': {
                'version': '1.0',
                'default_port': 53,
                'record_types': ['A', 'AAAA', 'CNAME', 'MX', 'NS', 'TXT'],
            },
            'SERIAL': {
                'version': '1.0',
                'protocols': ['MODBUS', 'DNP3', 'CUSTOM'],
            },
        }

        self.config = self.protocol_configs.get(
            self.protocol,
            {'version': '1.0', 'default_port': 0}
        )

    def encapsulate(self, data: any) -> DataUnit:
        """
        Encapsulate user data with application protocol headers.

        This is the entry point for data entering the OSI stack.
        """
        self.log(f"Creating {self.protocol} application {self.PDU_NAME.lower()}")

        if self.protocol == "HTTP":
            header = self._create_http_header(data)
        elif self.protocol == "FTP":
            header = self._create_ftp_header(data)
        elif self.protocol == "SMTP":
            header = self._create_smtp_header(data)
        elif self.protocol == "DNS":
            header = self._create_dns_header(data)
        elif self.protocol == "SERIAL":
            header = self._create_serial_header(data)
        else:
            header = self._create_generic_header(data)

        self.log(f"Protocol: {self.protocol}")
        self.log(f"Port: {header.get('destination_port', 'N/A')}")

        return DataUnit(
            payload=data,
            header=header,
            layer=self.LAYER_NUMBER,
            pdu_name=self.PDU_NAME
        )

    def decapsulate(self, data: DataUnit) -> any:
        """
        Decapsulate application data for the user/application.

        This is the exit point for data leaving the OSI stack.
        """
        self.log(f"Processing received {self.protocol} {self.PDU_NAME.lower()}")

        header = data.header
        protocol = header.get('protocol', self.protocol)

        self.log(f"Protocol: {protocol}")

        if protocol == "HTTP":
            self._process_http_response(header)
        elif protocol == "DNS":
            self._process_dns_response(header)

        # Return the actual application payload
        payload = data.payload
        if isinstance(payload, DataUnit):
            return payload.payload
        return payload

    def _create_http_header(self, data) -> dict:
        """Create HTTP request/response header."""
        if isinstance(data, dict) and 'method' in data:
            # HTTP Request
            return {
                'protocol': 'HTTP',
                'version': self.config['version'],
                'method': data.get('method', 'GET'),
                'path': data.get('path', '/'),
                'host': data.get('host', 'localhost'),
                'headers': {
                    'User-Agent': 'OSI-Demo/1.0',
                    'Accept': '*/*',
                    'Connection': 'keep-alive',
                    'Content-Type': data.get('content_type', 'text/plain'),
                },
                'destination_port': data.get('port', 80),
                'source_port': random.randint(49152, 65535),
            }
        else:
            # Simple HTTP GET request
            return {
                'protocol': 'HTTP',
                'version': self.config['version'],
                'method': 'GET',
                'path': '/',
                'host': 'localhost',
                'headers': {
                    'User-Agent': 'OSI-Demo/1.0',
                    'Accept': '*/*',
                },
                'destination_port': 80,
                'source_port': random.randint(49152, 65535),
            }

    def _create_ftp_header(self, data) -> dict:
        """Create FTP command header."""
        command = data.get('command', 'LIST') if isinstance(data, dict) else 'LIST'
        return {
            'protocol': 'FTP',
            'version': self.config['version'],
            'command': command,
            'argument': data.get('argument', '') if isinstance(data, dict) else str(data),
            'mode': 'passive',
            'destination_port': 21,
            'source_port': random.randint(49152, 65535),
        }

    def _create_smtp_header(self, data) -> dict:
        """Create SMTP command header."""
        if isinstance(data, dict):
            return {
                'protocol': 'SMTP',
                'version': self.config['version'],
                'command': data.get('command', 'DATA'),
                'from': data.get('from', 'sender@example.com'),
                'to': data.get('to', 'recipient@example.com'),
                'subject': data.get('subject', 'Test Email'),
                'destination_port': 25,
                'source_port': random.randint(49152, 65535),
            }
        else:
            return {
                'protocol': 'SMTP',
                'version': self.config['version'],
                'command': 'DATA',
                'destination_port': 25,
                'source_port': random.randint(49152, 65535),
            }

    def _create_dns_header(self, data) -> dict:
        """Create DNS query header."""
        query_name = data.get('query', 'example.com') if isinstance(data, dict) else str(data)
        query_type = data.get('type', 'A') if isinstance(data, dict) else 'A'
        return {
            'protocol': 'DNS',
            'version': self.config['version'],
            'transaction_id': random.randint(0, 65535),
            'flags': {
                'qr': 0,  # Query
                'opcode': 0,  # Standard query
                'rd': 1,  # Recursion desired
            },
            'questions': 1,
            'query_name': query_name,
            'query_type': query_type,
            'query_class': 'IN',
            'destination_port': 53,
            'source_port': random.randint(49152, 65535),
        }

    def _create_serial_header(self, data) -> dict:
        """Create serial protocol header (e.g., Modbus)."""
        if isinstance(data, dict):
            sub_protocol = data.get('protocol', 'MODBUS')
        else:
            sub_protocol = 'CUSTOM'

        if sub_protocol == 'MODBUS':
            return {
                'protocol': 'SERIAL',
                'sub_protocol': 'MODBUS',
                'transaction_id': random.randint(0, 65535),
                'unit_id': data.get('unit_id', 1) if isinstance(data, dict) else 1,
                'function_code': data.get('function', 3) if isinstance(data, dict) else 3,
                'starting_address': data.get('address', 0) if isinstance(data, dict) else 0,
                'quantity': data.get('quantity', 1) if isinstance(data, dict) else 1,
            }
        else:
            return {
                'protocol': 'SERIAL',
                'sub_protocol': 'CUSTOM',
                'sequence': random.randint(0, 255),
                'command': data.get('command', 'READ') if isinstance(data, dict) else 'DATA',
                'timestamp': datetime.now().isoformat(),
            }

    def _create_generic_header(self, data) -> dict:
        """Create generic application header."""
        return {
            'protocol': self.protocol,
            'version': '1.0',
            'timestamp': datetime.now().isoformat(),
            'data_type': type(data).__name__,
            'destination_port': self.config.get('default_port', 0),
            'source_port': random.randint(49152, 65535),
        }

    def _process_http_response(self, header: dict):
        """Process HTTP response header."""
        status = header.get('status_code', 200)
        self.log(f"HTTP Status: {status}")

    def _process_dns_response(self, header: dict):
        """Process DNS response header."""
        if header.get('answers'):
            for answer in header['answers']:
                self.log(f"DNS Answer: {answer}")

    def create_http_request(self, method: str, path: str, host: str,
                           body: str = None, headers: dict = None) -> DataUnit:
        """Create a complete HTTP request."""
        request_data = {
            'method': method.upper(),
            'path': path,
            'host': host,
            'body': body,
            'headers': headers or {},
        }
        return self.encapsulate(request_data)

    def create_http_response(self, status_code: int, body: str,
                            content_type: str = 'text/html') -> DataUnit:
        """Create an HTTP response."""
        header = {
            'protocol': 'HTTP',
            'version': '1.1',
            'status_code': status_code,
            'status_text': self._get_status_text(status_code),
            'headers': {
                'Content-Type': content_type,
                'Content-Length': len(body),
                'Server': 'OSI-Demo/1.0',
                'Date': datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT'),
            },
        }
        return DataUnit(payload=body, header=header, layer=7, pdu_name="HTTP Response")

    def _get_status_text(self, code: int) -> str:
        """Get HTTP status text for code."""
        status_texts = {
            200: 'OK',
            201: 'Created',
            204: 'No Content',
            301: 'Moved Permanently',
            302: 'Found',
            400: 'Bad Request',
            401: 'Unauthorized',
            403: 'Forbidden',
            404: 'Not Found',
            500: 'Internal Server Error',
        }
        return status_texts.get(code, 'Unknown')

    def create_dns_query(self, domain: str, query_type: str = 'A') -> DataUnit:
        """Create a DNS query."""
        query_data = {
            'query': domain,
            'type': query_type,
        }
        return self.encapsulate(query_data)

    def set_protocol(self, protocol: str):
        """Change the application protocol."""
        self.protocol = protocol.upper()
        self.config = self.protocol_configs.get(
            self.protocol,
            {'version': '1.0', 'default_port': 0}
        )
        self.log(f"Protocol changed to: {self.protocol}")

    def get_protocol_info(self) -> dict:
        """Get information about current protocol."""
        return {
            'protocol': self.protocol,
            'config': self.config.copy(),
            'available_protocols': list(self.protocol_configs.keys()),
        }
