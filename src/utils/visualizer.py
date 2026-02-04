"""
OSI Layer Visualization Utilities

Provides visual representations of data flow through OSI layers.
"""

try:
    from colorama import init, Fore, Back, Style
    init(autoreset=True)
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False
    # Fallback - no colors
    class Fore:
        RED = GREEN = YELLOW = BLUE = MAGENTA = CYAN = WHITE = RESET = ''
    class Back:
        RED = GREEN = YELLOW = BLUE = MAGENTA = CYAN = WHITE = RESET = ''
    class Style:
        BRIGHT = DIM = RESET_ALL = ''


class OSIVisualizer:
    """
    Visualizes OSI layer data and encapsulation process.
    """

    # Layer colors for visualization
    LAYER_COLORS = {
        7: Fore.RED,
        6: Fore.YELLOW,
        5: Fore.GREEN,
        4: Fore.CYAN,
        3: Fore.BLUE,
        2: Fore.MAGENTA,
        1: Fore.WHITE,
    }

    LAYER_NAMES = {
        7: 'Application',
        6: 'Presentation',
        5: 'Session',
        4: 'Transport',
        3: 'Network',
        2: 'Data Link',
        1: 'Physical',
    }

    PDU_NAMES = {
        7: 'Data',
        6: 'Data',
        5: 'Data',
        4: 'Segment',
        3: 'Packet',
        2: 'Frame',
        1: 'Bits',
    }

    def __init__(self):
        self.use_colors = COLORAMA_AVAILABLE

    def print_osi_model(self):
        """Print a visual representation of the OSI model."""
        print("\n" + "=" * 60)
        print("              OSI REFERENCE MODEL")
        print("=" * 60)
        print()

        for layer in range(7, 0, -1):
            color = self.LAYER_COLORS[layer]
            name = self.LAYER_NAMES[layer]
            pdu = self.PDU_NAMES[layer]

            print(f"{color}┌{'─' * 56}┐{Style.RESET_ALL}")
            print(f"{color}│ Layer {layer}: {name:20} │ PDU: {pdu:15} │{Style.RESET_ALL}")
            print(f"{color}└{'─' * 56}┘{Style.RESET_ALL}")

            if layer > 1:
                print(f"          {'↓' * 5}    {'↑' * 5}")

        print()

    def print_encapsulation_diagram(self, comm_type: str = "ethernet"):
        """Print a diagram showing encapsulation at each layer."""
        print("\n" + "=" * 70)
        print(f"          DATA ENCAPSULATION ({comm_type.upper()})")
        print("=" * 70)
        print()

        # Show data growing as it moves down layers
        data_representations = {
            7: "[         Application Data          ]",
            6: "[H6][       Application Data        ]",
            5: "[H5][H6][     Application Data      ]",
            4: "[H4][H5][H6][   Application Data    ]",
            3: "[H3][H4][H5][H6][ Application Data  ]",
            2: "[H2][H3][H4][H5][H6][App Data][T2]",
            1: "10101010[H2][H3][H4][H5][H6][App Data][T2]1010",
        }

        descriptions = {
            7: "Original user data",
            6: "Add: Encoding, encryption info",
            5: "Add: Session ID, sync points",
            4: "Add: Port numbers, seq/ack (TCP)" if comm_type == "ethernet" else "Add: Sequence numbers",
            3: "Add: IP addresses, TTL" if comm_type == "ethernet" else "Add: Device addresses (PPP)",
            2: "Add: MAC addresses, FCS" if comm_type == "ethernet" else "Add: HDLC flags, CRC",
            1: "Add: Preamble, convert to bits",
        }

        for layer in range(7, 0, -1):
            color = self.LAYER_COLORS[layer]
            name = self.LAYER_NAMES[layer]
            pdu = self.PDU_NAMES[layer]
            data = data_representations[layer]
            desc = descriptions[layer]

            print(f"{color}Layer {layer} ({name}): {pdu}{Style.RESET_ALL}")
            print(f"   {data}")
            print(f"   └─ {desc}")
            print()

    def print_comparison_table(self, serial_summary: list, ethernet_summary: list):
        """Print a comparison table of serial vs ethernet at each layer."""
        print("\n" + "=" * 90)
        print("               SERIAL vs ETHERNET COMPARISON BY OSI LAYER")
        print("=" * 90)
        print()

        header = f"{'Layer':<8} {'Name':<14} {'Serial Protocol':<25} {'Ethernet Protocol':<25}"
        print(header)
        print("-" * 90)

        for layer in range(7, 0, -1):
            serial = serial_summary[7 - layer]
            ethernet = ethernet_summary[7 - layer]

            color = self.LAYER_COLORS[layer]
            row = (f"{color}{layer:<8} {self.LAYER_NAMES[layer]:<14} "
                   f"{serial['serial_protocol']:<25} {ethernet['ethernet_protocol']:<25}{Style.RESET_ALL}")
            print(row)

        print("-" * 90)
        print()

    def print_data_flow(self, direction: str = "send"):
        """Print ASCII art showing data flow direction."""
        if direction == "send":
            print("\n  APPLICATION")
            print("      │")
            print("      ▼")
            for layer in range(6, 0, -1):
                color = self.LAYER_COLORS[layer + 1]
                print(f"  {color}Layer {layer + 1}{Style.RESET_ALL}")
                print("      │")
                print("      ▼")
            print("  PHYSICAL MEDIUM")
            print("      │")
            print("  ═══════════════")
            print("    Network/Cable")
        else:
            print("\n    Network/Cable")
            print("  ═══════════════")
            print("      │")
            print("  PHYSICAL MEDIUM")
            for layer in range(1, 8):
                print("      │")
                print("      ▲")
                color = self.LAYER_COLORS[layer]
                print(f"  {color}Layer {layer}{Style.RESET_ALL}")
            print("      │")
            print("      ▲")
            print("  APPLICATION")

    def print_layer_detail_box(self, layer: int, protocol: str, data: dict):
        """Print a detailed box for a specific layer."""
        color = self.LAYER_COLORS[layer]
        name = self.LAYER_NAMES[layer]
        pdu = self.PDU_NAMES[layer]

        width = 60

        print(f"\n{color}╔{'═' * width}╗{Style.RESET_ALL}")
        print(f"{color}║ Layer {layer}: {name:<{width - 12}}║{Style.RESET_ALL}")
        print(f"{color}╠{'═' * width}╣{Style.RESET_ALL}")
        print(f"{color}║ PDU: {pdu:<{width - 7}}║{Style.RESET_ALL}")
        print(f"{color}║ Protocol: {protocol:<{width - 12}}║{Style.RESET_ALL}")
        print(f"{color}╠{'─' * width}╣{Style.RESET_ALL}")

        for key, value in data.items():
            value_str = str(value)[:width - len(key) - 5]
            print(f"{color}║ {key}: {value_str:<{width - len(key) - 4}}║{Style.RESET_ALL}")

        print(f"{color}╚{'═' * width}╝{Style.RESET_ALL}")

    def print_frame_structure(self, frame_type: str = "ethernet"):
        """Print the structure of a frame/packet."""
        if frame_type == "ethernet":
            print("\n" + "=" * 70)
            print("                    ETHERNET FRAME STRUCTURE")
            print("=" * 70)
            print()
            print("┌──────────┬──────────┬──────────┬──────────────────┬─────┐")
            print("│ Preamble │ Dest MAC │ Src MAC  │     Payload      │ FCS │")
            print("│ 8 bytes  │ 6 bytes  │ 6 bytes  │   46-1500 bytes  │ 4B  │")
            print("└──────────┴──────────┴──────────┴──────────────────┴─────┘")
            print()
            print("Payload contains: IP Header + TCP/UDP Header + Application Data")
        else:  # serial/HDLC
            print("\n" + "=" * 70)
            print("                    HDLC FRAME STRUCTURE (Serial)")
            print("=" * 70)
            print()
            print("┌──────┬─────────┬─────────┬──────────────────┬─────┬──────┐")
            print("│ Flag │ Address │ Control │     Payload      │ FCS │ Flag │")
            print("│ 0x7E │ 1 byte  │ 1 byte  │   Variable       │ 2B  │ 0x7E │")
            print("└──────┴─────────┴─────────┴──────────────────┴─────┴──────┘")
            print()
            print("Payload contains: Protocol data (Modbus, PPP, etc.)")

    def print_tcp_handshake(self):
        """Print TCP three-way handshake diagram."""
        print("\n" + "=" * 50)
        print("       TCP THREE-WAY HANDSHAKE")
        print("=" * 50)
        print()
        print("    Client                     Server")
        print("      │                           │")
        print("      │───── SYN (seq=x) ────────>│")
        print("      │                           │")
        print("      │<──── SYN-ACK ────────────│")
        print("      │      (seq=y, ack=x+1)     │")
        print("      │                           │")
        print("      │───── ACK (ack=y+1) ──────>│")
        print("      │                           │")
        print("      │   Connection Established  │")
        print("      │                           │")
        print()

    def print_welcome_banner(self):
        """Print welcome banner for the application."""
        banner = """
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║     ██████╗ ███████╗██╗    ███╗   ███╗ ██████╗ ██████╗ ███████╗   ║
║    ██╔═══██╗██╔════╝██║    ████╗ ████║██╔═══██╗██╔══██╗██╔════╝   ║
║    ██║   ██║███████╗██║    ██╔████╔██║██║   ██║██║  ██║█████╗     ║
║    ██║   ██║╚════██║██║    ██║╚██╔╝██║██║   ██║██║  ██║██╔══╝     ║
║    ╚██████╔╝███████║██║    ██║ ╚═╝ ██║╚██████╔╝██████╔╝███████╗   ║
║     ╚═════╝ ╚══════╝╚═╝    ╚═╝     ╚═╝ ╚═════╝ ╚═════╝ ╚══════╝   ║
║                                                                   ║
║        Communication Demonstration Application                     ║
║        Serial & Ethernet through all 7 OSI Layers                 ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
"""
        print(f"{Fore.CYAN}{banner}{Style.RESET_ALL}")
