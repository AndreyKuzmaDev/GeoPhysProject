import numpy as np

class ObjectMesh:
    def __init__(self, vertices, colors, surface_mode, faces=None, edges=None):
        self.verticesVBO = vertices
        self.colorsVBO = colors
        self.faces = faces
        self.edges = edges

        self.surface_mode = surface_mode
        self.enabled = True

