import numpy as np

class ObjectMesh:
    def __init__(self, vertices, colors, surfaces):
        self.verticesVBO = vertices
        self.colorsVBO = colors
        self.surfaces = surfaces

        self.enabled = True

