# Copyright (c) 2003-2005 Maxim Sobolev. All rights reserved.
# Copyright (c) 2006-2022 Sippy Software, Inc. All rights reserved.
#
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

from sipapy.SdpMediaDescription import SdpMediaDescription, a_header
from sipapy.SdpGeneric import SdpGeneric
from sipapy.SdpOrigin import SdpOrigin
from sipapy.SdpConnection import SdpConnection

f_types = {'v': SdpGeneric, 'o': SdpOrigin, 's': SdpGeneric, 'i': SdpGeneric,
           'u': SdpGeneric, 'e': SdpGeneric, 'p': SdpGeneric, 'c': SdpConnection,
           'b': SdpGeneric, 't': SdpGeneric, 'r': SdpGeneric, 'z': SdpGeneric,
           'k': SdpGeneric}


class SdpBody:
    first_half = ('v', 'o', 's', 'i', 'u', 'e', 'p')
    second_half = ('b', 't', 'r', 'z', 'k')
    all_headers = ('v', 'o', 's', 'i', 'u', 'e',
                   'p', 'c', 'b', 't', 'r', 'z', 'k')
    top_hdrs_req = ('v', 'o', 's', 't')
    sect_hdrs_req = ('c')

    def __init__(self):
        self.a_headers = []
        self.media_lines = []

    @classmethod
    def from_string(cls, body):
        inst = cls()
        avpairs = [x.split('=', 1)
                   for x in body.strip().splitlines() if len(x.strip()) > 0]

        current_media = None
        c_header = None

        media_level = False
        for name, v in avpairs:
            name = name.lower()
            # decide if we are in session or media section
            if name == 'm':
                media_level = True

            # parse the session level
            if not media_level:
                if name == 'c':
                    c_header = v
                elif name == 'a':
                    inst.a_headers.append(a_header(v))
                else:
                    setattr(inst, name + '_header', f_types[name](v))
            # parse the media level
            else:
                if name == 'm':
                    if current_media is not None:
                        inst.media_lines.append(current_media)
                    current_media = SdpMediaDescription.fromString(v)
                else:
                    current_media.addHeader(name, v)

        # add the last media section if any
        if current_media is not None:
            inst.media_lines.append(current_media)

        # post processing
        # add the connection to all media media_lines that do not have it
        if c_header is not None:
            for section in inst.media_lines:
                if section.c_header == None:
                    section.addHeader('c', c_header)
            if len(inst.media_lines) == 0:
                inst.addHeader('c', c_header)
        # Do some sanity checking, RFC4566
        for header_name in [x + '_header' for x in inst.top_hdrs_req]:
            if getattr(inst, header_name) == None:
                raise Exception(
                    f'Mandatory "{header_name[0]}=" session header is missing')
        for section in inst.media_lines:
            for header_name in [x + '_header' for x in inst.sect_hdrs_req]:
                if getattr(section, header_name) == None:
                    raise Exception(
                        f'Mandatory "{header_name[0]}=" media header is missing')

        return inst

    def __str__(self):
        s = ''
        if len(self.media_lines_lines) == 1 and self.media_lines_lines[0].c_header is not None:
            for name in self.first_half:
                header = getattr(self, name + '_header')
                if header is not None:
                    s += '{}={}\r\n'.format(name, str(header))
            s += 'c=%s\r\n' % str(self.media_lines_lines[0].c_header)
            for name in self.second_half:
                header = getattr(self, name + '_header')
                if header is not None:
                    s += '{}={}\r\n'.format(name, str(header))
            for header in self.a_headers:
                s += 'a=%s\r\n' % str(header)
            s += self.media_lines_lines[0].localStr(noC=True)
            return s
        # Special code to optimize for the cases when there are many media streams pointing to
        # the same IP. Only include c= header into the top section of the SDP and remove it from
        # the streams that match.
        optimize_c_headers = False
        if len(self.media_lines_lines) > 1 and self.c_header == None and self.media_lines_lines[0].c_header != None and \
                str(self.media_lines_lines[0].c_header) == str(self.media_lines_lines[1].c_header):
            # Special code to optimize for the cases when there are many media streams pointing to
            # the same IP. Only include c= header into the top section of the SDP and remove it from
            # the streams that match.
            optimize_c_headers = True
            media_lines_0_str = str(self.media_lines_lines[0].c_header)
        if optimize_c_headers:
            for name in self.first_half:
                header = getattr(self, name + '_header')
                if header is not None:
                    s += '{}={}\r\n'.format(name, str(header))
            s += 'c=%s\r\n' % media_lines_0_str
            for name in self.second_half:
                header = getattr(self, name + '_header')
                if header is not None:
                    s += '{}={}\r\n'.format(name, str(header))
        else:
            for name in self.all_headers:
                header = getattr(self, name + '_header')
                if header is not None:
                    s += '{}={}\r\n'.format(name, str(header))
        for header in self.a_headers:
            s += 'a=%s\r\n' % str(header)
        for section in self.media_lines_lines:
            if optimize_c_headers and section.c_header != None and \
                    str(section.c_header) == media_lines_0_str:
                s += section.localStr(noC=True)
            else:
                s += str(section)
        return s

    def localStr(self, local_addr=None, local_port=None):
        s = ''
        if len(self.media_lines_lines) == 1 and self.media_lines_lines[0].c_header is not None:
            for name in self.first_half:
                header = getattr(self, name + '_header')
                if header is not None:
                    s += '{}={}\r\n'.format(name,
                                            header.localStr(local_addr, local_port))
            s += 'c=%s\r\n' % self.media_lines_lines[0].c_header.localStr(
                local_addr, local_port)
            for name in self.second_half:
                header = getattr(self, name + '_header')
                if header is not None:
                    s += '{}={}\r\n'.format(name,
                                            header.localStr(local_addr, local_port))
            for header in self.a_headers:
                s += 'a=%s\r\n' % str(header)
            s += self.media_lines_lines[0].localStr(
                local_addr, local_port, noC=True)
            return s
        # Special code to optimize for the cases when there are many media streams pointing to
        # the same IP. Only include c= header into the top section of the SDP and remove it from
        # the streams that match.
        optimize_c_headers = False
        if len(self.media_lines_lines) > 1 and self.c_header == None and self.media_lines_lines[0].c_header != None and \
                self.media_lines_lines[0].c_header.localStr(local_addr, local_port) == self.media_lines_lines[1].c_header.localStr(local_addr, local_port):
            # Special code to optimize for the cases when there are many media streams pointing to
            # the same IP. Only include c= header into the top section of the SDP and remove it from
            # the streams that match.
            optimize_c_headers = True
            media_lines_0_str = self.media_lines_lines[0].c_header.localStr(
                local_addr, local_port)
        if optimize_c_headers:
            for name in self.first_half:
                header = getattr(self, name + '_header')
                if header is not None:
                    s += '{}={}\r\n'.format(name,
                                            header.localStr(local_addr, local_port))
            s += 'c=%s\r\n' % media_lines_0_str
            for name in self.second_half:
                header = getattr(self, name + '_header')
                if header is not None:
                    s += '{}={}\r\n'.format(name,
                                            header.localStr(local_addr, local_port))
        else:
            for name in self.all_headers:
                header = getattr(self, name + '_header')
                if header is not None:
                    s += '{}={}\r\n'.format(name,
                                            header.localStr(local_addr, local_port))
        for header in self.a_headers:
            s += 'a=%s\r\n' % str(header)
        for section in self.media_lines_lines:
            if optimize_c_headers and section.c_header != None and \
                    section.c_header.localStr(local_addr, local_port) == media_lines_0_str:
                s += section.localStr(local_addr, local_port, noC=True)
            else:
                s += section.localStr(local_addr, local_port)
        return s

    def __iadd__(self, other):
        if len(self.media_lines_lines) > 0:
            self.media_lines_lines[-1].addHeader(*other.strip().split('=', 1))
        else:
            self.addHeader(*other.strip().split('=', 1))
        return self

    def getCopy(self):
        return SdpBody(cself=self)

    def addHeader(self, name, header):
        if name == 'a':
            self.a_headers.append(a_header(header))
        else:
            setattr(self, name + '_header', f_types[name](header))
