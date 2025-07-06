from PyQt5 import QtCore, QtWidgets  # core Qt functionality
from PyQt5 import QtGui  # extends QtCore with GUI functionality
from PyQt5 import QtOpenGL  # provides QGLWidget, a special OpenGL QWidget

import OpenGL.GL as gl  # python wrapping of OpenGL
from OpenGL import GLU  # OpenGL Utility Library, extends OpenGL functionality

from OpenGL.arrays import vbo

from pyglm import glm

import numpy as np

from AppWindow import MainWindow
import math
import sys  # we'll need this later to run our Qt application
import ezdxf
from object_meshes import ObjectMesh
from scene_objects import SceneObject
from collisions import CollisionBox


def load_dxf_vertices(file_path, scale=1.0, normalize=False):
    doc = ezdxf.readfile(file_path)
    msp = doc.modelspace()

    vertices = []
    indices = []
    index_offset = 0

    for e in msp.query('3DFACE'):
        if e.dxftype() == '3DFACE':
            pts = [(point[0]%10, point[1]%10, point[2]%10 if len(point) > 2 else 0) for point in e.get_points('xyz')]
        else:
            pts = [(vertex.dxf.location.x%10, vertex.dxf.location.y%10, vertex.dxf.location.z%10) for vertex in e.vertices()]

        pts = np.array(pts, dtype=np.float64) * scale
        print(pts)
        vertices.extend(pts)

        n = len(pts)
        for i in range(n):
            indices.extend([index_offset + i,])

        if e.closed:
            indices.extend([index_offset + n - 1, index_offset])

        index_offset += n

    vertices = np.array(vertices, dtype=np.float64)
    print(vertices)
    print(len(vertices))
    if normalize:
        min_coords = vertices.min(axis=0)
        max_coords = vertices.max(axis=0)
        vertices = (vertices - min_coords) / (max_coords - min_coords)

    indices = np.array(indices, dtype=np.uint32)
    print(indices)
    print(len(indices))
    return vertices, indices


def create_dxf_object(file_path):
    vertices, indices = load_dxf_vertices(file_path, True)

    print(vertices.shape, indices.shape)

    vertVBO = vbo.VBO(vertices.astype(np.float32))
    vertVBO.bind()

    colors = np.tile(np.array([0.5, 0.5, 0.5], dtype=np.float32), (len(vertices), 1))
    colorVBO = vbo.VBO(colors.astype(np.float32))
    colorVBO.bind()

    mesh = ObjectMesh(vertVBO, colorVBO, indices)

    min_v = vertices.min(axis=0)
    max_v = vertices.max(axis=0)
    collision = CollisionBox(glm.vec3(min_v), glm.vec3(max_v))

    center = (min_v + max_v) / 2.0
    obj = SceneObject(mesh, collision, center)

    return obj
def create_cube():
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
    mesh = ObjectMesh(vertVBO, colorVBO, cubeIdxArray)
    collision = CollisionBox(glm.vec3([0.0, 0.0, 0.0]), glm.vec3([1.0, 1.0, 1.0]))
    obj = SceneObject(mesh, collision, np.array([0.5, 0.5, 0.5]))

    return obj

