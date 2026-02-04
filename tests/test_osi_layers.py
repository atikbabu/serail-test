"""
Tests for OSI Layer implementations.
"""

import unittest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.osi_layers import (
    DataUnit,
    PhysicalLayer,
    DataLinkLayer,
    NetworkLayer,
    TransportLayer,
    SessionLayer,
    PresentationLayer,
    ApplicationLayer,
)


class TestDataUnit(unittest.TestCase):
    """Tests for DataUnit class."""

    def test_create_data_unit(self):
        """Test creating a basic DataUnit."""
        du = DataUnit(payload="test data", layer=7, pdu_name="Data")
        self.assertEqual(du.payload, "test data")
        self.assertEqual(du.layer, 7)
        self.assertEqual(du.pdu_name, "Data")

    def test_to_bytes(self):
        """Test converting DataUnit to bytes."""
        du = DataUnit(payload="test", header={'key': 'value'})
        data = du.to_bytes()
        self.assertIsInstance(data, bytes)
        self.assertIn(b'test', data)

    def test_from_bytes(self):
        """Test creating DataUnit from bytes."""
        original = DataUnit(payload="test", header={'key': 'value'})
        data = original.to_bytes()
        restored = DataUnit.from_bytes(data, layer=7)
        self.assertEqual(restored.payload, "test")


class TestPhysicalLayer(unittest.TestCase):
    """Tests for Physical Layer."""

    def test_serial_encapsulation(self):
        """Test serial physical layer encapsulation."""
        layer = PhysicalLayer(medium_type="serial", verbose=False)
        input_data = DataUnit(payload="test", layer=2, pdu_name="Frame")

        result = layer.encapsulate(input_data)

        self.assertEqual(result.layer, 1)
        self.assertEqual(result.pdu_name, "Bits")
        self.assertIn('baud_rate', result.header)

    def test_ethernet_encapsulation(self):
        """Test ethernet physical layer encapsulation."""
        layer = PhysicalLayer(medium_type="ethernet", verbose=False)
        input_data = DataUnit(payload="test", layer=2, pdu_name="Frame")

        result = layer.encapsulate(input_data)

        self.assertEqual(result.layer, 1)
        self.assertIn('speed_mbps', result.header)


class TestDataLinkLayer(unittest.TestCase):
    """Tests for Data Link Layer."""

    def test_ethernet_frame(self):
        """Test ethernet frame creation."""
        layer = DataLinkLayer(protocol="ethernet", verbose=False)
        input_data = DataUnit(payload="test", layer=3, pdu_name="Packet")

        result = layer.encapsulate(input_data)

        self.assertEqual(result.layer, 2)
        self.assertEqual(result.pdu_name, "Frame")
        self.assertIn('source_mac', result.header)
        self.assertIn('destination_mac', result.header)
        self.assertIn('fcs', result.trailer)

    def test_hdlc_frame(self):
        """Test HDLC frame creation for serial."""
        layer = DataLinkLayer(protocol="serial", verbose=False)
        input_data = DataUnit(payload="test", layer=3, pdu_name="Packet")

        result = layer.encapsulate(input_data)

        self.assertEqual(result.header['protocol'], 'HDLC')
        self.assertIn('fcs', result.trailer)

    def test_mac_address_format(self):
        """Test MAC address generation format."""
        layer = DataLinkLayer(protocol="ethernet", verbose=False)
        mac = layer.get_mac_address()

        # Should be in format XX:XX:XX:XX:XX:XX
        parts = mac.split(':')
        self.assertEqual(len(parts), 6)
        for part in parts:
            self.assertEqual(len(part), 2)


class TestNetworkLayer(unittest.TestCase):
    """Tests for Network Layer."""

    def test_ipv4_packet(self):
        """Test IPv4 packet creation."""
        layer = NetworkLayer(ip_version=4, verbose=False)
        input_data = DataUnit(
            payload="test",
            header={'destination_ip': '192.168.1.1'},
            layer=4,
            pdu_name="Segment"
        )

        result = layer.encapsulate(input_data)

        self.assertEqual(result.layer, 3)
        self.assertEqual(result.pdu_name, "Packet")
        self.assertEqual(result.header['version'], 4)
        self.assertIn('source_ip', result.header)
        self.assertIn('ttl', result.header)

    def test_icmp_packet(self):
        """Test ICMP packet creation."""
        layer = NetworkLayer(verbose=False)
        packet = layer.create_icmp_packet('192.168.1.1')

        self.assertEqual(packet.layer, 3)
        self.assertIn('destination_ip', packet.header)


class TestTransportLayer(unittest.TestCase):
    """Tests for Transport Layer."""

    def test_tcp_segment(self):
        """Test TCP segment creation."""
        layer = TransportLayer(protocol="TCP", verbose=False)
        input_data = DataUnit(
            payload="test",
            header={'destination_port': 80},
            layer=5,
            pdu_name="Data"
        )

        result = layer.encapsulate(input_data)

        self.assertEqual(result.layer, 4)
        self.assertIn('source_port', result.header)
        self.assertIn('destination_port', result.header)
        self.assertIn('sequence_number', result.header)
        self.assertIn('flags', result.header)

    def test_udp_datagram(self):
        """Test UDP datagram creation."""
        layer = TransportLayer(protocol="UDP", verbose=False)
        input_data = DataUnit(
            payload="test",
            header={'destination_port': 53},
            layer=5,
            pdu_name="Data"
        )

        result = layer.encapsulate(input_data)

        self.assertEqual(result.pdu_name, "Datagram")
        self.assertIn('length', result.header)

    def test_syn_segment(self):
        """Test SYN segment creation."""
        layer = TransportLayer(protocol="TCP", verbose=False)
        syn = layer.create_syn_segment(80)

        self.assertTrue(syn.header['flags']['SYN'])
        self.assertFalse(syn.header['flags']['ACK'])


