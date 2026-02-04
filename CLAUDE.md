# CLAUDE.md - AI Assistant Guidelines

This file provides guidance for AI assistants working with this codebase.

## Repository Overview

**Repository:** serail-test
**Owner:** atikbabu
**Language:** Python 3.8+
**Purpose:** Educational demonstration of Serial and Ethernet communication through all 7 OSI model layers

This application demonstrates how data is encapsulated/decapsulated as it travels through the OSI (Open Systems Interconnection) model, comparing Serial (RS-232/HDLC) and Ethernet (IEEE 802.3/TCP-IP) communication.

## Project Structure

```
serail-test/
├── CLAUDE.md              # AI assistant guidelines (this file)
├── README.md              # User documentation
├── requirements.txt       # Python dependencies
├── src/
│   ├── __init__.py        # Package init with version info
│   ├── main.py            # CLI entry point with interactive menu
│   ├── osi_layers/        # OSI layer implementations
│   │   ├── __init__.py    # Layer exports
│   │   ├── base.py        # Base classes: OSILayer, DataUnit
│   │   ├── physical.py    # Layer 1: RS-232/Ethernet signals
│   │   ├── data_link.py   # Layer 2: HDLC/IEEE 802.3 framing
│   │   ├── network.py     # Layer 3: IP addressing & routing
│   │   ├── transport.py   # Layer 4: TCP/UDP segments
│   │   ├── session.py     # Layer 5: Session management
│   │   ├── presentation.py# Layer 6: Encoding/encryption
│   │   └── application.py # Layer 7: HTTP/Modbus protocols
│   ├── serial_comm/       # Serial communication demo
│   │   ├── __init__.py
│   │   └── serial_demo.py # SerialCommunicationDemo class
│   ├── ethernet_comm/     # Ethernet communication demo
│   │   ├── __init__.py
│   │   └── ethernet_demo.py # EthernetCommunicationDemo class
│   └── utils/             # Utility modules
│       ├── __init__.py
│       └── visualizer.py  # OSIVisualizer for ASCII diagrams
└── tests/
    ├── __init__.py
    └── test_osi_layers.py # Unit tests for all layers
```

## Key Components

### OSI Layer Classes (`src/osi_layers/`)

Each layer inherits from `OSILayer` base class and implements:
- `encapsulate(data: DataUnit) -> DataUnit` - Add headers/trailers going down the stack
- `decapsulate(data: DataUnit) -> DataUnit` - Remove headers going up the stack

**DataUnit** is the core data structure representing PDUs (Protocol Data Units) at each layer.

### Communication Demos

- **SerialCommunicationDemo** (`src/serial_comm/serial_demo.py`)
  - Demonstrates Modbus/HDLC protocols
  - RS-232 physical layer simulation
  - Optional real serial port connection via PySerial

- **EthernetCommunicationDemo** (`src/ethernet_comm/ethernet_demo.py`)
  - Demonstrates HTTP/TCP/IP protocols
  - TCP three-way handshake simulation
  - ARP and DNS query demonstrations

### Visualizer (`src/utils/visualizer.py`)

Provides ASCII art visualizations:
- OSI model diagram
- Encapsulation process
- Frame structures (Ethernet/HDLC)
- TCP handshake diagram

## Development Guidelines

### Code Conventions

1. **Python Style**
   - Follow PEP 8 guidelines
   - Use 4-space indentation
   - Use type hints where applicable
   - Document classes and public methods with docstrings

2. **Naming Conventions**
   - Classes: `PascalCase` (e.g., `DataLinkLayer`)
   - Functions/methods: `snake_case` (e.g., `encapsulate`)
   - Constants: `UPPER_SNAKE_CASE` (e.g., `LAYER_NUMBER`)
   - Private methods: `_leading_underscore`

3. **File Organization**
   - One main class per file
   - Related utilities grouped in `utils/`
   - Tests mirror source structure

### OSI Layer Implementation Pattern

When modifying or adding OSI layer functionality:

