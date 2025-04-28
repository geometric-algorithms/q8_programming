import sys
import matplotlib.pyplot as plt

# Point class
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

# Read points from a file
def read_points(filename, skip_first_line=False):
    points = []
    with open(filename, 'r') as f:
        if skip_first_line:
            f.readline()  # Skip the first line
        for line in f:
            if line.strip():
                x, y = map(float, line.strip().split())
                points.append(Point(x, y))
    return points

# Compute triangle area using determinant formula
def triangle_area(p1, p2, p3):
    return abs((p1.x * (p2.y - p3.y) +
                p2.x * (p3.y - p1.y) +
                p3.x * (p1.y - p2.y)) / 2.0)

# Generate all unique triangles from a list of points
def brute_force_triangles(points):
    triangles = []
    n = len(points)
    for i in range(n):
        for j in range(i + 1, n):
            for k in range(j + 1, n):
                triangles.append([points[i], points[j], points[k]])
    return triangles

# Plot the given triangle and all triangles with min area side by side
def plot_given_and_min_area_triangles(points, given_triangle, min_area_triangles):
    num_plots = 1 + len(min_area_triangles)
    fig, axs = plt.subplots(1, num_plots, figsize=(5 * num_plots, 5))
    if num_plots == 1:
        axs = [axs]

    def plot(ax, triangle_points, title, color):
        xs = [p.x for p in points]
        ys = [p.y for p in points]
        ax.scatter(xs, ys, color='blue', label='Points')

        tri_xs = [p.x for p in triangle_points] + [triangle_points[0].x]
        tri_ys = [p.y for p in triangle_points] + [triangle_points[0].y]
        ax.plot(tri_xs, tri_ys, color=color, linewidth=2, label='Triangle')

        ax.set_title(title)
        ax.set_aspect('equal', adjustable='box')
        ax.grid(True)

    # Plot the given triangle
    plot(axs[0], given_triangle, "Given Triangle", 'red')

    # Plot all min-area triangles
    for i, tri in enumerate(min_area_triangles):
        plot(axs[i + 1], tri, f"Min Area Triangle {i+1}", 'green')

    plt.tight_layout()
    output_image = sys.argv[2].replace('.txt', '_comparison.png')
    plt.savefig(output_image)
    print(f"Saved figure to {output_image}")
    plt.show()

# Main script
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python q2.py <input_file> <output_file>")
        sys.exit(1)

    # Read input files
    points_filename = sys.argv[1]
    triangle_filename = sys.argv[2]

    points = read_points(points_filename, skip_first_line=True)
    triangle_points = read_points(triangle_filename)

    # Generate all triangles from the point set
    triangles = brute_force_triangles(points)

    # Find all triangles with the smallest non-zero area
    min_area = float('inf')
    min_area_triangles = []

    for triangle in triangles:
        area = triangle_area(*triangle)
        if area == 0:
            continue
        if area < min_area:
            min_area = area
            min_area_triangles = [triangle]
        elif abs(area - min_area) < 1e-9:
            min_area_triangles.append(triangle)

    # Compute area of the given triangle
    given_area = triangle_area(*triangle_points)

    # Output triangle area info
    print(f"Area of the given triangle: {given_area}")
    print(f"Minimum triangle area: {min_area}")
    print(f"Number of triangles with min area: {len(min_area_triangles)}")

    # Plot the given and min area triangles side by side
    plot_given_and_min_area_triangles(points, triangle_points, min_area_triangles)
