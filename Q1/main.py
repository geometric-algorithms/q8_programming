import sys
import matplotlib.pyplot as plt
import itertools
from collections import defaultdict
import numpy as np
import matplotlib.cm as cm
import warnings
warnings.filterwarnings("ignore")

def read_points(file_path):
    points = []
    with open(file_path, 'r') as f:
        for i, line in enumerate(f, 1):
            parts = line.strip().split()
            if len(parts) != 2:
                # print(f"Warning: Skipping invalid line {i}: {line.strip()}")
                continue
            try:
                x, y = map(float, parts)
                points.append((x, y))
            except ValueError:
                print(f"Warning: Could not convert line {i} to float: {line.strip()}")
    return points

def dual_line(point):
    x, y = point
    # Dual of point (a,b) is line y = ax - b
    return (x, -y)  # Represented as slope and intercept

def find_intersections_and_collinear(pts):
    duals = [dual_line(pt) for pt in pts]
    intersection_dict = defaultdict(set)

    for (i1, (a1, b1)), (i2, (a2, b2)) in itertools.combinations(enumerate(duals), 2):
        if a1 == a2:
            continue  # parallel lines, no intersection
        x_int = (b2 - b1) / (a1 - a2)
        y_int = a1 * x_int + b1
        key = (round(x_int, 8), round(y_int, 8))
        intersection_dict[key].add(i1)
        intersection_dict[key].add(i2)

    max_collinear = max(intersection_dict.values(), key=len, default=set())
    collinear_points = [pts[i] for i in max_collinear]

    return collinear_points, duals, intersection_dict

def plot_primal_and_dual(primal_points, duals, intersections, collinear_points, input_file):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

    cmap = cm.get_cmap("tab10", len(primal_points))
    all_x, all_y = [], []

    # --- Left Plot: Primal Points ---
    for i, pt in enumerate(primal_points):
        color = cmap(i)
        all_x.append(pt[0])
        all_y.append(pt[1])
        ax1.plot(pt[0], pt[1], 'o', color=color)
        ax1.text(pt[0]+0.1, pt[1], f"{pt}", fontsize=8, color=color)

    ax1.set_title("Primal Points")
    ax1.set_aspect('equal')
    ax1.grid(True)

    # Extend x and y range slightly
    x_margin = (max(all_x) - min(all_x)) * 0.2
    y_margin = (max(all_y) - min(all_y)) * 0.1
    ax1.set_xlim(min(all_x) - x_margin, max(all_x) + x_margin)
    ax1.set_ylim(min(all_y) - y_margin, max(all_y) + y_margin)

    # --- Right Plot: Dual Lines and Intersections ---
    x_vals = np.linspace(-10, 10, 500)
    all_dual_y = []

    for i, (a, b) in enumerate(duals):
        y_vals = a * x_vals + b
        color = cmap(i)
        ax2.plot(x_vals, y_vals, color=color, linewidth=1)
        all_dual_y.extend(y_vals)

    # Plot intersections
    if intersections:
        ix, iy = zip(*intersections.keys())
        ax2.plot(ix, iy, 'ro', label='Intersections')
        all_dual_y.extend(iy)

    ax2.set_title("Dual Lines and Intersections")
    ax2.set_aspect('auto')
    ax2.grid(True)

    # Extend y-axis for dual plot
    y_margin_dual = (max(all_dual_y) - min(all_dual_y)) * 0.1
    ax2.set_ylim(min(all_dual_y) - y_margin_dual, max(all_dual_y) + y_margin_dual)

    # Add legend with primal point info
    for i, pt in enumerate(primal_points):
        ax2.text(1.02, 0.98 - i * 0.05, f"{pt}", transform=ax2.transAxes,
                 fontsize=10, color=cmap(i), ha='left', va='top')

    ax2.legend()

    # Save output
    image_filename = f"{input_file.split('.')[0]}.png"
    plt.tight_layout()
    plt.savefig(image_filename)
    print(f"Plot saved as {image_filename}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 main.py <filename>")
        sys.exit(1)

    filename = sys.argv[1]
    primal_points = read_points(filename)
    collinear_points, duals, intersections = find_intersections_and_collinear(primal_points)

    print("\nMax subset of collinear points:")
    for pt in collinear_points:
        print(pt)

    plot_primal_and_dual(primal_points, duals, intersections, collinear_points, filename)