```python
class NewLayer(OSILayer):
    LAYER_NUMBER = N
    LAYER_NAME = "LayerName"
    PDU_NAME = "PDUName"

    def encapsulate(self, data: DataUnit) -> DataUnit:
        # Add layer-specific header
        header = {...}
        self.log(f"Processing {self.PDU_NAME}")
        return DataUnit(
            payload=data,
            header=header,
            layer=self.LAYER_NUMBER,
            pdu_name=self.PDU_NAME
        )

    def decapsulate(self, data: DataUnit) -> DataUnit:
        # Extract and process header
        # Return payload for upper layer
        return data.payload
```

### Git Workflow

1. **Branch Naming**
   - Feature: `feature/<description>`
   - Bug fix: `fix/<description>`
   - AI branches: `claude/<session-identifier>`

2. **Commit Messages**
   - Start with verb: Add, Fix, Update, Remove, Refactor
   - Keep first line under 72 characters
   - Reference issues when applicable

## Common Tasks

### Running the Application

```bash
# Interactive mode (default)
python -m src.main

# Serial demo only
python -m src.main --mode serial

# Ethernet demo only
python -m src.main --mode ethernet

# Comparison mode
python -m src.main --mode compare

# With custom message
python -m src.main --mode ethernet --message "Hello"
```

### Running Tests

```bash
# Using pytest
python -m pytest tests/ -v

# Using unittest
python -m unittest discover -s tests -v

# Run specific test
python -m pytest tests/test_osi_layers.py::TestPhysicalLayer -v
```

### Installing Dependencies

```bash
pip install -r requirements.txt
```

### Adding a New Protocol

1. Identify which layer the protocol operates at
2. Add protocol logic to the appropriate layer class
3. Add configuration to `protocol_configs` if in Application layer
4. Update tests in `tests/test_osi_layers.py`
5. Document in README.md

## Dependencies

| Package   | Version | Purpose                    |
|-----------|---------|----------------------------|
| pyserial  | >=3.5   | Real serial port access    |
| colorama  | >=0.4.6 | Colored terminal output    |
| tabulate  | >=0.9.0 | Table formatting           |

## AI Assistant Instructions

### When Working on This Codebase

1. **Understand the OSI model** - Each layer has specific responsibilities
2. **Maintain encapsulation pattern** - Data flows down (encapsulate) and up (decapsulate)
3. **Keep demonstrations educational** - Verbose logging helps users understand
4. **Test layer interactions** - Changes may affect multiple layers

### Important Files to Review First

1. `src/osi_layers/base.py` - Core classes and patterns
2. `src/main.py` - Entry point and CLI structure
3. `tests/test_osi_layers.py` - Expected behavior

### Things to Avoid

- Breaking the encapsulation/decapsulation symmetry
- Removing educational logging without reason
- Adding real network operations without user confirmation
- Committing credentials or sensitive data

### Testing Changes

Always run the full test suite after modifications:
```bash
python -m pytest tests/ -v
```

Verify interactive mode still works:
```bash
python -m src.main --mode serial --quiet
python -m src.main --mode ethernet --quiet
```

## Architecture Notes

### Data Flow (Sending)

```
Application Data
       ↓
[Layer 7] Add HTTP/Modbus headers
       ↓
[Layer 6] Encode/encrypt/compress
       ↓
[Layer 5] Add session ID
       ↓
[Layer 4] Add TCP/UDP ports, seq numbers
       ↓
[Layer 3] Add IP addresses
       ↓
[Layer 2] Add MAC addresses, FCS
       ↓
[Layer 1] Convert to bits, add preamble
       ↓
Physical Medium (Wire/Radio)
```

### Key Design Decisions

1. **DataUnit wrapping** - Each layer wraps the previous layer's DataUnit as its payload, preserving the full encapsulation chain
2. **Simulation focus** - This is educational, not production networking code
3. **Protocol flexibility** - Easy to add new protocols at any layer
4. **Verbose by default** - Users can see exactly what happens at each layer

---

*Last updated: 2026-02-04*
