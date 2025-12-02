import random

def weighted_random(choices, weights):
    total = sum(weights)
    r = random.uniform(0, total)
    upto = 0
    for c, w in zip(choices, weights):
        if upto + w >= r:
            return c
        upto += w
    return choices[-1]
