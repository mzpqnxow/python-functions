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


    What this snippet contains:

    - An OrederedDict YaML loader, for preserving order of YaML files
    - A nested/two-pass Jinja2 templating function working on any type of object

    Very useful in configuration files written in YaML that require re-use of values which
    is better solved using variables within the YaML. The `nested_template` function permits
    the following transformation, as an example:

    Example input file:
    --- start input.yml ---
        user: someuser
        root: /home/{{ user }}
        appname: myapp
        appversion: 1.2
        app_path: "{{ root }}/{{ appname }}-{{ appversion }}"
        test:
          - "{{ root }} {{ appname }}"
        # Sequences (equivalent to lists or arrays) look like this:
        more:
          - Item 1
          - 0.5
          - key: "{{ root }}"
            another_key: "{{ appname }}"
          -
            - This is a sequence
            - inside another sequence with {{ root }}
    --- end input.yml ---

    Example output:
        {
        "user": "someuser",
        "root": "/home/someuser",
        "appname": "myapp",
        "appversion": 1.2,
        "app_path": "/home/someuser/myapp-1.2"
        }

    You can see the YaML file is loaded once and then used as the source
    of variables for another pass against the contents of the YaML file.
"""
from __future__ import print_function, unicode_literals
from collections import OrderedDict
from json import dumps as json_print
from re import search as regex_search

from jinja2 import Template
from yaml import load as load_yaml_plain


def json_pretty(obj):
    """Print an object with standard types neatly"""
    print(json_print(obj, indent=2))


def nested_template(data, template_vars):
    """data is an arbitrary data structure, template_vars is a dict

    The `data` object is traversed and each instance of a Jinja2 variable
    that is found in template_vars is replaced (templated)

    This is a recursive function with the end-case being when the object is
    a simple string or unicode string type
    """

    if isinstance(data, (str, unicode)):
        tmpl = Template(data)
        data = tmpl.render(template_vars)
        return data
    elif isinstance(data, dict):
        for key, value in data.iteritems():
            data[key] = nested_template(value, template_vars)
        return data
    elif isinstance(data, list):
        # Not supporting sets and tuples since YaML doesn't support them
        tmp_list = []
        data.reverse()
        while data:
            item = data.pop()
            item = nested_template(item, template_vars)
            tmp_list.append(item)
        return tmp_list
    elif isinstance(data, (int, float)):
        return data
    raise RuntimeError('unexpected and unsupported type "{}" encountered'.format(
        type(data)))


def load_yaml_ordered(filename):
    """Load a YaML file as an OrderedDict

    Inspired by StackOverflow

    This function loads a YaML file, preserving order. It also
    detects duplicates of keys
    """
    with open(filename, 'r') as filefd:
        lines = filefd.read().splitlines()
        top_keys = []
        duped_keys = []
        for line in lines:
            match = regex_search(r'^([A-Za-z0-9_]+) *:', line)
            if match:
                if match.group(1) in top_keys:
                    duped_keys.append(match.group(1))
                else:
                    top_keys.append(match.group(1))
        if duped_keys:
            raise RuntimeError('ERROR: duplicate keys: {}'.format(duped_keys))
    with open(filename, 'r') as filefd:
        d_tmp = load_yaml_plain(filefd)
    return OrderedDict([(key, d_tmp[key]) for key in top_keys])


def main():
    """Driver"""
    data = load_yaml_ordered("test.yml")
    print('--- Before ---')
    json_pretty(data)
    print('')
    template_input_vars = data
    resolved = nested_template(data, template_input_vars)
    print('--- After ---')
    json_pretty(resolved)


if __name__ == '__main__':
    main()
