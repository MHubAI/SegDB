"""
-------------------------------------------------
SegDB - Color 
-------------------------------------------------

-------------------------------------------------
Author: Leonard Nürnberg
Email:  leonard.nuernberg@maastrichtuniversity.nl
-------------------------------------------------
"""

from typing import List

class Color:
    def __init__(self, r:int, g:int, b:int) -> None:
        self.r = int(r)
        self.g = int(g)
        self.b = int(b)

    def getComponents(self) -> List[int]:
        return [self.r, self.g, self.b]

    def getComponentsAsFloat(self) -> List[float]:
        return [self.r / 255, self.g / 255, self.b / 255]

    def getRed(self) -> int:
        return self.r

    def getGreen(self) -> int:
        return self.g

    def getBlue(self) -> int:
        return self.b