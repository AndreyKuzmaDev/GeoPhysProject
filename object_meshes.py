import numpy as np

class ObjectMesh:
    def __init__(self, vertices, colors, surfaces, surface_mode):
        self.verticesVBO = vertices
        self.colorsVBO = colors
        self.surfaces = surfaces

        self.surface_mode = surface_mode
        self.enabled = True

