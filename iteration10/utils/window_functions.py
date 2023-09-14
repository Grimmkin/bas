import dearpygui.dearpygui as dpg
from numpy import issubdtype, floating, integer, floor
from typing import Union, Tuple

def calculate_window_position_dimensions(
    width: Union[int, float] = 0.9,
    height: Union[int, float] = 0.9,
) -> Tuple[int, int, int, int]:
    assert (issubdtype(type(width), floating) and width > 0.0 and width < 1.0) or (
        issubdtype(type(width), integer) and width > 0
    )
    assert (issubdtype(type(height), floating) and height > 0.0 and height < 1.0) or (
        issubdtype(type(width), integer) and height > 0
    )
    viewport_width: int = dpg.get_viewport_width()
    x: int
    if issubdtype(type(width), floating):
        x = floor(viewport_width * (1.0 - width) / 2)
        width = floor(viewport_width * width)
    else:
        x = floor((viewport_width - width) / 2)
    viewport_height: int = dpg.get_viewport_height()
    y: int
    if issubdtype(type(height), floating):
        y = floor(viewport_height * (1.0 - height) / 2)
        height = floor(viewport_height * height)
    else:
        y = floor((viewport_height - height) / 2)
    return (
        int(x),
        int(y),
        int(width),
        int(height),
    )