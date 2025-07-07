import ezdxf
import numpy as np
from OpenGL.arrays import vbo
from pyglm import glm
import OpenGL.GL as gl

from collisions import CollisionBox
from object_meshes import ObjectMesh
from scene_objects import SceneObject


def load_dxf_vertices(file_path, scale=1.0, normalize=False):
    doc = ezdxf.readfile(file_path)
    msp = doc.modelspace()

    vertices = []
    indices = []
    index_offset = 0
    face_limit = 100
    for e in msp.query('3DFACE'):
        if len(e.wcs_vertices(False)) != 3:
            continue
        pts = [(vertex.x, vertex.y, vertex.z) for vertex in e.wcs_vertices(False)]

        pts = np.array(pts, dtype=np.float32) * scale
        #print(pts)
        vertices.extend(pts)

        n = len(pts)
        for i in range(n):
            indices.extend([(index_offset + n - i - 1) % 8 ,])
        index_offset += n
        face_limit -= 1
        if face_limit == 0:
            break

    vertices = np.array(vertices, dtype=np.float32)

    if normalize:
        min_coords = vertices.min(axis=0)
        max_coords = vertices.max(axis=0)
        vertices = (vertices - min_coords) / (max_coords - min_coords)

    indices = np.array(indices, dtype=np.uint32)

    return vertices, indices


def create_dxf_object(file_path):
    vertices, indices = load_dxf_vertices(file_path, 1.0,True)
    print(vertices)
    print(indices)
    vertVBO = vbo.VBO(np.reshape(vertices,
                                  (1, -1)).astype(np.float32))
    vertVBO.bind()
# functions that create SceneObject should be defined in file object_constructors.py and imported here

    colors = np.tile(np.array([0.0, 0.0, 0.0], dtype=np.float32), (len(vertices), 1))
    colorVBO = vbo.VBO(np.reshape(colors,
                                  (1, -1)).astype(np.float32))
    colorVBO.bind()

    print(vertVBO)
    print(colorVBO)

    mesh = ObjectMesh(vertVBO, colorVBO, gl.GL_TRIANGLES, indices)

    min_v = vertices.min(axis=0)
    max_v = vertices.max(axis=0)
    collision = CollisionBox(glm.vec3(min_v), glm.vec3(max_v))

    center = (min_v + max_v) / 2.0

    obj = SceneObject(mesh, collision, center)

    return obj


def create_cube():
    cubeClrArray = np.array(
        [[0.0, 0.0, 0.0],
         [1.0, 0.0, 0.0],
         [1.0, 1.0, 0.0],
         [0.0, 1.0, 0.0],
         [0.0, 0.0, 1.0],
         [1.0, 0.0, 1.0],
         [1.0, 1.0, 1.0],
         [0.0, 1.0, 1.0]])
    colorVBO = vbo.VBO(np.reshape(cubeClrArray,
                                  (1, -1)).astype(np.float32))
    colorVBO.bind()

    cubeIdxArray = np.array(
        [0, 1, 2, 3,
         3, 2, 6, 7,
         1, 0, 4, 5,
         2, 1, 5, 6,
         0, 3, 7, 4,
         7, 6, 5, 4])
    cubeVtxArray = np.array(
        [[0.0, 0.0, 0.0],
         [1.0, 0.0, 0.0],
         [1.0, 1.0, 0.0],
         [0.0, 1.0, 0.0],
         [0.0, 0.0, 1.0],
         [1.0, 0.0, 1.0],
         [1.0, 1.0, 1.0],
         [0.0, 1.0, 1.0]])
    vertVBO = vbo.VBO(np.reshape(cubeVtxArray,
                                 (1, -1)).astype(np.float32))
    vertVBO.bind()
    cubeEdgesIdxArray = np.array(
        [0, 1,
         1, 2,
         2, 3,
         3, 0,
         0, 4,
         1, 5,
         2, 6,
         3, 7,
         4, 5,
         5, 6,
         6, 7,
         7, 4]
    )

    mesh = ObjectMesh(vertVBO, colorVBO, gl.GL_QUADS, cubeIdxArray, cubeEdgesIdxArray)
    collision = CollisionBox(glm.vec3([0.0, 0.0, 0.0]), glm.vec3([1.0, 1.0, 1.0]))
    obj = SceneObject(mesh, collision, np.array([0.5, 0.5, 0.5]))

    return obj
