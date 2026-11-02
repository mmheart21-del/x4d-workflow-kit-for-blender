"""Deterministic field and clone math; independent of Blender."""
import math
import random

def field_weight(kind, point, radius=1.0, invert=False, low=0.0, high=1.0, seed=0, index=0):
    r = max(abs(radius), 1e-6)
    if kind == 'SPHERE':
        v = 1 - math.sqrt(sum(x*x for x in point)) / r
    elif kind == 'BOX':
        v = 1 - max(abs(x) for x in point) / r
    elif kind == 'LINEAR':
        v = .5 + point[2] / (2*r)
    else:
        v = random.Random(seed + index * 104729).random()
    v = max(0., min(1., (v-low)/max(high-low, 1e-6)))
    return 1-v if invert else v

def blend_weight(a,b,mode):
    return max(0., min(1., {'ADD':lambda:a+b,'MULTIPLY':lambda:a*b,'MAX':lambda:max(a,b),'MIN':lambda:min(a,b),'SUBTRACT':lambda:a-b}[mode]()))

def positions(mode, count, spacing, radius):
    if mode == 'GRID':
        return [((x-(count[0]-1)/2)*spacing[0], (y-(count[1]-1)/2)*spacing[1], (z-(count[2]-1)/2)*spacing[2]) for z in range(count[2]) for y in range(count[1]) for x in range(count[0])]
    n=count[0]
    if mode == 'RADIAL':
        return [(radius*math.cos(i*2*math.pi/n),radius*math.sin(i*2*math.pi/n),0) for i in range(n)]
    return [(i*spacing[0],i*spacing[1],i*spacing[2]) for i in range(n)]
