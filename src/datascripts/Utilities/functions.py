__author__ = 'thodrek'

import numpy as np
import random

def sampleCDF(values, probs, size):
    seeds = [random.random() for i in range(size)]
    sample = []
    for s in seeds:
        indx = 0
        while indx < len(probs):
            if probs[indx] > s:
                break
            indx += 1
        value = probs[indx-1]
        indx = 0
        for indx in range(len(probs)):
            if probs[indx] == value:
                break
        sample.append(values[indx])
    return sample


def skewness(sample):
    mean = np.mean(sample)
    n = float(len(sample))
    numerator = 0.0
    denom = 0.0
    for i in sample:
        numerator += (i - mean)**3
        denom += (i - mean)**2

    numerator = numerator/n
    denom = (denom/(n-1))**(3.0/2.0)
    return numerator/denom

