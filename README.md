# Maximum Collinear Points and Minimum Area Triangle using Duality

## Problem Description

This project solves two computational geometry problems using **point-line duality**:

### (a) Maximum Subset of Collinear Points (Q1)
- **Input:** A set of `n` points in ℝ².
- **Output:** The largest subset of points in `P` that lie on a common line.
- **Approach:** Use point-line duality to transform points into lines and find the maximum collinear subset.

### (b) Minimum Area Triangle (Q2)
- **Input:** A set of `n` points in ℝ² in general position (no three points are collinear).
- **Output:** The triangle of minimum area formed by any three points.
- **Approach:** Use duality and efficient search to find the minimum area triangle.
- **Time Complexity:** O(n² log n)

---

## Running Instructions

## Running Q1

### Steps
```bash
python3 dual.py "test.txt"
python3 q1.py "segs.txt" "out.txt" "test.txt"
```

### Description

- **Input:**  
  `test.txt` contains:
  ```
  <number of points>
  x1 y1
  x2 y2
  ...
  ```
  Example:
  ```
  4
  1 2
  2 3
  3 1
  4 4
  ```

- **dual.py**:  
  - Reads `test.txt`.
  - Dualizes the points into lines.
  - Clips the lines inside a bounding box.
  - Writes resulting line segments into `segs.txt`.

- **segs.txt**:
  ```
  <number of line segments>
  x1 y1 x2 y2
  ...
  ```
  (Each line describes a segment by its two endpoints.)

- **q1.py**:  
  - Reads `segs.txt` and `test.txt`.
  - Processes the segments, finding intersections.
  - Writes all the points in the Max collinear subset into `out.txt`.

- **out.txt**:
  ```
  x y
  ...
  ```
  (Each line describes a resulting point.)

---

## Running Q2

### Steps
```bash
g++ q2.cpp
./a.out < "test.txt" > "points.txt"
python3 q2.py test.txt points.txt
```

### Description

- **Input:**  
  Same `test.txt` is used as in Q1.

- **q2.cpp**:  
  - Finds the set of three points that form the triangle of **minimum area**.
  - Outputs these three points into `points.txt`.

- **points.txt**:
  ```
  x1 y1
  x2 y2
  x3 y3
  ```
  (Coordinates of the three points forming the minimum-area triangle.)

- **q2.py**:
  - For visualizing the results.

---

## File Summary

| File         | Purpose                                    |
|--------------|--------------------------------------------|
| `test.txt`   | Input: Set of points.                      |
| `dual.py`    | Dualizes points, writes line segments.     |
| `segs.txt`   | Output: Line segments (dual plane).        |
| `q1.py`      | Processes segments, finding intersections and outputs Max subset of collinear points.     |
| `out.txt`    | Output: Max subset of collinear points.                  |
| `q2.cpp`     | Finds minimum area triangle.               |
| `points.txt` | Output: points forming a min area Triangle.                   |
| `q2.py`      | visualization              |

---

## Notes

- Make sure `python3` and `g++` are installed.
- Keep input/output filenames consistent (`test.txt`, `segs.txt`, `out.txt`, `points.txt`).
