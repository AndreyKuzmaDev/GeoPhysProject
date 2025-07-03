from PyQt5 import QtCore, QtWidgets  # core Qt functionality
from PyQt5 import QtGui  # extends QtCore with GUI functionality
from PyQt5 import QtOpenGL  # provides QGLWidget, a special OpenGL QWidget

import OpenGL.GL as gl  # python wrapping of OpenGL
from OpenGL import GLU  # OpenGL Utility Library, extends OpenGL functionality

import sys  # we'll need this later to run our Qt application

from OpenGL.arrays import vbo
import numpy as np

from DrawableObject import DrawableObject

class GLWidget(QtOpenGL.QGLWidget):
    def __init__(self, parent=None):
        self.parent = parent
        self.target = None
        self.armLength = 20
        self.rotX = 0
        self.rotY = 0
        QtOpenGL.QGLWidget.__init__(self, parent)

    def initializeGL(self):
        self.qglClearColor(QtGui.QColor(135, 206, 235))  # initialize the screen to blue
        gl.glEnable(gl.GL_DEPTH_TEST)  # enable depth testing

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

        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
        gl.glEnableClientState(gl.GL_COLOR_ARRAY)

        gl.glVertexPointer(3, gl.GL_FLOAT, 0, drawable.verticesVBO)
        gl.glColorPointer(3, gl.GL_FLOAT, 0, drawable.colorsVBO)

        gl.glDrawElements(gl.GL_QUADS, len(drawable.surfaces), gl.GL_UNSIGNED_INT, drawable.surfaces)

        gl.glDisableClientState(gl.GL_VERTEX_ARRAY)
        gl.glDisableClientState(gl.GL_COLOR_ARRAY)

        gl.glPopMatrix()


    def paintGL(self):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        for obj in self.objects:
            self.draw_object(obj)

        if self.target is not None:
            gl.glPopMatrix()
            gl.glPushMatrix()
            gl.glTranslate(*self.target.location)
            gl.glRotatef(self.rotX, 1.0, 0.0, 0.0)
            gl.glRotatef(self.rotY, 0.0, 1.0, 0.0)
            gl.glTranslate(*(self.target.location * -1))



    def add_cube(self):
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
        obj = DrawableObject(vertVBO, colorVBO, cubeIdxArray)

        self.objects.append(obj)

    def initGeometry(self):
        self.objects = []
        self.add_cube()
        self.objects[-1].scale = np.array([10.0, 10.0, 10.0])
        self.objects[-1].location = np.array([-10.0, 0.0, -50.0])
        self.objects[-1].origin = np.array([0.5, 0.5, 0.5])
        self.add_cube()
        self.objects[-1].scale = np.array([10.0, 10.0, 10.0])
        self.objects[-1].location = np.array([10.0, 0.0, -50.0])
        self.objects[-1].origin = np.array([0.5, 0.5, 0.5])
        self.target = self.objects[0]


    def setRotX(self, val):
        self.rotX = np.pi * val

    def setRotY(self, val):
        self.rotY = np.pi * val

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
        sliderX.valueChanged.connect(lambda val: self.glWidget.setRotX(val))

        sliderY = QtWidgets.QSlider(QtCore.Qt.Horizontal)
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

