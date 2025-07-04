import numpy as np


class CollisionBox:
    def __init__(self, poingBegin, pointEnd):
        self.enabled = True

        self.pointBegin = poingBegin
        self.pointEnd = pointEnd


