#!/usr/bin/env python
"""
Yet another stub-file for matplot-lib.
"""
from typing import List, Tuple, Dict, Optional


class ColorMap:
    """BaseClass."""


class ListedColormap(ColorMap):
    def __init__(self, color_list: List[Tuple[int, int, int]],
                 name: Optional[str] = None) -> None: ...


class LinearSegmentedColormap(ColorMap):
    def __init__(self, name: str,
                 color_dict: Dict[str,
                                  List[Tuple[float,
                                             Optional[float],
                                             Optional[float]
                                             ]
                                       ]
                                  ]
                 ) -> None: ...
