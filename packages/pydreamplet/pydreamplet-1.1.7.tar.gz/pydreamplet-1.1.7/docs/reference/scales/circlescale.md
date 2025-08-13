# `CircleScale`

The `CircleScale` class maps an input value to a circle radius such that the circle’s area is linearly proportional to the input value. This ensures that if the area of a circle is meant to represent a value, the radius is calculated appropriately.

## <span class=class></span>`pydreamplet.scales.CircleScale`

```py
CircleScale(
    domain: tuple[float, float],
    output_range: tuple[float, float]
)
```

<span class="param">**Parameters**</span>

- `domain` *(tuple[float, float])*: The numeric input domain.
- `output_range` *(tuple[float, float])*: The desired radius range (rmin, rmax).

```py
circle_scale = CircleScale((0, 100), (5, 20))
print(circle_scale.map(50))  # Outputs the radius corresponding to the value 50
```

### <span class="meth"></span>`map`

```py
map(value: float) -> float
```

Maps the input value to a circle radius based on area proportionality.

### <span class="prop"></span>`domain`

Get or set the numeric domain.

### <span class="prop"></span>`output_range`

Get or set the radius range.
