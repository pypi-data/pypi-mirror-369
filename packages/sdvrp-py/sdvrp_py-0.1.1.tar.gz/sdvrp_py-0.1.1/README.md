# sdvrp-py

<p>
    <a href="https://pypi.org/project/sdvrp-py/"><img src="https://img.shields.io/pypi/v/sdvrp-py"/></a>
    <a href="https://crates.io/crates/sdvrp"><img src="https://img.shields.io/crates/v/sdvrp" alt="crates.io"></a>
    <a href="https://docs.rs/sdvrp/"><img src="https://docs.rs/sdvrp/badge.svg" alt="docs"></a>
    <a href="https://github.com/HellOwhatAs/sdvrp-py/"><img src="https://img.shields.io/github/languages/top/HellOwhatAs/sdvrp-py"></a>
</p>

Python binding of Rust binding of [Alkaid-SDVRP](https://github.com/HUST-Smart/Alkaid-SDVRP): An Efficient Open-Source Solver for the Vehicle Routing Problem with Split Deliveries.

## Install
```
pip install sdvrp-py
```

> If there are no precompiled wheels suitable for your platform, you need to [install Rust](https://www.rust-lang.org/tools/install) before running `pip install sdvrp-py`.

## Example
```py
import sdvrp_py
import matplotlib.pyplot as plt

# fmt: off
demands=[
    18, 26, 11, 30, 21, 19, 15, 16, 29, 26, 37, 16, 12, 31, 8, 19, 20,
    13, 15, 22, 28, 12, 6, 27, 14, 18, 17, 29, 13, 22, 25, 28, 27, 19,
    10, 12, 14, 24, 16, 33, 15, 11, 18, 17, 21, 27, 19, 20, 5, 22, 12,
    19, 22, 16, 7, 26, 14, 21, 24, 13, 15, 18, 11, 28, 9, 37, 30, 10,
    8, 11, 3, 1, 6, 10, 20
]
coord_list=[
    (40, 40), (22, 22), (36, 26), (21, 45), (45, 35), (55, 20), (33, 34),
    (50, 50), (55, 45), (26, 59), (40, 66), (55, 65), (35, 51), (62, 35),
    (62, 57), (62, 24), (21, 36), (33, 44), (9, 56), (62, 48), (66, 14),
    (44, 13), (26, 13), (11, 28), (7, 43), (17, 64), (41, 46), (55, 34),
    (35, 16), (52, 26), (43, 26), (31, 76), (22, 53), (26, 29), (50, 40),
    (55, 50), (54, 10), (60, 15), (47, 66), (30, 60), (30, 50), (12, 17),
    (15, 14), (16, 19), (21, 48), (50, 30), (51, 42), (50, 15), (48, 21),
    (12, 38), (15, 56), (29, 39), (54, 38), (55, 57), (67, 41), (10, 70),
    (6, 25), (65, 27), (40, 60), (70, 64), (64, 4), (36, 6), (30, 20),
    (20, 30), (15, 5), (50, 70), (57, 72), (45, 42), (38, 33), (50, 4),
    (66, 8), (59, 5), (35, 60), (27, 24), (40, 20), (40, 37)
]
# fmt: on

result = sdvrp_py.solve_sdvrp(
    capacity=140,
    demands=demands,
    coord_list=coord_list,
    time_limit=10.0,
)

print(result)

plt.scatter(
    [coord[0] for coord in coord_list],
    [coord[1] for coord in coord_list],
    c="blue",
    label="Customers",
)
for route in result:
    route = [(0, 0), *route, (0, 0)]
    x = [coord_list[i][0] for i, _ in route]
    y = [coord_list[i][1] for i, _ in route]
    plt.plot(x, y, marker=None)

plt.show()
```
Output: _`(node, load)`_
```py
[
    [(17, 4), (3, 11), (44, 17), (50, 22), (18, 13), (55, 7), (25, 14), (31, 25), (10, 26), (72, 1)],
    [(26, 11), (58, 21), (38, 24), (65, 9), (66, 37), (11, 37)],
    [(6, 12), (73, 6), (1, 18), (43, 18), (41, 15), (42, 11), (64, 28), (22, 12), (62, 18), (2, 2), (68, 0)],
    [(30, 22), (74, 10), (21, 28), (61, 15), (28, 29), (2, 24), (68, 10)], 
    [(45, 21), (5, 21), (15, 8), (57, 14), (54, 16), (13, 12), (27, 17), (52, 19), (34, 0), (67, 1)],
    [(17, 16), (40, 33), (32, 28), (9, 29), (39, 16), (12, 16)],
    [(51, 12), (16, 19), (49, 5), (24, 27), (56, 26), (23, 6), (63, 11), (33, 27), (6, 7)],
    [(67, 29), (46, 27), (34, 19), (4, 25), (75, 20)],
    [(4, 5), (29, 13), (37, 14), (20, 22), (70, 11), (60, 13), (71, 3), (69, 8), (36, 12), (47, 19), (48, 20)],
    [(26, 7), (7, 15), (35, 10), (53, 22), (14, 31), (59, 24), (19, 15), (8, 16), (67, 0)]
]
```

![sdvrp](https://github.com/user-attachments/assets/6d16ee60-9a76-4969-a894-f481ed86bfb9)
