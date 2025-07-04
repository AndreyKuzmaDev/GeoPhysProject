import numpy as np

# never interact with this var outside SceneObject class
OBJECT_COUNT = 0


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

        global OBJECT_COUNT
        self.id = OBJECT_COUNT
        OBJECT_COUNT += 1



if __name__ == '__main__':
    a = SceneObject(None, None)