from OpenGL.raw.GL.VERSION.GL_1_0 import GL_MATRIX_MODE
from PyQt5 import QtCore, QtWidgets  # core Qt functionality
from PyQt5 import QtGui  # extends QtCore with GUI functionality
from PyQt5 import QtOpenGL  # provides QGLWidget, a special OpenGL QWidget

import OpenGL.GL as gl  # python wrapping of OpenGL
from OpenGL import GLU  # OpenGL Utility Library, extends OpenGL functionality
from OpenGL.arrays import vbo

from pyglm import glm

import numpy as np
import math
import sys  # we'll need this later to run our Qt application

from object_meshes import ObjectMesh
from scene_objects import SceneObject
from collisions import CollisionBox


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
        obj_pos = glm.vec3(obj.matrix[3][:3])
        delta = obj_pos - glm.vec3([self.camX, self.camY, self.camZ])
        """print(obj_pos)
        print(glm.vec3([self.camX, self.camY, self.camZ]))
        print(obj.location)
        print(direction)
        print(delta)
        print()"""
        pts_beg = [obj.collision.pointBegin.x, obj.collision.pointBegin.y, obj.collision.pointBegin.z]
        pts_end = [obj.collision.pointEnd.x, obj.collision.pointEnd.y, obj.collision.pointEnd.z]
        for i in range(3):
            axis = glm.vec3(obj.matrix[i][:3])
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

        if obj.matrix is None:
            obj.matrix = gl.glGetDoublev(gl.GL_MODELVIEW_MATRIX)

        gl.glVertexPointer(3, gl.GL_FLOAT, 0, obj.mesh.verticesVBO)
        gl.glColorPointer(3, gl.GL_FLOAT, 0, obj.mesh.colorsVBO)

        gl.glDrawElements(gl.GL_QUADS, len(obj.mesh.surfaces), gl.GL_UNSIGNED_INT, obj.mesh.surfaces)
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
                    print(obj)
        gl.glPopMatrix()
        gl.glPushMatrix()

        self._position_camera()


    def _init_geometry(self):
        obj1 = create_cube()
        obj1.scale = np.array([10.0, 10.0, 10.0])
        obj1.location = np.array([-10.0, 0.0, -50.0])

        obj2 = create_cube()
        obj2.scale = np.array([1.0, 1.0, 1.0])
        obj2.location = np.array([10.0, 0.0, -50.0])
        self.objects = {obj1.id : obj1,
                        obj2.id : obj2}

        self.target = obj2


    def _init_physics(self):
        pass

    def setRotX(self, val):
        self.rotX = math.pi * (val / 180)

    def setRotY(self, val):
        self.rotY = math.pi * (val / 360)

    def setArm(self, val):
        self.armLength = 20 + val


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)  # call the init for the parent class

        self.resize(800, 600)
        self.setWindowTitle('OpenGL App')

        self.glWidget = GLWidget(self)
        self.initGUI()

        timer = QtCore.QTimer(self)
        timer.setInterval(20)  # period, in milliseconds
        timer.timeout.connect(self.glWidget.updateGL)
        timer.start()

    def initGUI(self):
        central_widget = QtWidgets.QWidget()
        gui_layout = QtWidgets.QVBoxLayout()
        central_widget.setLayout(gui_layout)

        self.setCentralWidget(central_widget)

        gui_layout.addWidget(self.glWidget)

        sliderX = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        sliderX.setMinimum(0)
        sliderX.setMaximum(360)
        sliderX.valueChanged.connect(lambda val: self.glWidget.setRotX(val))

        sliderY = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        sliderY.setMinimum(1)
        sliderY.setMaximum(359)
        sliderY.valueChanged.connect(lambda val: self.glWidget.setRotY(val))

        sliderZ = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        sliderZ.valueChanged.connect(lambda val: self.glWidget.setArm(val))

        gui_layout.addWidget(sliderX)
        gui_layout.addWidget(sliderY)
        gui_layout.addWidget(sliderZ)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    win = MainWindow()
    win.show()

    sys.exit(app.exec_())