# TODO : MAKE THIS SHIT LOOK BETTER
class GLWidget(QtOpenGL.QGLWidget):
    def __init__(self, parent=None):
        self.parent = parent

        self.armLength = 20

        self.rotX = 0.0
        self.rotY = math.pi * (1 / 360)

        self.camX = 0.0
        self.camY = 0.0
        self.camZ = 0.0

        self.objects = []
        self.picked = None
        self.target = None

        self.lockPicked = False

        QtOpenGL.QGLWidget.__init__(self, parent)

    def initializeGL(self):
        self.qglClearColor(QtGui.QColor(135, 206, 235))
        gl.glEnable(gl.GL_DEPTH_TEST)

        self._init_geometry()
        gl.glPushMatrix()


    def resizeGL(self, width, height):
        gl.glViewport(0, 0, width, height)
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        aspect = width / float(height)

        GLU.gluPerspective(45.0, aspect, 1.0, 500.0)
        gl.glMatrixMode(gl.GL_MODELVIEW)


    def check_collision(self, direction, obj):
        tMin = 0.0
        tMax = 100.0
        obj_pos = glm.vec3([obj.matrix[3].x, obj.matrix[3].y, obj.matrix[3].z])
        loc = glm.mat3(obj.scale[0], 0.0 ,0.0,
                       0.0, obj.scale[1], 0.0,
                       0.0, 0.0, obj.scale[2]) * glm.vec3([self.camX, self.camY, self.camZ])
        delta = obj_pos - loc
        '''print(obj_pos)
        print(loc)
        print(direction)
        print(delta)
        print()'''
        pts_beg = [obj.collision.pointBegin.x, obj.collision.pointBegin.y, obj.collision.pointBegin.z]
        pts_end = [obj.collision.pointEnd.x, obj.collision.pointEnd.y, obj.collision.pointEnd.z]
        for i in range(3):
            axis = glm.vec3([obj.matrix[i].x, obj.matrix[i].y, obj.matrix[i].z])
            e = glm.dot(axis, delta)
            f = glm.dot(direction, axis)

            if math.fabs(f) > 0:
                t1 = (e + pts_beg[i]) / f
                t2 = (e + pts_end[i]) / f
                if t1 > t2:
                    t1, t2 = t2, t1
                if t2 < tMax:
                    tMax = t2
                if t1 > tMin:
                    tMin = t1
                if tMax < tMin:
                    return -1.0
            else:
                if -e + pts_beg[i] > 0.0 or -e + pts_end[i] < 0.0:
                    return -1.0
        return tMin



    def draw_object(self, obj):
        gl.glPushMatrix()

        gl.glTranslate(*obj.location)
        gl.glRotatef(obj.rotation[0], 1.0, 0.0, 0.0)
        gl.glRotatef(obj.rotation[1], 0.0, 1.0, 0.0)
        gl.glRotatef(obj.rotation[2], 0.0, 0.0, 1.0)
        gl.glScale(*obj.scale)
        gl.glTranslate(*(obj.origin * -1))


        # print(gl.glGetDoublev(gl.GL_MODELVIEW_MATRIX))

        gl.glVertexPointer(3, gl.GL_FLOAT, 0, obj.mesh.verticesVBO)
        gl.glColorPointer(3, gl.GL_FLOAT, 0, obj.mesh.colorsVBO)

        gl.glDrawElements(gl.GL_TRIANGLES, len(obj.mesh.surfaces), gl.GL_UNSIGNED_INT, obj.mesh.surfaces)
        gl.glPopMatrix()


    def _compute_camera(self):
        if self.target is not None:
            x, y, z = self.target.location
            self.camX = x + self.armLength * math.sin(self.rotY) * math.cos(self.rotX)
            self.camY = y + self.armLength * math.cos(self.rotY)
            self.camZ = z + self.armLength * math.sin(self.rotY) * math.sin(self.rotX)



    def _position_camera(self):
        if self.target is not None:
            x, y, z = self.target.location
            GLU.gluLookAt(self.camX, self.camY, self.camZ, x, y, z, 0.0, 1.0, 0.0)


    def paintGL(self):

        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        self._compute_camera()

        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
        gl.glEnableClientState(gl.GL_COLOR_ARRAY)

        for obj in self.objects:
            if self.objects[obj].enabled and self.objects[obj].mesh.enabled:
                self.draw_object(self.objects[obj])

        gl.glDisableClientState(gl.GL_VERTEX_ARRAY)
        gl.glDisableClientState(gl.GL_COLOR_ARRAY)

        direction = glm.normalize(glm.vec3(self.target.location) - glm.vec3([self.camX, self.camY, self.camZ]))
        for obj in self.objects:
            if self.objects[obj].enabled and self.objects[obj].collision.enabled:
                if self.check_collision(direction, self.objects[obj]) > 0.0:
                    pass

        gl.glPopMatrix()
        gl.glPushMatrix()

        self._position_camera()


    def _init_geometry(self):
        obj1 = create_dxf_object("korkino_model.dxf")
        obj1.scale = np.array([1.0, 1.0, 1.0])
        obj1.location = np.array([0.0, 0.0, -50.00])
        obj1.calculate_matrix()

        '''obj2 = create_cube()
        obj2.scale = np.array([1.0, 1.0, 1.0])
        obj2.location = np.array([10.0, 0.0, -50.0])
        obj2.calculate_matrix()'''
        self.objects = {obj1.id : obj1}

        self.target = obj1


    def _init_physics(self):
        pass

    def setRotX(self, val):
        self.rotX = math.pi * (val / 180)

    def setRotY(self, val):
        self.rotY = math.pi * (val / 360)

    def setArm(self, val):
        self.armLength = 20 + val



if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    win = MainWindow(GLWidget())
    win.show()

    sys.exit(app.exec_())

