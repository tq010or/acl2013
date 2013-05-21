#!/usr/bin/env python
"""
This module includes self-contained common utilities
"""


def most_freq_item(input_list):
    assert(input_list)
    freq_dict = dict()
    for item in input_list:
        try:
            freq_dict[item] += 1
        except KeyError:
            freq_dict[item] = 1
    sorted_list = sorted(freq_dict.items(), key = lambda k: k[1], reverse = True)
    return sorted_list[0][0].decode("utf-8")