class TestSessionLayer(unittest.TestCase):
    """Tests for Session Layer."""

    def test_session_creation(self):
        """Test session establishment."""
        layer = SessionLayer(verbose=False)
        session_id = layer.establish_session()

        self.assertIsNotNone(session_id)
        self.assertTrue(session_id.startswith('SES-'))

    def test_session_encapsulation(self):
        """Test session data encapsulation."""
        layer = SessionLayer(verbose=False)
        layer.establish_session()

        input_data = DataUnit(payload="test", layer=6, pdu_name="Data")
        result = layer.encapsulate(input_data)

        self.assertIn('session_id', result.header)
        self.assertIn('message_sequence', result.header)


class TestPresentationLayer(unittest.TestCase):
    """Tests for Presentation Layer."""

    def test_json_encoding(self):
        """Test JSON serialization."""
        layer = PresentationLayer(verbose=False)
        layer.set_format('json')

        input_data = DataUnit(
            payload={'key': 'value'},
            layer=7,
            pdu_name="Data"
        )

        result = layer.encapsulate(input_data)

        self.assertEqual(result.header['format'], 'json')
        self.assertIn('checksum', result.header)

    def test_compression(self):
        """Test data compression."""
        layer = PresentationLayer(verbose=False)
        layer.set_compression('zlib')

        input_data = DataUnit(
            payload="test data " * 100,  # Repetitive data compresses well
            layer=7,
            pdu_name="Data"
        )

        result = layer.encapsulate(input_data)

        self.assertEqual(result.header['compression'], 'zlib')
        # Compressed size should be smaller
        self.assertLess(result.header['processed_size'], result.header['original_size'])


class TestApplicationLayer(unittest.TestCase):
    """Tests for Application Layer."""

    def test_http_request(self):
        """Test HTTP request creation."""
        layer = ApplicationLayer(protocol="HTTP", verbose=False)
        request = layer.create_http_request("GET", "/api", "example.com")

        self.assertEqual(request.header['protocol'], 'HTTP')
        self.assertEqual(request.header['method'], 'GET')
        self.assertEqual(request.header['path'], '/api')

    def test_dns_query(self):
        """Test DNS query creation."""
        layer = ApplicationLayer(protocol="DNS", verbose=False)
        query = layer.create_dns_query("example.com", "A")

        self.assertEqual(query.header['protocol'], 'DNS')
        self.assertEqual(query.header['query_name'], 'example.com')
        self.assertEqual(query.header['query_type'], 'A')

    def test_protocol_switching(self):
        """Test switching between protocols."""
        layer = ApplicationLayer(protocol="HTTP", verbose=False)
        self.assertEqual(layer.protocol, "HTTP")

        layer.set_protocol("FTP")
        self.assertEqual(layer.protocol, "FTP")


class TestFullStackEncapsulation(unittest.TestCase):
    """Integration tests for full OSI stack."""

    def test_ethernet_full_stack(self):
        """Test encapsulation through all layers for Ethernet."""
        layers = {
            7: ApplicationLayer(protocol="HTTP", verbose=False),
            6: PresentationLayer(verbose=False),
            5: SessionLayer(verbose=False),
            4: TransportLayer(protocol="TCP", verbose=False),
            3: NetworkLayer(ip_version=4, verbose=False),
            2: DataLinkLayer(protocol="ethernet", verbose=False),
            1: PhysicalLayer(medium_type="ethernet", verbose=False),
        }

        # Start with application data
        data = layers[7].encapsulate({"message": "Hello"})
        data.header['destination_ip'] = '192.168.1.1'
        data.header['destination_port'] = 80

        # Encapsulate through each layer
        for layer_num in range(6, 0, -1):
            data = layers[layer_num].encapsulate(data)

        # Verify final output is bits
        self.assertEqual(data.layer, 1)
        self.assertEqual(data.pdu_name, "Bits")
        self.assertIsInstance(data.payload, str)
        self.assertTrue(all(c in '01' for c in data.payload))

    def test_serial_full_stack(self):
        """Test encapsulation through all layers for Serial."""
        layers = {
            7: ApplicationLayer(protocol="SERIAL", verbose=False),
            6: PresentationLayer(verbose=False),
            5: SessionLayer(verbose=False),
            4: TransportLayer(protocol="TCP", verbose=False),
            3: NetworkLayer(ip_version=4, verbose=False),
            2: DataLinkLayer(protocol="serial", verbose=False),
            1: PhysicalLayer(medium_type="serial", verbose=False),
        }

        data = layers[7].encapsulate({"command": "READ"})

        for layer_num in range(6, 0, -1):
            data = layers[layer_num].encapsulate(data)

        self.assertEqual(data.layer, 1)
        self.assertIn('baud_rate', data.header)


if __name__ == '__main__':
    unittest.main()
