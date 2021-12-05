# -*- coding: utf-8 -*-
"""
Created on Sun Jun  3 20:59:40 2018

@author: Roberto
"""

def trg_to_tuples(target_string):
    # TODO assert to check if target is valid
    repetitions = 0
    output = []
    for i, char in enumerate(target_string):
        if char.isdigit():
            repetitions = int(char)
        elif repetitions > 0:
            output.append((repetitions, char))
            repetitions = 0
        else:
            raise Exception('Target string does not match "2R2G" (number+letter) format')
    return output