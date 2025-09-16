# Copyright (c) 2003-2005 Maxim Sobolev. All rights reserved.
# Copyright (c) 2006-2022 Sippy Software, Inc. All rights reserved.
# 2025 cleaned up by eckschi

# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation and/or
# other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from sipapy.SdpConnection import SdpConnection
from sipapy.SdpGeneric import SdpGeneric
from sipapy.SdpCodecInfo import SdpCodecInfo, Codec

from enum import Enum
import re

f_types = {'i': SdpGeneric, 'c': SdpConnection, 'b': SdpGeneric,
           'k': SdpGeneric}

# Using an Enum is the best way to define a fixed set of types
class MediaType(Enum):
    AUDIO = "audio"
    VIDEO = "video"
    OTHER = "other"


class a_header:
    name = None
    value = None

    def __init__(self, s):
        parts = s.split(':', 1)
        self.name = parts[0]
        if len(parts) > 1:
            self.value = parts[1]

    def __str__(self):
        if self.value is None:
            return self.name
        return '{}:{}'.format(self.name, self.value)


class SdpMediaDescription:
    all_headers = ('m', 'i', 'c', 'b', 'k')

    def __init__(self, body=None):
        self.other_attributes = []
        self.c_header = None
        self.codecs = {}
        if body is not None:
            self.from_string(body)

    @classmethod
    def fromString(cls, s):
        parts = s.split()
        media_desc = cls()
        media_desc.stype = parts[0]
        media_desc.port = int(parts[1])
        media_desc.transport = parts[2]
        if media_desc.stype.lower() == 'audio':
            media_desc.type = MediaType.AUDIO
        elif media_desc.stype.lower() == 'video':
            media_desc.type = MediaType.VIDEO
        else:
            media_desc.type = MediaType.OTHER
        if media_desc.type in (MediaType.AUDIO, MediaType.VIDEO):
            media_desc.formats = [int(x) for x in parts[3:]]
        else:
            media_desc.formats = parts[3:]
        return media_desc

    def __str__(self):
        # media line
        s = '%s %d %s' % (self.stype, self.port, self.transport)
        if self.type in (MediaType.AUDIO, MediaType.VIDEO):
            for format in self.formats:
                s += ' %d' % format
        else:
            for format in self.formats:
                s += ' %s' % format
        # other headers
        for name in self.all_headers:
            header = getattr(self, name + '_header')
            if header is not None:
                s += '{}={}\r\n'.format(name, str(header))
        for header in self.other_attributes:
            s += 'a=%s\r\n' % str(header)
        return s

    def localStr(self, local_addr=None, local_port=None, noC=False):
        s = ''
        for name in self.all_headers:
            if noC and name == 'c':
                continue
            header = getattr(self, name + '_header')
            if header is not None:
                s += '{}={}\r\n'.format(name,
                                        header.localStr(local_addr, local_port))
        for header in self.other_attributes:
            s += 'a=%s\r\n' % str(header)
        return s

    def __iadd__(self, other):
        self.addHeader(*other.strip().split('=', 1))
        return self

    def addHeader(self, name, header):
        rtpmap_regex = re.compile(r'rtpmap:(\d+)\s+([a-zA-Z0-9\-]+)/(\d+)(?:/(\d+))?')
        fmtp_regex = re.compile(r'fmtp:(\d+)\s+(.+)')

        if name == 'a':
            self.other_attributes.append(a_header(header))

            rtpmap_match = rtpmap_regex.search(header)
            if rtpmap_match:
                payload_type = int(rtpmap_match.group(1))
                codec_name = rtpmap_match.group(2)
                clock_rate = int(rtpmap_match.group(3))
                channels = int(rtpmap_match.group(4)) if rtpmap_match.group(4) else 1
                print(f"Parsed rtpmap - Payload Type: {payload_type}, Codec: {codec_name}, Clock Rate: {clock_rate}, Channels: {channels}")
                self.codecs[payload_type] = SdpCodecInfo(codec_name, clock_rate, channels)
                print(f"Created SdpCodecInfo: {self.codecs[payload_type]}")

            fmtp_match = fmtp_regex.search(header)
            if fmtp_match:
                payload_type = int(fmtp_match.group(1))
                params = fmtp_match.group(2)
                print(f"Parsed fmtp - Payload Type: {payload_type}, Params: {params}")
                if payload_type in self.codecs:
                    self.codecs[payload_type].fmtp = params

        else:
            setattr(self, name + '_header', f_types[name](header))
