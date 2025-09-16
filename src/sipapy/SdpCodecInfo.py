from enum import Enum

class Codec(Enum):
    """
    An enumeration of common RTP codecs.
    
    Using an Enum provides type safety and improves code readability.
    """
    PCMU = "PCMU"
    PCMA = "PCMA"
    G729 = "G729"
    OPUS = "opus"
    AMR = "AMR"
    AMR_WB = "AMR-WB"
    G722 = "G722"
    L16 = "L16"
    L24 = "L24"
    AAC = "AAC"
    H264 = "H264"
    VP8 = "VP8"
    TELEPHONE_EVENT = "telephone-event"


class SdpCodecInfo:
    """
    A class to represent a specific codec and its attributes.
    """
    def __init__(self, codec_name, clock_rate: int, channels: int = 1):
        self.codec = Codec(codec_name) if codec_name in Codec._value2member_map_ else codec_name
        self.clock_rate = clock_rate
        self.channels = channels
        self.fmtp = []
    
    def __str__(self):
        if self.codec in Codec:
            return f"{self.codec.value}/{self.clock_rate}/{self.channels}"
        return f"{self.codec}/{self.clock_rate}/{self.channels}"

class MediaLine:
    """
    A class representing a single media description line from SDP.
    
    This class encapsulates media-related attributes and uses a list of
    CodecInfo objects to represent the available codecs.
    """
    def __init__(self, media_type: str, port: int, payload_types: list, codecs: list):
        self.media_type = media_type
        self.port = port
        self.payload_types = payload_types
        self.codecs = codecs

    def get_info(self):
        """
        Prints information about the media line and its codecs.
        """
        print(f"Media Type: {self.media_type}")
        print(f"Port: {self.port}")
        print(f"Payload Types: {self.payload_types}")
        print("Available Codecs:")
        for codec_info in self.codecs:
            fmtp_str = f" with fmtp: {codec_info.fmtp}" if codec_info.fmtp else ""
            print(f"  - {codec_info.codec.value}/{codec_info.clock_rate}/{codec_info.channels}{fmtp_str}")