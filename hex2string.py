#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
    Copyright 2018 copyright@mzpqnxow.com

    Redistribution and use in source and binary forms, with or without
    modification, are permitted provided that the following conditions are met:

    1. Redistributions of source code must retain the above copyright notice, this
       list of conditions and the following disclaimer.

    2. Redistributions in binary form must reproduce the above copyright notice, this
       list of conditions and the following disclaimer in the documentation and/or other
       materials provided with the distribution.

    3. Neither the name of the copyright holder nor the names of its contributors may be
       used to endorse or promote products derived from this software without specific
       prior written permission.

    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY
    EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
    OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT
    SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
    INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
    TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
    BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
    CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
    ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

    Function to import files from xxd, od, tcpdump -X, wireshark hex exports into a Python
    'raw' string. Useful when dealing with hex dumps from binary sources such
    as the network or executable files
"""

from __future__ import print_function, unicode_literals
from re import (
    sub as regex_sub,
    match as regex_match)
from binascii import a2b_hex as ascii_hex_to_binary

def ascii_hex_to_python(inbuf,
                        skip_bin_encode=False,
                        is_xxd=False,
                        is_od=False,
                        is_tcpdump=False,
                        is_wireshark=False):
    """
        Take as input inbuf, a newline delimited string consisting of the
        ASCII representation (in hex) of raw bytes from the od, xxd, tcpdump or
        wireshark tools' output format. Return either a clean ASCII hex stream
        or the binary/string version of the bytes as a Python variable
        Essentially, rip out metadata like offsets and other row prefixes that
        various tools use as garnish and just load the byte values.
        Input:
            inbuf (str): Newline delimited text ASCII hex dump
            skip_bin_encode (bool): If true, don't perform final conversion
            is_xxd (bool): If True, handle as an xxd string
            is_od (bool): If true, handle as an od string.
            is_tcpdump (bool): If true, handle as a tcpdump string
            is_wireshark (bool): If true, handle as a wireshark string
        Output:
            If skib_bin_encode is True, returns a stream of hex bytes, i.e.
            '414243444546'
            If skip_bin_encode is True, return raw bytes, i.e. 'ABCDEFG'
        Notes:
            To produce od output compatible with this function, use:
                $ od -A x -t x1z -v <filename>
            To produce xxd output compatible with this function, use:
                $ xxd <filename>
            To produce tcpdump output compatible with this function use:
                $ tcpdump -X -vvv
                ... copy and paste the buffer you want ...
            To produce wireshark output compatible with this function use:
                $ wireshark ...
                1. Choose a packet in the top pane, choose follow TCP stream.
                2. Select one direction of the stream from the dropdown box and
                   do NOT choose the "full" conversation, just one side
                3. Check 'hex' and save as
            This is most useful for:
                xxd, od: running on a third party hosts, a cheap way to copy
                         paste files into Python when you don't want to use
                         base64 or uuencode/uudecode
                tcpdump: when running on a remote host or even a local host but
                         you don't feel like parsing the cap file and you just
                         want to get a packet into Python quickly to manipulate
                wireshark: yeah, I don't know why you wouldn't just export raw
                           bytes, it seems much easier. But it's a similar regex
                           so might as well support it
        Errata:
            You will find this function will work with many types of hex dump formats
            so if you have one that isn't od, xxd, tcpdump or wireshark, you should
            try it out anyway. You might get lucky :>
    """

    def err(msg):
        from sys import stderr
        stderr.write(msg + '\n')

    if len(filter(lambda x: x is True, (is_od, is_tcpdump, is_wireshark, is_xxd))) != 1:
        raise RuntimeError('must choose one format')

    running_hex_buffer = ''
    for ascii_line in inbuf.split('\n'):
        if is_tcpdump is True:
            # Just copy/paste the hex that is flowing by
            hex_byte_line = regex_match(r'^ *0x' +
                                        r'([0-9a-fA-F]){1,8}' +
                                        r'(:){0,1}(\s)*' +
                                        r'(?P<data>(([0-9a-fA-F]{2})\s*)' +
                                        r'{1,16})',
                                        ascii_line)
        elif is_od is True:
            # od -A x -t x1z -v <filename>
            hex_byte_line = regex_match(r'^([0-9a-fA-F]){1,8} ' +
                                        r'(?P<data>(([0-9a-fA-F]{2})\s*)' +
                                        r'{1,16})',
                                        ascii_line)
        elif is_wireshark is True:
            # Follow stream, hex stream, save as (one side of conversation only)
            hex_byte_line = regex_match(r'^([0-9a-fA-F]){1,8}' +
                                        r'(:){0,1}(\s)*(?P<data>' +
                                        r'(([0-9a-fA-F]{2})\s*){1,16})',
                                        ascii_line)
        elif is_xxd is True:
            # xxd <filename>
            hex_byte_line = regex_match(r'^([0-9a-fA-F]){1,8}:' +
                                        r' ' +
                                        r'*(?P<data>(([0-9a-fA-F]{2})' +
                                        r'\s*){1,16})',
                                        ascii_line)
        else:
            raise RuntimeError('unknown hex ascii inpur format')
        if hex_byte_line is not None:
            running_hex_buffer += hex_byte_line.group('data')
        else:
            err('NO match on line: "%s"' % ascii_line)
    running_hex_buffer = regex_sub(r'\s+', '', running_hex_buffer)
    if skip_bin_encode is True:
        return running_hex_buffer
    return ascii_hex_to_binary(running_hex_buffer)


def main():
    """Driver"""
    from sys import argv
    if len(argv) != 2:
        print('Test suite for hex function ...')
        print('    Usage: %s <input file>' % (argv[0]))
        print()
        print('You will need to set flags like is_tcpdump yourself in code')
        exit(0)
    with open(argv[1], 'rb') as filefd:
        print(ascii_hex_to_python(filefd.read(), is_tcpdump=True))


if __name__ == '__main__':
    main()
