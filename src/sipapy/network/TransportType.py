from enum import Enum, auto

class TransportType(Enum):
    """Enumeration of supported transport protocols."""
    UDP = auto()
    TCP = auto()
    TLS = auto()
    
    def __str__(self):
        return self.name
    
    def __repr__(self):
        return f"TransportType.{self.name}"