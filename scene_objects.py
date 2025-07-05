import numpy as np
from pyglm import glm
from pyglm.glm import sin, cos

# NEVER EVER interact with this var outside SceneObject class
OBJECT_COUNT = 0

# TODO : create methods to update SceneObject fields and automatically recalculate matrix
# OR : do something with matrices provided by OpenGL and make them work!!
class SceneObject:
    def __init__(self, mesh, collision, origin=np.array([0.0, 0.0, 0.0])):
        self.enabled = True

        self.mesh = mesh
        self.collision = collision
        self.origin = origin

        self.scale = np.array([1.0, 1.0, 1.0])
        self.rotation = np.array([0.0, 0.0, 0.0])
        self.location = np.array([0.0, 0.0, 0.0])
        self.matrix = None
        self.calculate_matrix()

        global OBJECT_COUNT
        self.id = OBJECT_COUNT
        OBJECT_COUNT += 1


    def calculate_matrix(self):
        a, b, c = self.rotation
        x, y, z = self.location
        sx, sy, sz = self.scale
        ox, oy, oz = self.origin
        R = glm.mat4(cos(b) * cos(c), sin(a) * sin(b) * cos(c) - cos(a) * sin(c), cos(a) * sin(b) * cos(c) + sin(a) * sin(c), x,
                      cos(b) * sin(c), sin(a) * sin(b) * sin(c) + cos(a) * cos(c), cos(a) * sin(b) * sin(c) - sin(a) * cos(c), y,
                      -sin(b),         sin(a) * cos(b),                            cos(a) * cos(b),                            z,
                      0.0,             0.0,                                        0.0,                                        1.0)
        S = glm.mat4(sx, 0.0, 0.0, 0.0,
                      0.0, sy, 0.0, 0.0,
                      0.0, 0.0, sz, 0.0,
                      0.0, 0.0, 0.0, 1.0)
        O = glm.mat4(1.0, 0.0, 0.0, -ox,
                      0.0, 1.0, 0.0, -oy,
                      0.0, 0.0, 1.0, -oz,
                      0.0, 0.0, 0.0, 1.0)
        self.matrix = glm.transpose(R * O * S)




if __name__ == '__main__':
    a = SceneObject(None, None)