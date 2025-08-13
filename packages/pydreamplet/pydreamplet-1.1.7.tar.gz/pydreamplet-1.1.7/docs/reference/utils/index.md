---
icon: material/tools
---

# Helper functions

This module provides utility functions for various mathematical operations and unit conversions. It includes functions for rounding numbers using a round half up method, constraining values within a specified range, converting between degrees and radians, and generating rounded tick values for grid lines.

## <span class="func"></span>`math_round`

```py
math_round(x)
```

Rounds `x` to the nearest integer using the round half up method.

<span class="param">**Parameters**</span>

- `x` *(float)*: The number to round.

<span class="returns">**Returns**</span>

*(int)*: The rounded integer.

```py
print(math_round(3.4))  # Output: 3
print(math_round(3.6))  # Output: 4
```

## <span class="func"></span>`constrain`

```py
constrain(value, min_val, max_val)
```

Constrains the given `value` between `min_val` and `max_val`.

<span class="param">**Parameters**</span>

- `value` *(numeric)*: The value to be constrained.
- `min_val` *(numeric)*: The minimum allowed value.
- `max_val` *(numeric)*: The maximum allowed value.

<span class="returns">**Returns**</span>

*(numeric)*: The constrained value.

```py
print(constrain(10, 0, 5))  # Output: 5
print(constrain(-3, 0, 5))  # Output: 0
```

## <span class="func"></span>`radians`

```py
radians(degrees)
```

Converts an angle from degrees to radians.

<span class="param">**Parameters**</span>

- `degrees` *(float)*: Angle in degrees.

<span class="returns">**Returns**</span>

*(float)*: Angle in radians.

```py
print(radians(180))  # Output: 3.141592653589793 (approximately)
```

## <span class="func"></span>`degrees`

```py
degrees(radians)
```

Converts an angle from radians to degrees.

<span class="param">**Parameters**</span>

- `radians` *(float)*: Angle in radians.

<span class="returns">**Returns**</span>

*(float)*: Angle in degrees.

```py
print(degrees(3.141592653589793))  # Output: 180.0
```

## <span class="func"></span>`calculate_ticks`

```py
calculate_ticks(min_val, max_val, num_ticks=5, below_max=True)
```

Generates a list of rounded tick values between `min_val` and `max_val`. The number of ticks is approximately equal to `num_ticks`.

<span class="param">**Parameters**</span>

- `min_val` *(float)*: The minimum value.
- `max_val` *(float)*: The maximum value.
- `num_ticks` *(int, optional)*: The desired number of tick values (default: 5).
- `below_max` *(bool)*: If set to `True` last tick is always below `max_val`. Default: `True`

<span class="returns">**Returns**</span>

*(list[int])*: A list of rounded tick values.

Raises `ValueError`: If min_val is not less than max_val.

```py
ticks = calculate_ticks(0, 100, num_ticks=5)
print(ticks)  # Example output: [0, 20, 40, 60, 80, 100]
```

## <span class="func"></span>`pie_angles`

```py
pie_angles(values, start_angle=0, end_angle=360)
```

Calculates the start and end angles (in degrees) for each pie slice based on their proportional values. The function divides the specified angle span among the slices in proportion to their values.

<span class="param">**Parameters**</span>

- `values` *(list[int | float])*: A list of numerical values representing the sizes of each pie slice.
- `start_angle` *(int | float, optional)*: The starting angle (in degrees) for the first slice (default: 0).
- `end_angle` *(int | float, optional)*: The ending angle (in degrees) for the last slice (default: 360).

<span class="returns">**Returns**</span>

*(list[tuple[float, float]])*: A list of tuples where each tuple contains the start and end angles for a slice.

Raises `ZeroDivisionError`: If the sum of `values` is zero.

```py
angles = pie_angles([1, 2, 3])
print(angles)  
# [(0, 60.0), (60.0, 180.0), (180.0, 360.0)]

# Creating a semicircle pie chart
semi_angles = pie_angles([1, 2, 3], end_angle=180)
print(semi_angles)
# [(0, 30.0), (30.0, 90.0), (90.0, 180.0)]
```

```py title="Usage example"
import pydreamplet as dp
from pydreamplet.shapes import ring
from pydreamplet.utils import pie_angles
from pydreamplet.colors import generate_colors

data = [25, 34, 18, 72]

svg = dp.SVG(400, 400)
g = dp.G(pos=dp.Vector(svg.w / 2, svg.h / 2))
svg.append(g)

segments = pie_angles(sorted(data, reverse=True), -90)
colors = generate_colors("#db45f9", len(segments))

for i, segment in enumerate(segments):
    g.append(dp.Path(
        d=ring(0, 0, inner_radius=50, outer_radius=150, start_angle=segment[0], end_angle=segment[1]),
        fill=colors[i]
    ))

svg.display()
```

![Result](assets/pie_chart.svg){.img-light-dark-bg}

## <span class="func"></span>`sample_uniform`

```py
sample_uniform(my_list, n, precedence="first")
```

Selects uniformly spaced indices from a list based on the total number of items, the desired number of selections, and an optional anchoring (precedence) parameter. The function returns a tuple of indices chosen from the list such that they are as evenly distributed as possible.

<span class="param">**Parameters**</span>

- `input_list` *(list[Any])*: A list containing elements of any type.
- `n` *(int)*: The number of indices to select from the list.
- `precedence` *(str | None, optional)*: Determines which end of the list is anchored during sampling. Use `"first"` (default) to always include the first element, `"last"` to always include the last element, or `None` for an unanchored, balanced selection.

<span class="returns">**Returns**</span>

*(tuple[int])*: A tuple of indices representing the uniformly spaced positions within the list.

Raises `ValueError`: If precedence is not `"first"`, `"last"`, or `None`.

```py
# With "first" precedence (anchoring the first element):
indices = sample_uniform(["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"], n=4, precedence="first")
print(indices)  # Expected output: (0, 3, 6, 9)

# With "last" precedence (anchoring the last element):
indices = sample_uniform(["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"], n=3, precedence="last")
print(indices)  # Expected output: (1, 5, 9)

# With no precedence (balanced selection):
indices = sample_uniform(["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l"], n=4, precedence=None)
print(indices)  # Expected output: (1, 3, 7, 10)
```

## <span class="func"></span>`force_distance`

```py
force_distance(values, distance)
```

Adjusts an unsorted list of numeric label positions so that the spacing between adjacent labels is at least the specified distance. The function ensures that each adjusted label remains within ±distance/2 of its original value while keeping the new positions as close as possible to the input values. Internally, the input list is sorted for processing, and the computed positions are then re-mapped to match the original order.

<span class="param">**Parameters**</span>

- `values` *(list[float])*: A sorted list of original numeric label positions.
- `distance` *(float)*: The minimum required distance between adjacent labels. Each label can shift within the interval `[v - distance/2, v + distance/2]` relative to its original position.

<span class="returns">**Returns**</span>

*(list[float])*: A list of adjusted label positions that meet the minimum spacing requirement, returned in the same order as the input list.

```py
input_values = [2, 6, 7, 8, 10, 16, 18]
adjusted_positions = force_distance(input_values, distance=2)
print(adjusted_positions)  # Expected output: [2, 5, 7, 9, 11, 16, 18]
```

Internally, the function reformulates each position as `x[i] = y[i] + i * distance`, which reduces the spacing constraint to requiring that the sequence `y` is non-decreasing. A pooling algorithm is then applied to adjust the values while ensuring each remains within its allowed interval.
