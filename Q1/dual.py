import matplotlib.pyplot as plt
from shapely.geometry import LineString, box
import numpy as np
import sys
import re

def dual_line(pt):
    a, b = pt
    return (a, -b)  # y = ax + b'

def intersection(l1, l2):
    a1, b1 = l1
    a2, b2 = l2
    if a1 == a2:
        return None
    x = (b2 - b1) / (a1 - a2)
    y = a1 * x + b1
    return (x, y)

def merge_envelopes(env1, env2, is_upper=True):
    merged = []
    i = j = 0
    while i < len(env1) and j < len(env2):
        if (is_upper and env1[i][0] < env2[j][0]) or (not is_upper and env1[i][0] > env2[j][0]):
            merged.append(env1[i])
            i += 1
        else:
            merged.append(env2[j])
            j += 1
    merged.extend(env1[i:])
    merged.extend(env2[j:])
    return merged

def compute_envelope(lines, is_upper=True):
    if len(lines) == 1:
        return [lines[0]]
    mid = len(lines) // 2
    left = compute_envelope(lines[:mid], is_upper)
    right = compute_envelope(lines[mid:], is_upper)
    return merge_envelopes(left, right, is_upper)

def compute_envelope_intersections(env):
    intersections = []
    for i in range(len(env) - 1):
        inter = intersection(env[i], env[i + 1])
        if inter:
            intersections.append(inter)
    return intersections

def clip_line(a, b, bbox):
    min_x, max_x, min_y, max_y = bbox
    line = LineString([(min_x, a * min_x + b), (max_x, a * max_x + b)])
    clipped = line.intersection(box(min_x, min_y, max_x, max_y))
    return clipped if not clipped.is_empty else None

def main():
    filename = sys.argv[1]  # e.g., 'test1.txt'
    match = re.search(r'\d+', filename)
    i = match.group() if match else "0"

    with open(filename, 'r') as f:
        lines = f.read().strip().split('\n')

    n = int(lines[0])
    points = [tuple(map(float, line.strip().split())) for line in lines[1:n+1]]

    duals = [dual_line(p) for p in points]
    duals_sorted = sorted(duals)

    upper_env = compute_envelope(duals_sorted, is_upper=True)
    lower_env = compute_envelope(duals_sorted, is_upper=False)

    upper_pts = compute_envelope_intersections(upper_env)
    lower_pts = compute_envelope_intersections(lower_env)

    all_pts = upper_pts + lower_pts
    xs, ys = zip(*all_pts)
    min_x, max_x = min(xs)-1, max(xs)+1
    min_y, max_y = min(ys)-1, max(ys)+1
    bbox = (min_x, max_x, min_y, max_y)

    # Clip and store segments
    segments = []
    for idx, (a, b) in enumerate(duals):
        seg = clip_line(a, b, bbox)
        if seg and isinstance(seg, LineString):
            coords = list(seg.coords)
            if len(coords) == 2:
                segments.append((coords[0], coords[1], idx))

    # Write segments to file
    with open(f"segs{i}.txt", 'w') as f:
        f.write(f"{len(segments)}\n")
        for (x1, y1), (x2, y2), _ in segments:
            f.write(f"{x1:.6f} {y1:.6f} {x2:.6f} {y2:.6f}\n")

if __name__ == "__main__":
    main()