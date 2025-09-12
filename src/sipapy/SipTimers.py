from dataclasses import dataclass

@dataclass(frozen=True)
class SipTimers:
    T1: float = 0.5      # RTT estimate in seconds
    T2: float = 4.0      # Max retransmit interval for non-INVITE
    T4: float = 5.0      # Network timeout
    A: float = T1        # INVITE request retransmit interval
    B: float = 64 * T1   # INVITE transaction timeout
    C: float = 3 * 60.0  # Proxy INVITE timeout (optional)
    D: float = 0.0       # Wait time for response retransmits
    E: float = T1        # Non-INVITE request retransmit interval
    F: float = 64 * T1   # Non-INVITE transaction timeout
    G: float = T1        # INVITE response retransmit interval
    H: float = 64 * T1   # Wait time for ACKs
    I: float = T4        # Wait time after sending ACK
    J: float = 64 * T1   # Wait time for non-INVITE responses
    K: float = T4        # Timer for ACK retransmissions
