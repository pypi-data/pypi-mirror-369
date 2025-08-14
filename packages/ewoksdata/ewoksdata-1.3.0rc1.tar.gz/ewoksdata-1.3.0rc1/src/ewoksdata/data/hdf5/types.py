from numbers import Integral
from typing import Optional, Tuple, NewType

PositiveIntegral = NewType("PositiveIntegral", Integral)  # >= 0
StrictPositiveIntegral = NewType("StrictPositiveIntegral", Integral)  # > 0
ShapeType = Tuple[StrictPositiveIntegral]
SizeType = PositiveIntegral

VarShapeType = Tuple[Optional[PositiveIntegral]]  # 0 or None mark a variable dimension
VarH5pyShapeType = Tuple[
    Optional[StrictPositiveIntegral]
]  # None marks a variable dimension
