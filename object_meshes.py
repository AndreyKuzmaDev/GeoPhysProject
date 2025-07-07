import numpy as np

class ObjectMesh:
    def __init__(self, vertices, colors, faces=None, edges=None):
        self.verticesVBO = vertices
        self.colorsVBO = colors
        self.faces = faces
        self.edges = edges

        self.enabled = True

