from enum import Enum, auto

class SipTransactionStates(Enum):
    # client
    CALLING = auto()
    TRYING = auto()       # Like CALLING but for non-INVITE
    PROCEEDING = auto()
    COMPLETED = auto()
    ACCEPTED = auto()     # Optional: RFC 6026 refinement
    TERMINATED = auto()
    CONFIRMED = auto()
