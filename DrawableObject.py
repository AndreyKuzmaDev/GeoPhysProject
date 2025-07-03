import numpy as np

class DrawableObject:
    def __init__(self, vertices, colors, surfaces):
        self.verticesVBO = vertices
        self.colorsVBO = colors
        self.surfaces = surfaces

        self.enabled = True

        self.scale = np.array([1.0, 1.0, 1.0])
        self.rotation = np.array([0.0, 0.0, 0.0])
        self.location = np.array([0.0, 0.0, 0.0])
        self.origin = np.array([0.0, 0.0, 0.0])
