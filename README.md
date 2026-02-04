# OSI Model Communication Demonstration

A comprehensive Python application demonstrating **Serial** and **Ethernet** communication through all 7 layers of the OSI (Open Systems Interconnection) model.

## Overview

This educational application shows how data is encapsulated and decapsulated as it travels through each OSI layer:

| Layer | Name         | Serial Protocol     | Ethernet Protocol     | PDU      |
|-------|--------------|--------------------|-----------------------|----------|
| 7     | Application  | Modbus, Custom     | HTTP, FTP, DNS        | Data     |
| 6     | Presentation | Binary encoding    | TLS/SSL, MIME         | Data     |
| 5     | Session      | Transaction IDs    | NetBIOS, RPC          | Data     |
| 4     | Transport    | Simplified         | TCP, UDP              | Segment  |
| 3     | Network      | PPP/SLIP           | IPv4, IPv6, ICMP      | Packet   |
| 2     | Data Link    | HDLC               | IEEE 802.3            | Frame    |
| 1     | Physical     | RS-232, RS-485     | 100BASE-TX            | Bits     |

## Features

- **Interactive CLI** with menu-driven interface
- **Serial Communication Demo** - Shows data flow through Modbus/HDLC protocols
- **Ethernet Communication Demo** - Shows data flow through TCP/IP stack
- **TCP Handshake Visualization** - Three-way handshake demonstration
- **ARP Resolution Demo** - Address resolution process
- **DNS Query Demo** - Domain name resolution
- **Visual Diagrams** - ASCII art showing encapsulation and frame structures
- **Side-by-side Comparison** - Serial vs Ethernet at each layer

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd serail-test

# Install dependencies
pip install -r requirements.txt
```

### Dependencies

- **pyserial** (>=3.5) - For real serial port communication
- **colorama** (>=0.4.6) - Colored terminal output
- **tabulate** (>=0.9.0) - Table formatting

## Usage

### Interactive Mode (Default)

```bash
python -m src.main
```

This opens an interactive menu with options to:
1. View OSI Model overview
2. Run Serial communication demo
3. Run Ethernet communication demo
4. Compare Serial vs Ethernet
5. View TCP handshake
6. View ARP resolution
7. View DNS query process
8. Show encapsulation diagrams
9. Show frame structures

### Command Line Options

```bash
# Serial demo only
python -m src.main --mode serial

# Ethernet demo only
python -m src.main --mode ethernet

# Comparison mode
python -m src.main --mode compare

# Custom message
python -m src.main --mode ethernet --message "Hello World"

# Quiet mode (less verbose)
python -m src.main --mode serial --quiet
```

## Project Structure

```
serail-test/
├── CLAUDE.md              # AI assistant guidelines
├── README.md              # This file
├── requirements.txt       # Python dependencies
├── src/
│   ├── __init__.py
│   ├── main.py            # Main application entry point
│   ├── osi_layers/        # OSI layer implementations
│   │   ├── __init__.py
│   │   ├── base.py        # Base classes (OSILayer, DataUnit)
│   │   ├── physical.py    # Layer 1: Physical
│   │   ├── data_link.py   # Layer 2: Data Link
│   │   ├── network.py     # Layer 3: Network
│   │   ├── transport.py   # Layer 4: Transport
│   │   ├── session.py     # Layer 5: Session
│   │   ├── presentation.py# Layer 6: Presentation
│   │   └── application.py # Layer 7: Application
│   ├── serial_comm/       # Serial communication demo
│   │   ├── __init__.py
│   │   └── serial_demo.py
│   ├── ethernet_comm/     # Ethernet communication demo
│   │   ├── __init__.py
│   │   └── ethernet_demo.py
│   └── utils/             # Utilities
│       ├── __init__.py
│       └── visualizer.py  # ASCII visualization
└── tests/
    ├── __init__.py
    └── test_osi_layers.py # Unit tests
```

## Example Output

### Ethernet Encapsulation

```
Layer 7 (Application): Data
   [         Application Data          ]
   └─ Original user data

Layer 4 (Transport): Segment
   [H4][H5][H6][   Application Data    ]
   └─ Add: Port numbers, seq/ack (TCP)

Layer 3 (Network): Packet
   [H3][H4][H5][H6][ Application Data  ]
   └─ Add: IP addresses, TTL

Layer 2 (Data Link): Frame
   [H2][H3][H4][H5][H6][App Data][T2]
   └─ Add: MAC addresses, FCS

Layer 1 (Physical): Bits
   10101010[H2][H3][H4][H5][H6][App Data][T2]1010
   └─ Add: Preamble, convert to bits
```

## Running Tests

```bash
python -m pytest tests/ -v
```

Or using unittest:

```bash
python -m unittest discover -s tests -v
```

## API Usage

You can also use the library programmatically:

```python
from src.serial_comm import SerialCommunicationDemo
from src.ethernet_comm import EthernetCommunicationDemo

# Serial demo
serial_demo = SerialCommunicationDemo(verbose=True)
serial_demo.demonstrate_send("Hello Serial!")

# Ethernet demo
ethernet_demo = EthernetCommunicationDemo(verbose=True)
ethernet_demo.demonstrate_send("Hello Ethernet!", dest_ip="192.168.1.1", dest_port=80)

# TCP handshake
ethernet_demo.demonstrate_tcp_handshake()

# ARP resolution
ethernet_demo.demonstrate_arp_resolution("192.168.1.100")

# DNS query
ethernet_demo.demonstrate_dns_query("example.com")
```

## Educational Purpose

This application is designed for:
- **Students** learning about networking and the OSI model
- **Developers** wanting to understand protocol stack internals
- **Educators** demonstrating network concepts
- **Engineers** reviewing serial vs ethernet communication differences

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
