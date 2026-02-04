#!/usr/bin/env python3
"""
OSI Model Communication Demonstration Application

This application demonstrates how data flows through all 7 layers
of the OSI model for both Serial and Ethernet communication.

Usage:
    python -m src.main [--mode MODE] [--verbose]

Modes:
    interactive - Interactive CLI menu (default)
    serial      - Run serial communication demo
    ethernet    - Run ethernet communication demo
    compare     - Show comparison between serial and ethernet
"""

import argparse
import sys
from typing import Optional

from .serial_comm import SerialCommunicationDemo
from .ethernet_comm import EthernetCommunicationDemo
from .utils import OSIVisualizer


def print_menu():
    """Print the interactive menu."""
    print("\n" + "=" * 50)
    print("           MAIN MENU")
    print("=" * 50)
    print("1. Show OSI Model Overview")
    print("2. Serial Communication Demo")
    print("3. Ethernet Communication Demo")
    print("4. Compare Serial vs Ethernet")
    print("5. TCP Handshake Demo")
    print("6. ARP Resolution Demo")
    print("7. DNS Query Demo")
    print("8. Show Encapsulation Diagram")
    print("9. Show Frame Structures")
    print("0. Exit")
    print("-" * 50)


def run_serial_demo(visualizer: OSIVisualizer, verbose: bool = True):
    """Run the serial communication demonstration."""
    print("\n" + "=" * 70)
    print("            SERIAL COMMUNICATION DEMONSTRATION")
    print("=" * 70)

    demo = SerialCommunicationDemo(verbose=verbose)

    # Show layer summary
    print("\n📋 Serial Communication OSI Layer Summary:")
    print("-" * 70)
    for layer_info in demo.get_serial_layer_summary():
        print(f"  Layer {layer_info['layer']}: {layer_info['name']:<15} "
              f"Protocol: {layer_info['serial_protocol']:<20} PDU: {layer_info['pdu']}")
    print()

    # Get message from user or use default
    message = input("Enter message to send (or press Enter for default): ").strip()
    if not message:
        message = "Hello from Serial!"

    # Run the demonstration
    demo.demonstrate_send(message)

    # Show physical layer details
    visualizer.print_frame_structure("serial")


def run_ethernet_demo(visualizer: OSIVisualizer, verbose: bool = True):
    """Run the ethernet communication demonstration."""
    print("\n" + "=" * 70)
    print("            ETHERNET COMMUNICATION DEMONSTRATION")
    print("=" * 70)

    demo = EthernetCommunicationDemo(verbose=verbose)

    # Show layer summary
    print("\n📋 Ethernet Communication OSI Layer Summary:")
    print("-" * 70)
    for layer_info in demo.get_ethernet_layer_summary():
        print(f"  Layer {layer_info['layer']}: {layer_info['name']:<15} "
              f"Protocol: {layer_info['ethernet_protocol']:<20} PDU: {layer_info['pdu']}")
    print()

    # Get parameters from user or use defaults
    message = input("Enter message to send (or press Enter for default): ").strip()
    if not message:
        message = "Hello from Ethernet!"

    dest_ip = input("Enter destination IP (or press Enter for 192.168.1.1): ").strip()
    if not dest_ip:
        dest_ip = "192.168.1.1"

    dest_port_str = input("Enter destination port (or press Enter for 80): ").strip()
    dest_port = int(dest_port_str) if dest_port_str else 80

    # Run the demonstration
    demo.demonstrate_send(message, dest_ip, dest_port)

    # Show physical layer details
    visualizer.print_frame_structure("ethernet")


def run_comparison(visualizer: OSIVisualizer):
    """Run comparison between serial and ethernet."""
    serial_demo = SerialCommunicationDemo(verbose=False)
    ethernet_demo = EthernetCommunicationDemo(verbose=False)

    serial_summary = serial_demo.get_serial_layer_summary()
    ethernet_summary = ethernet_demo.get_ethernet_layer_summary()

    visualizer.print_comparison_table(serial_summary, ethernet_summary)

    # Print detailed comparison
    comparison = ethernet_demo.compare_with_serial()

    print("\n" + "=" * 70)
    print("               DETAILED COMPARISON")
    print("=" * 70)

    for layer in range(7, 0, -1):
        comp = comparison[layer]
        print(f"\n📊 Layer {layer} - {comp['layer']}:")
        print(f"   Ethernet: {comp['ethernet']}")
        print(f"   Serial:   {comp['serial']}")
        print(f"   Key Diff: {comp['difference']}")


