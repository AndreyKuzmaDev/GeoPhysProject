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
    face_limit = 10
    for e in msp.query('3DFACE'):
        if len(e.wcs_vertices(False)) != 3:
            continue
        pts = [(vertex.x, vertex.y, vertex.z) for vertex in e.wcs_vertices(False)]

        pts = np.array(pts, dtype=np.float32) * scale
        # print(pts)
        vertices.extend(pts)

        n = len(pts)
        indices.extend([index_offset, index_offset + 1, index_offset + 2])
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
    vertices, indices = load_dxf_vertices(file_path, 1.0, True)
    print(vertices)
    print(indices)

    colors = np.tile(np.array([1.0, 0.0, 0.0], dtype=np.float32), (len(vertices), 1))

    vertVBO = vbo.VBO(vertices.flatten().astype(np.float32))
    colorVBO = vbo.VBO(colors.flatten().astype(np.float32))
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


def create_test():
    cubeVtxArray = np.array(
        [[0.4017314, 0.0, 0.06345682],
         [0.3172672, 0.36789298, 0.05736027],
         [0.51240057, 0.04785181, 0.08870859],
         [0.51240057, 0.04785181, 0.08870859],
         [0.5036266, 0.61435556, 0.10527653],
         [0.71911556, 0.19192179, 0.13765411],
         [0.71911556, 0.19192179, 0.13765411],
         [0.6084464, 0.71983534, 0.13115488],
         [0.87342066, 0.3326473, 0.17527585],
         [0.87342066, 0.3326473, 0.17527585],
         [0.7525737, 0.77437615, 0.16378084],
         [1.0, 0.49909955, 0.20780772],
         [0.13453439, 0.47182918, 0.70687443],
         [0.22999533, 0.29765886, 0.03636856],
         [0.20870379, 0.48675072, 0.7399802],
         [0.20870379, 0.48675072, 0.7399802],
         [0.3172672, 0.36789298, 0.05736027],
         [0.31434253, 0.556213, 0.7898082],
         [0.31434253, 0.556213, 0.7898082],
         [0.5036266, 0.61435556, 0.10527653],
         [0.36932614, 0.63184977, 0.8178486],
         [0.5036266, 0.61435556, 0.10527653],
         [0.431095, 0.7949576, 0.8536696],
         [0.6084464, 0.71983534, 0.13115488],
         [0.05217595, 0.48392075, 0.67166686],
         [0.06832007, 0.24311809, 0.0],
         [0.0, 0.53434527, 0.65175706],
         [0.6137108, 0.9760741, 0.9430838],
         [0.7525737, 0.77437615, 0.16378084],
         [0.741343, 1.0, 1.0]])
    vertVBO = vbo.VBO(np.reshape(cubeVtxArray,
                                 (1, -1)).astype(np.float32))

    cubeClrArray = np.array(
        [[1.0, 1.0, 0.0] for i in range(30)])
    colorVBO = vbo.VBO(np.reshape(cubeClrArray,
                                  (1, -1)).astype(np.float32))

    cubeIdxArray = np.array(
        [0, 1, 3,
         1, 2, 3,
         3, 2, 7,
         2, 6, 7,
         1, 0, 5,
         0, 4, 5,
         2, 1, 6,
         1, 5, 6,
         0, 3, 4,
         3, 7, 4,
         7, 6, 4,
         6, 5, 4])

    cubeEdgesIdxArray = np.array(30 ** 2 // 2)
    for j in range(30):
        for i in range(j):
            cubeEdgesIdxArray = np.append(cubeEdgesIdxArray, i)
    mesh = ObjectMesh(vertVBO, colorVBO, gl.GL_TRIANGLES, cubeIdxArray, cubeEdgesIdxArray)
    collision = CollisionBox(glm.vec3([0.0, 0.0, 0.0]), glm.vec3([1.0, 1.0, 1.0]))
    obj = SceneObject(mesh, collision, np.array([0.5, 0.5, 0.5]))

    return obj
