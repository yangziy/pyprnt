#!/usr/local/bin/python3

"""
Trimmed version of pyprnt for my own purpose
All credit goes to the original author

Original License >>>

MIT License

Copyright (c) 2019 Kevin Kim
https://github.com/kevink1103/pyprnt

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
from collections import Mapping, Sequence

import numpy as np


def safe_str(obj, newline_repr='\\n'):
    if isinstance(obj, np.ndarray):
        s = str(obj).replace('\n', ',')
    else:
        s = str(obj).replace('\n', newline_repr)

    return s


def create_border(position, label, value):
    if position == "top":
        return "┌" + "─" * (label) + "┬" + "─" * (value) + "┐"
    elif position == "bottom":
        return "└" + "─" * (label) + "┴" + "─" * (value) + "┘"


def create_lines(key: str, key_width, value: str, value_width):
    output = []
    while len(value) != 0:
        new_value = value[:value_width]
        output.append("│{}│{}│".format(key.ljust(key_width), new_value.ljust(value_width)))

        key = ''
        value = value[value_width:]
    return output


def create_block(obj, width):
    """
    Args:
        obj: Mapping
        width: int, should be larger or equal to 5

    Returns:
        List[str]
    """

    if isinstance(obj, Sequence) and not isinstance(obj, str):
        obj = {idx: elem for idx, elem in enumerate(obj)}

    assert isinstance(obj, Mapping)
    assert width >= 5

    # Calculate layout
    half_width = width // 2 - 1
    max_label_width = max([len(safe_str(key)) for key in obj.keys()])
    key_width = min(max_label_width, half_width)

    max_value_length = max([len(safe_str(val)) for val in obj.values()])
    val_width = min(max_value_length, width - key_width - 3)  # Max allowed space for value

    # Prepare output
    output = []
    top_border = create_border("top", key_width, val_width)
    bottom_border = create_border("bottom", key_width, val_width)
    output.append(top_border)

    for key, val in obj.items():
        key_s = safe_str(key)
        key_s = key_s if len(key_s) <= key_width else key_s[:key_width - 3] + '...'  # truncate if key is too long

        val_s = safe_str(val)
        if isinstance(val, (Sequence, Mapping)) and not isinstance(val, str) and len(val_s) >= val_width >= 5:
            lines = create_block(val, width=val_width)

            for j, line in enumerate(lines):
                if j > 0: key_s = " " * len(key_s)
                output.append("│{}│{}│".format(key_s.ljust(key_width), line))
        else:
            output += create_lines(key_s, key_width, val_s, val_width)

    output.append(bottom_border)
    output = tailor_output(output)
    return output


def tailor_output(output):
    if not isinstance(output, list):
        return output

    top_border = output[0]
    bottom_border = output[len(output) - 1]
    max_width = 0

    # Skip very first and very last
    for i in range(1, len(output) - 1):
        row = output[i]
        if len(row) >= max_width:
            max_width = len(row)

    diff = max_width - len(top_border)

    if diff >= 0:
        top_border = top_border[:-1]
        top_border += "─" * (diff)
        top_border += "┐"
        bottom_border = bottom_border[:-1]
        bottom_border += "─" * (diff)
        bottom_border += "┘"
        output[0] = top_border
        output[len(output) - 1] = bottom_border
    else:
        top_border = top_border[:diff - 1]
        top_border += "─" * (diff)
        top_border += "┐"
        bottom_border = bottom_border[:diff - 1]
        bottom_border += "─" * (diff)
        bottom_border += "┘"
        output[0] = top_border
        output[len(output) - 1] = bottom_border

    for i in range(1, len(output) - 1):
        row = output[i]
        diff = max_width - len(row)
        if diff > 0:
            output[i] = row[:-1] + (" " * (diff)) + "│"

    return output


def prnt(obj, width=150, *args, **kwargs):
    print('\n'.join(create_block(obj, width)), *args, **kwargs)
