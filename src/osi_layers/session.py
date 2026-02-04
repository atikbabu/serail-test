"""
Layer 5: Session Layer Implementation

The Session Layer is responsible for:
- Session establishment, maintenance, and termination
- Dialog control: Managing conversation between applications
- Synchronization: Checkpoints for data recovery
- Token management: Controlling access to shared resources

Key Functions:
- Authentication and authorization
- Session restoration after interruption
- Simplex, half-duplex, full-duplex communication modes

Protocols at this layer:
- NetBIOS, RPC, SQL, NFS
- PAP (Password Authentication Protocol)
- PPTP (Point-to-Point Tunneling Protocol)
"""

from .base import OSILayer, DataUnit
import random
import time
from datetime import datetime


class SessionLayer(OSILayer):
    """
    Session Layer - Handles session management.

    This layer manages dialogs, synchronization, and checkpoints
    between communicating applications.
    """

    LAYER_NUMBER = 5
    LAYER_NAME = "Session"
    PDU_NAME = "Data"

    def __init__(self, verbose: bool = True):
        super().__init__(verbose)

        # Session state
        self.sessions = {}
        self.current_session_id = None

        # Configuration
        self.config = {
            'dialog_mode': 'full-duplex',  # simplex, half-duplex, full-duplex
            'sync_interval': 100,  # Bytes between sync points
            'max_sessions': 10,
            'session_timeout': 300,  # seconds
        }

    def encapsulate(self, data: DataUnit) -> DataUnit:
        """
        Encapsulate presentation data with session information.

        Adds:
        - Session ID
        - Dialog tokens
        - Synchronization points
        """
        self.log(f"Adding session management to {self.PDU_NAME.lower()}")

        # Create or use existing session
        if self.current_session_id is None:
            self.current_session_id = self._create_session()

        session = self.sessions.get(self.current_session_id, {})

        # Increment message counter
        session['message_count'] = session.get('message_count', 0) + 1

        # Add synchronization point if needed
        sync_point = None
        if session['message_count'] % 10 == 0:
            sync_point = self._create_sync_point(session)
            self.log(f"Created sync point: {sync_point}")

        header = {
            'session_id': self.current_session_id,
            'dialog_mode': self.config['dialog_mode'],
            'token_holder': session.get('token_holder', 'initiator'),
            'message_sequence': session['message_count'],
            'sync_point': sync_point,
            'timestamp': datetime.now().isoformat(),
            'activity_id': session.get('activity_id'),
        }

        self.log(f"Session ID: {self.current_session_id}")
        self.log(f"Dialog mode: {self.config['dialog_mode']}")
        self.log(f"Message sequence: {session['message_count']}")

        return DataUnit(
            payload=data,
            header=header,
            layer=self.LAYER_NUMBER,
            pdu_name=self.PDU_NAME
        )

    def decapsulate(self, data: DataUnit) -> DataUnit:
        """
        Decapsulate session data to extract presentation data.

        Validates:
        - Session ID
        - Message sequence
        - Synchronization points
        """
        self.log(f"Processing session {self.PDU_NAME.lower()}")

        header = data.header
        session_id = header.get('session_id', 'Unknown')
        msg_seq = header.get('message_sequence', 0)
        sync_point = header.get('sync_point')

        self.log(f"Session ID: {session_id}")
        self.log(f"Message sequence: {msg_seq}")

        if sync_point:
            self.log(f"Sync point received: {sync_point}")
            self._process_sync_point(session_id, sync_point)

        # Validate session
        if session_id in self.sessions:
            self.sessions[session_id]['last_activity'] = time.time()
            self.sessions[session_id]['received_count'] = \
                self.sessions[session_id].get('received_count', 0) + 1

        # Extract presentation data payload
        payload = data.payload
        if isinstance(payload, DataUnit):
            return payload
        else:
            return DataUnit(payload=payload, layer=6, pdu_name="Data")

    def _create_session(self) -> str:
        """Create a new session and return session ID."""
        session_id = f"SES-{random.randint(10000, 99999)}"

        self.sessions[session_id] = {
            'id': session_id,
            'state': 'established',
            'created': time.time(),
            'last_activity': time.time(),
            'token_holder': 'initiator',
            'message_count': 0,
            'received_count': 0,
            'sync_points': [],
            'activity_id': f"ACT-{random.randint(1000, 9999)}",
        }

        self.log(f"Created new session: {session_id}")
        return session_id

    def _create_sync_point(self, session: dict) -> dict:
        """Create a synchronization point for recovery."""
        sync_point = {
            'id': len(session.get('sync_points', [])) + 1,
            'timestamp': time.time(),
            'message_sequence': session['message_count'],
            'type': 'major',  # major or minor
        }
        session.setdefault('sync_points', []).append(sync_point)
        return sync_point

    def _process_sync_point(self, session_id: str, sync_point: dict):
        """Process received synchronization point."""
        if session_id in self.sessions:
            self.sessions[session_id]['last_sync'] = sync_point

    def establish_session(self, peer_address: str = None) -> str:
        """
        Establish a new session with a peer.

        Returns session ID.
        """
        self.log("Initiating session establishment...")

        # Session establishment phases
        phases = [
            "Phase 1: Connection request",
            "Phase 2: Parameter negotiation",
            "Phase 3: Authentication",
            "Phase 4: Session established",
        ]

        for phase in phases:
            self.log(f"  {phase}")

        session_id = self._create_session()
        self.current_session_id = session_id

        if peer_address:
            self.sessions[session_id]['peer_address'] = peer_address

        return session_id

    def terminate_session(self, session_id: str = None) -> bool:
        """
        Terminate a session gracefully.

        Returns True if successful.
        """
        if session_id is None:
            session_id = self.current_session_id

        if session_id not in self.sessions:
            self.log(f"Session {session_id} not found")
            return False

        self.log(f"Terminating session: {session_id}")

        # Termination phases
        phases = [
            "Phase 1: Release request",
            "Phase 2: Final data transfer",
            "Phase 3: Confirmation",
            "Phase 4: Session terminated",
        ]

        for phase in phases:
            self.log(f"  {phase}")

        self.sessions[session_id]['state'] = 'terminated'
        self.sessions[session_id]['terminated'] = time.time()

        if self.current_session_id == session_id:
            self.current_session_id = None

        return True

    def get_session_info(self, session_id: str = None) -> dict:
        """Get information about a session."""
        if session_id is None:
            session_id = self.current_session_id

        if session_id in self.sessions:
            session = self.sessions[session_id].copy()
            session['duration'] = time.time() - session['created']
            return session

        return {}

    def request_token(self, token_type: str = 'data') -> bool:
        """
        Request a dialog token (for half-duplex communication).

        Token types: data, release, sync
        """
        if self.current_session_id is None:
            return False

        session = self.sessions.get(self.current_session_id)
        if session:
            self.log(f"Requesting {token_type} token...")
            session['token_holder'] = 'local'
            session['token_type'] = token_type
            return True

        return False

    def give_token(self) -> bool:
        """Give up the dialog token to the peer."""
        if self.current_session_id is None:
            return False

        session = self.sessions.get(self.current_session_id)
        if session:
            self.log("Giving token to peer...")
            session['token_holder'] = 'peer'
            return True

        return False

    def resync_session(self, sync_point_id: int) -> bool:
        """
        Resynchronize session to a previous sync point.

        Used for recovery after failures.
        """
        if self.current_session_id is None:
            return False

        session = self.sessions.get(self.current_session_id)
        if session:
            sync_points = session.get('sync_points', [])
            for sp in sync_points:
                if sp['id'] == sync_point_id:
                    self.log(f"Resynchronizing to sync point {sync_point_id}")
                    session['message_count'] = sp['message_sequence']
                    return True

        self.log(f"Sync point {sync_point_id} not found")
        return False
