"""
Serial Communication Demonstration

Demonstrates how data flows through all 7 OSI layers
for serial (RS-232/UART) communication.

Serial communication characteristics:
- Point-to-point connection
- Typically lower speeds (9600 - 115200 baud)
- Used in embedded systems, industrial control, etc.
- Protocols: RS-232, RS-485, UART
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

try:
    import serial
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False


class SerialCommunicationDemo:
    """
    Demonstrates serial communication through OSI layers.

    This class shows how data is encapsulated as it travels
    down the OSI stack for serial transmission, and decapsulated
    when received.
    """

    def __init__(self, verbose: bool = True):
        self.verbose = verbose

        # Initialize all layers for serial communication
        self.layers = {
            7: ApplicationLayer(protocol="SERIAL", verbose=verbose),
            6: PresentationLayer(verbose=verbose),
            5: SessionLayer(verbose=verbose),
            4: TransportLayer(protocol="TCP", verbose=verbose),
            3: NetworkLayer(ip_version=4, verbose=verbose),
            2: DataLinkLayer(protocol="serial", verbose=verbose),
            1: PhysicalLayer(medium_type="serial", verbose=verbose),
        }

        # Serial port configuration
        self.serial_config = {
            'port': '/dev/ttyUSB0',
            'baudrate': 9600,
            'bytesize': 8,
            'parity': 'N',
            'stopbits': 1,
            'timeout': 1.0,
        }

        self.serial_port = None

    def demonstrate_send(self, message: str) -> dict:
        """
        Demonstrate sending data through all OSI layers for serial communication.

        Shows the complete encapsulation process from Layer 7 to Layer 1.

        Args:
            message: The application data to send

        Returns:
            Dictionary containing data at each layer
        """
        print("\n" + "=" * 70)
        print("SERIAL COMMUNICATION - SENDING DATA THROUGH OSI LAYERS")
        print("=" * 70)

        layer_data = {}

        # Prepare application data for serial protocol (e.g., Modbus)
        app_data = {
            'protocol': 'MODBUS',
            'unit_id': 1,
            'function': 3,  # Read Holding Registers
            'address': 0,
            'quantity': 10,
            'data': message,
        }

        print(f"\n📤 Original Message: '{message}'")
        print(f"   Application Protocol: MODBUS (Serial)")
        print()

        # Layer 7: Application Layer
        print("-" * 70)
        print("LAYER 7 - APPLICATION LAYER (MODBUS Protocol)")
        print("-" * 70)
        current_data = self.layers[7].encapsulate(app_data)
        layer_data[7] = {
            'name': 'Application',
            'pdu': 'Data',
            'data': current_data,
            'description': 'Modbus request created with function code and registers',
        }
        self._print_layer_details(current_data)

        # Layer 6: Presentation Layer
        print("\n" + "-" * 70)
        print("LAYER 6 - PRESENTATION LAYER (Data Formatting)")
        print("-" * 70)
        # Configure for serial: compact binary format
        self.layers[6].set_format('json')
        current_data = self.layers[6].encapsulate(current_data)
        layer_data[6] = {
            'name': 'Presentation',
            'pdu': 'Data',
            'data': current_data,
            'description': 'Data serialized and encoded for transmission',
        }
        self._print_layer_details(current_data)

        # Layer 5: Session Layer
        print("\n" + "-" * 70)
        print("LAYER 5 - SESSION LAYER (Dialog Control)")
        print("-" * 70)
        current_data = self.layers[5].encapsulate(current_data)
        layer_data[5] = {
            'name': 'Session',
            'pdu': 'Data',
            'data': current_data,
            'description': 'Session ID and synchronization added',
        }
        self._print_layer_details(current_data)

        # Layer 4: Transport Layer
        print("\n" + "-" * 70)
        print("LAYER 4 - TRANSPORT LAYER (End-to-End)")
        print("-" * 70)
        print("   Note: For serial, simplified transport (no ports needed)")
        current_data = self.layers[4].encapsulate(current_data)
        layer_data[4] = {
            'name': 'Transport',
            'pdu': 'Segment',
            'data': current_data,
            'description': 'Sequence numbers for reliable delivery',
        }
        self._print_layer_details(current_data)

        # Layer 3: Network Layer
        print("\n" + "-" * 70)
        print("LAYER 3 - NETWORK LAYER (Addressing)")
        print("-" * 70)
        print("   Note: Point-to-point serial uses simplified addressing")
        current_data = self.layers[3].encapsulate(current_data)
        layer_data[3] = {
            'name': 'Network',
            'pdu': 'Packet',
            'data': current_data,
            'description': 'IP-like addressing for routable serial (PPP)',
        }
        self._print_layer_details(current_data)

        # Layer 2: Data Link Layer
        print("\n" + "-" * 70)
        print("LAYER 2 - DATA LINK LAYER (HDLC Framing)")
        print("-" * 70)
        current_data = self.layers[2].encapsulate(current_data)
        layer_data[2] = {
            'name': 'Data Link',
            'pdu': 'Frame',
            'data': current_data,
            'description': 'HDLC frame with flags, address, control, and FCS',
        }
        self._print_layer_details(current_data)

        # Layer 1: Physical Layer
        print("\n" + "-" * 70)
        print("LAYER 1 - PHYSICAL LAYER (RS-232 Signals)")
        print("-" * 70)
        current_data = self.layers[1].encapsulate(current_data)
        layer_data[1] = {
            'name': 'Physical',
            'pdu': 'Bits',
            'data': current_data,
            'description': 'UART framing with start/stop bits, voltage signals',
        }
        self._print_layer_details(current_data)

        # Physical transmission statistics
        print("\n" + "=" * 70)
        print("PHYSICAL TRANSMISSION (RS-232)")
        print("=" * 70)
        bits = current_data.payload
        stats = self.layers[1].simulate_transmission(bits)
        print(f"   Bits to transmit: {stats['bits_transmitted']}")
        print(f"   Transmission time: {stats['transmission_time_seconds']*1000:.2f} ms")
        print(f"   Baud rate: {self.serial_config['baudrate']}")
        print(f"   Signal: RS-232 voltage levels (+12V/-12V)")
        print(f"   UART Config: {self.serial_config['bytesize']}{self.serial_config['parity']}{self.serial_config['stopbits']}")

        return layer_data

    def demonstrate_receive(self, bits: str) -> dict:
        """
        Demonstrate receiving data through all OSI layers.

        Shows the complete decapsulation process from Layer 1 to Layer 7.

        Args:
            bits: The received bit stream

        Returns:
            Dictionary containing data at each layer
        """
        print("\n" + "=" * 70)
        print("SERIAL COMMUNICATION - RECEIVING DATA THROUGH OSI LAYERS")
        print("=" * 70)

        layer_data = {}

        # Create initial physical layer data unit
        current_data = DataUnit(
            payload=bits,
            header={'medium': 'serial', 'encoding': 'NRZ'},
            layer=1,
            pdu_name="Bits"
        )

        print(f"\n📥 Received {len(bits)} bits from RS-232 interface")
        print()

        # Layer 1 -> 2: Physical to Data Link
        print("-" * 70)
        print("LAYER 1 -> 2: Physical to Data Link")
        print("-" * 70)
        current_data = self.layers[1].decapsulate(current_data)
        layer_data[1] = {'processed': current_data}
        self._print_layer_details(current_data)

        # Continue decapsulation up the stack...
        for layer_num in range(2, 7):
            print(f"\n" + "-" * 70)
            print(f"LAYER {layer_num} -> {layer_num + 1}: "
                  f"{self.layers[layer_num].LAYER_NAME} to {self.layers[layer_num + 1].LAYER_NAME}")
            print("-" * 70)
            current_data = self.layers[layer_num].decapsulate(current_data)
            layer_data[layer_num] = {'processed': current_data}
            self._print_layer_details(current_data)

        # Final application data
        print("\n" + "-" * 70)
        print("LAYER 7: Application Layer - Final Data")
        print("-" * 70)
        final_data = self.layers[7].decapsulate(current_data)
        layer_data[7] = {'processed': final_data}
        print(f"   📨 Received Application Data: {final_data}")

        return layer_data

    def _print_layer_details(self, data: DataUnit):
        """Print details about data at current layer."""
        print(f"   PDU Type: {data.pdu_name}")
        print(f"   Header: {data.header}")
        if data.trailer:
            print(f"   Trailer: {data.trailer}")

        # Show payload summary
        payload = data.payload
        if isinstance(payload, DataUnit):
            print(f"   Payload: [Encapsulated {payload.pdu_name}]")
        elif isinstance(payload, str) and len(payload) > 100:
            print(f"   Payload: {payload[:100]}... ({len(payload)} chars)")
        else:
            print(f"   Payload: {payload}")

        print(f"   Size: {data.get_size()} bytes")

    def get_serial_layer_summary(self) -> list:
        """Get a summary of all layers for serial communication."""
        return [
            {
                'layer': 7,
                'name': 'Application',
                'serial_protocol': 'Modbus RTU / Custom',
                'function': 'Industrial control commands, sensor data',
                'pdu': 'Data',
            },
            {
                'layer': 6,
                'name': 'Presentation',
                'serial_protocol': 'Binary/ASCII encoding',
                'function': 'Data format conversion, simple encoding',
                'pdu': 'Data',
            },
            {
                'layer': 5,
                'name': 'Session',
                'serial_protocol': 'Transaction IDs',
                'function': 'Request-response matching',
                'pdu': 'Data',
            },
            {
                'layer': 4,
                'name': 'Transport',
                'serial_protocol': 'Simplified/None',
                'function': 'Basic sequencing (if any)',
                'pdu': 'Segment',
            },
            {
                'layer': 3,
                'name': 'Network',
                'serial_protocol': 'PPP/SLIP (if IP)',
                'function': 'Device addressing (unit IDs)',
                'pdu': 'Packet',
            },
            {
                'layer': 2,
                'name': 'Data Link',
                'serial_protocol': 'HDLC/PPP',
                'function': 'Framing, error detection (CRC)',
                'pdu': 'Frame',
            },
            {
                'layer': 1,
                'name': 'Physical',
                'serial_protocol': 'RS-232/RS-485/UART',
                'function': 'Voltage signaling, bit timing',
                'pdu': 'Bits',
            },
        ]

    def connect_serial_port(self, port: str = None, baudrate: int = None) -> bool:
        """
        Connect to a real serial port (if available).

        Args:
            port: Serial port path (e.g., '/dev/ttyUSB0', 'COM3')
            baudrate: Baud rate for communication

        Returns:
            True if connected successfully
        """
        if not SERIAL_AVAILABLE:
            print("⚠️  PySerial not installed. Run: pip install pyserial")
            return False

        if port:
            self.serial_config['port'] = port
        if baudrate:
            self.serial_config['baudrate'] = baudrate

        try:
            self.serial_port = serial.Serial(
                port=self.serial_config['port'],
                baudrate=self.serial_config['baudrate'],
                bytesize=self.serial_config['bytesize'],
                parity=self.serial_config['parity'],
                stopbits=self.serial_config['stopbits'],
                timeout=self.serial_config['timeout'],
            )
            print(f"✅ Connected to {self.serial_config['port']} at {self.serial_config['baudrate']} baud")
            return True
        except Exception as e:
            print(f"❌ Failed to connect: {e}")
            return False

    def disconnect_serial_port(self):
        """Disconnect from serial port."""
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
            print("Disconnected from serial port")

    def send_real_data(self, data: bytes) -> bool:
        """
        Send data over real serial port.

        Args:
            data: Bytes to send

        Returns:
            True if sent successfully
        """
        if not self.serial_port or not self.serial_port.is_open:
            print("Serial port not connected")
            return False

        try:
            self.serial_port.write(data)
            self.serial_port.flush()
            return True
        except Exception as e:
            print(f"Error sending data: {e}")
            return False

    def receive_real_data(self, num_bytes: int = 1024) -> bytes:
        """
        Receive data from real serial port.

        Args:
            num_bytes: Maximum bytes to read

        Returns:
            Received bytes
        """
        if not self.serial_port or not self.serial_port.is_open:
            print("Serial port not connected")
            return b''

        try:
            return self.serial_port.read(num_bytes)
        except Exception as e:
            print(f"Error receiving data: {e}")
            return b''
