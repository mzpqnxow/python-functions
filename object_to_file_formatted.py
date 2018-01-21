#!/usr/bin/env python
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


    Function for dumping objects to files of different formats. The following are supported:
        - JSON (JSON)
        - CSV (comma separated value w/optional column header row)
        - LST (raw list of ASCII strings, one per line)


    Example invocation:
        obj = ["a", "b", "c"]
        to_file('out.lst', obj)
    Example output:
        --- out.lst ---
        a
        b
        c
        --- out.lst ---

    Example invocation:
        obj = ["a", "b", "c"]
        to_file('out.json', obj)
    Example output:
        --- out.json ---
        ["a", "b", "c"]
        --- out.json ---

    Example invocation:
        obj = ["a", "b", "c"]
        to_file('out.csv', obj, csv_fields=['col1', 'col2', 'col3'])
    Example output:
        --- out.csv ---
        col1, col2, col3
        a, b, c
        --- out.csv ---


"""
from __future__ import unicode_literals, print_function


from csv import (
    DictWriter as CSVDictWriter,
    writer as CSVWriter)
from json import dump as json_dump


def to_file(dest, obj, csv_fields=None, uniq=True, filter_blanks=True, silent=False):
    """
    Dump to a file based on extension
    If .json, do a standard JSON dump() to the file
    If .csv, emit a CSV file, optionally with field names
    If .lst, emit a raw list of ASCII items, one per line

    The format emitted is determined by the destination file extension
    Object can be anything for JSON
    Object must be a sequence for CSV
    Object must be a sequence for LST
    """
    try:
        write_stream = open(dest, 'wb')
    except OSError as err:
        print(err)
        raise

    if dest.endswith('.json'):
        # Basic JSON dump
        json_dump(obj, write_stream, sort_keys=False)
    elif dest.endswith('.csv'):
        # Write out a plain CSV file, or one with a header if csv_fields is
        # specified
        if isinstance(obj, (set, tuple, list)) is False:
            raise RuntimeError(
                'ERROR: csv files must be generated from a list/tuple/set')
        obj_len = len(obj)
        if obj_len and isinstance(obj[0], dict):
            csv_fields = obj[0].keys()
        if csv_fields is not None:
            writer = CSVDictWriter(write_stream, fieldnames=csv_fields)
            writer.writeheader()
        else:
            writer = CSVWriter(write_stream)
        for row in obj:
            if obj is None:
                continue
            if csv_fields is not None:
                if isinstance(row, dict):
                    row = {k.encode('utf-8'): v.encode(
                        'utf-8') for k, v in row.iteritems()}
                    # new_row[k.encode('utf-8')] = v.encode('utf-8')
                    writer.writerow(row)
                elif csv_fields is not None:
                    writer.writerow(dict(zip(csv_fields, row)))
                else:
                    raise RuntimeError('unknown type for row')
            else:
                writer.writerow(row)
    elif dest.endswith('.lst'):
        if isinstance(obj, (set, tuple, list)) is False:
            raise RuntimeError('ERROR: raw/.lst dump object must be set/tuple/list')
        if uniq is True:
            obj = set(obj)
        for row in obj:
            if isinstance(obj, (str, unicode)) is False:
                raise RuntimeError(
                    'ERROR: raw/.lst files must be list of strings')
            if filter_blanks is True and row.strip() == '':
                continue
            write_stream.write(row + '\n')
    else:
        # Unknown extension, assume list of strings
        print('WARN: unknown file extension, dumping as list of strings')
        for row in obj:
            if not isinstance(row, str):
                raise RuntimeError(
                    'ERROR: lst files must be list of strings')
            write_stream.write(row.strip() + '\n')
    write_stream.close()
    if silent is False:
        print('--- Object dumped to file %s ...' % (dest))
