from PyQt5 import QtCore, QtWidgets  # core Qt functionality
from PyQt5 import QtGui  # extends QtCore with GUI functionality
from PyQt5 import QtOpenGL  # provides QGLWidget, a special OpenGL QWidget

import OpenGL.GL as gl  # python wrapping of OpenGL
from OpenGL import GLU  # OpenGL Utility Library, extends OpenGL functionality

import sys  # we'll need this later to run our Qt application

from OpenGL.arrays import vbo
import numpy as np

from AppWindow import MainWindow
import math
from DrawableObject import DrawableObject


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
    obj = DrawableObject(vertVBO, colorVBO, cubeIdxArray, np.array([0.5, 0.5, 0.5]))

    return obj


class GLWidget(QtOpenGL.QGLWidget):
    def __init__(self, parent=None):
        self.parent = parent
        self.target = None
        self.armLength = 20

        self.rotX = 0.0
        self.rotY = math.pi * (1 / 360)

        self.camX = 0.0
        self.camY = 0.0
        self.camZ = 0.0

        self.objects = []

        QtOpenGL.QGLWidget.__init__(self, parent)

    def initializeGL(self):
        self.qglClearColor(QtGui.QColor(135, 206, 235))
        gl.glEnable(gl.GL_DEPTH_TEST)

        self.initGeometry()
        gl.glPushMatrix()


    def resizeGL(self, width, height):
        gl.glViewport(0, 0, width, height)
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        aspect = width / float(height)

        GLU.gluPerspective(45.0, aspect, 1.0, 500.0)
        gl.glMatrixMode(gl.GL_MODELVIEW)


    def draw_object(self, drawable):
        gl.glPushMatrix()

        gl.glTranslate(*drawable.location)
        gl.glRotatef(drawable.rotation[0], 1.0, 0.0, 0.0)
        gl.glRotatef(drawable.rotation[1], 0.0, 1.0, 0.0)
        gl.glRotatef(drawable.rotation[2], 0.0, 0.0, 1.0)
        gl.glScale(*drawable.scale)
        gl.glTranslate(*(drawable.origin * -1))

        gl.glVertexPointer(3, gl.GL_FLOAT, 0, drawable.verticesVBO)
        gl.glColorPointer(3, gl.GL_FLOAT, 0, drawable.colorsVBO)

        gl.glDrawElements(gl.GL_QUADS, len(drawable.surfaces), gl.GL_UNSIGNED_INT, drawable.surfaces)

        gl.glPopMatrix()


    def paintGL(self):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
        gl.glEnableClientState(gl.GL_COLOR_ARRAY)

        for obj in self.objects:
            if obj.enabled:
                self.draw_object(obj)

        gl.glDisableClientState(gl.GL_VERTEX_ARRAY)
        gl.glDisableClientState(gl.GL_COLOR_ARRAY)

        if self.target is not None:
            gl.glPopMatrix()
            gl.glPushMatrix()
            x, y, z = self.target.location
            self.camX = x + self.armLength * math.sin(self.rotY) * math.cos(self.rotX)
            self.camZ = z + self.armLength * math.sin(self.rotY) * math.sin(self.rotX)
            self.camY = y + self.armLength * math.cos(self.rotY)
            GLU.gluLookAt(self.camX, self.camY, self.camZ, x, y, z, 0.0, 1.0, 0.0)

    def initGeometry(self):
        obj1 = create_cube()
        obj1.scale = np.array([10.0, 10.0, 10.0])
        obj1.location = np.array([-10.0, 0.0, -50.0])

        obj2 = create_cube()
        obj2.scale = np.array([10.0, 10.0, 10.0])
        obj2.location = np.array([10.0, 0.0, -50.0])
        self.objects = [obj1, obj2]

        self.target = obj1


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

