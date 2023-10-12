#!/usr/bin/python3
# -*- coding: utf-8 -*-

def get_biases_from_file(path: str):
    """
    Helper function to read bias from a file
    """
    biases = {}
    try:
        biases_file = open(path, 'r')
    except IOError:
        print("Cannot open bias file: " + path)
    else:
        for line in biases_file:

            # Skip lines starting with '%': comments
            if line.startswith('%'):
                continue

            # element 0 : value
            # element 1 : name
            split = line.split("%")
            biases[split[1].strip()] = int(split[0])
    return biases


def save_biases_to_file(path: str, biases: dict):
    """
    helper function to write biases to file
    """
    try:
        f = open(path, 'w')
    except IOError:
        print("Cannot save bias file: " + path)
    else:
        for name, value in biases.items():
            f.write(str(value) + " % " + name + "\n")
