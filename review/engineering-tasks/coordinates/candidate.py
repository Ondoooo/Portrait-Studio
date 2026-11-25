"""Starter implementation. See README.md for the coordinate contract."""


def map_to_source(points, crop, orientation, target_size):
    """Return {label: (source_x, source_y)} for labeled points in the view."""
    left, top, right, bottom = crop
    width, height = right - left, bottom - top
    target_width, target_height = target_size
    if orientation == "cw90":
        view_width, view_height = height, width
    else:
        view_width, view_height = width, height

    x_scale = view_width / target_width
    y_scale = view_height / target_height
    result = {}
    for label, (view_x, view_y) in points.items():
        u, v = view_x * x_scale, view_y * y_scale
        if orientation == "cw90":
            x, y = view_y * x_scale, height - u
        elif orientation == "flip_x":
            x, y = width - u, v
        elif orientation == "identity":
            x, y = u, v
        else:
            raise ValueError(f"Unknown orientation: {orientation}")
        result[label] = (left + x, top + y)
    return result