def run_tcp_handshake(visualizer: OSIVisualizer):
    """Demonstrate TCP three-way handshake."""
    visualizer.print_tcp_handshake()

    demo = EthernetCommunicationDemo(verbose=True)

    dest_ip = input("Enter destination IP (or press Enter for 192.168.1.1): ").strip()
    if not dest_ip:
        dest_ip = "192.168.1.1"

    demo.demonstrate_tcp_handshake(dest_ip, 80)


def run_arp_demo():
    """Demonstrate ARP resolution."""
    demo = EthernetCommunicationDemo(verbose=True)

    target_ip = input("Enter target IP (or press Enter for 192.168.1.1): ").strip()
    if not target_ip:
        target_ip = "192.168.1.1"

    demo.demonstrate_arp_resolution(target_ip)


def run_dns_demo():
    """Demonstrate DNS query."""
    demo = EthernetCommunicationDemo(verbose=True)

    domain = input("Enter domain to resolve (or press Enter for example.com): ").strip()
    if not domain:
        domain = "example.com"

    demo.demonstrate_dns_query(domain)


def interactive_mode():
    """Run the application in interactive mode."""
    visualizer = OSIVisualizer()
    visualizer.print_welcome_banner()

    while True:
        print_menu()
        choice = input("Select option: ").strip()

        if choice == '1':
            visualizer.print_osi_model()
            visualizer.print_data_flow("send")

        elif choice == '2':
            run_serial_demo(visualizer)

        elif choice == '3':
            run_ethernet_demo(visualizer)

        elif choice == '4':
            run_comparison(visualizer)

        elif choice == '5':
            run_tcp_handshake(visualizer)

        elif choice == '6':
            run_arp_demo()

        elif choice == '7':
            run_dns_demo()

        elif choice == '8':
            print("\nSelect type:")
            print("1. Ethernet encapsulation")
            print("2. Serial encapsulation")
            enc_choice = input("Choice: ").strip()
            if enc_choice == '1':
                visualizer.print_encapsulation_diagram("ethernet")
            else:
                visualizer.print_encapsulation_diagram("serial")

        elif choice == '9':
            print("\nSelect type:")
            print("1. Ethernet frame")
            print("2. Serial/HDLC frame")
            frame_choice = input("Choice: ").strip()
            if frame_choice == '1':
                visualizer.print_frame_structure("ethernet")
            else:
                visualizer.print_frame_structure("serial")

        elif choice == '0':
            print("\nThank you for using OSI Model Demo!")
            print("Goodbye! 👋")
            break

        else:
            print("\n⚠️  Invalid option. Please try again.")

        input("\nPress Enter to continue...")


def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(
        description='OSI Model Communication Demonstration',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m src.main                    # Interactive mode
  python -m src.main --mode serial      # Serial demo only
  python -m src.main --mode ethernet    # Ethernet demo only
  python -m src.main --mode compare     # Comparison mode

This application demonstrates how data flows through all 7 layers
of the OSI model for both Serial (RS-232) and Ethernet (IEEE 802.3)
communication.
        """
    )

    parser.add_argument(
        '--mode', '-m',
        choices=['interactive', 'serial', 'ethernet', 'compare'],
        default='interactive',
        help='Demo mode to run (default: interactive)'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        default=True,
        help='Enable verbose output (default: True)'
    )

    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Disable verbose output'
    )

    parser.add_argument(
        '--message',
        type=str,
        default="Hello, OSI World!",
        help='Message to send in demo (default: "Hello, OSI World!")'
    )

    args = parser.parse_args()

    verbose = not args.quiet
    visualizer = OSIVisualizer()

    if args.mode == 'interactive':
        interactive_mode()

    elif args.mode == 'serial':
        visualizer.print_welcome_banner()
        demo = SerialCommunicationDemo(verbose=verbose)
        demo.demonstrate_send(args.message)

    elif args.mode == 'ethernet':
        visualizer.print_welcome_banner()
        demo = EthernetCommunicationDemo(verbose=verbose)
        demo.demonstrate_send(args.message)

    elif args.mode == 'compare':
        visualizer.print_welcome_banner()
        run_comparison(visualizer)


if __name__ == '__main__':
    main()
