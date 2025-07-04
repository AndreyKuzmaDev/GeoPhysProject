import numpy as np

class DrawableObject:
    def __init__(self, vertices, colors, surfaces, origin=np.array([0.0, 0.0, 0.0])):
        self.verticesVBO = vertices
        self.colorsVBO = colors
        self.surfaces = surfaces
        self.origin = origin

        self.enabled = True

        self.scale = np.array([1.0, 1.0, 1.0])
        self.rotation = np.array([0.0, 0.0, 0.0])
        self.location = np.array([0.0, 0.0, 0.0])

