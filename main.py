from PyQt5 import QtCore, QtWidgets  # core Qt functionality
from PyQt5 import QtGui  # extends QtCore with GUI functionality
from PyQt5 import QtOpenGL  # provides QGLWidget, a special OpenGL QWidget

import OpenGL.GL as gl  # python wrapping of OpenGL
from OpenGL import GLU  # OpenGL Utility Library, extends OpenGL functionality

from pyglm import glm

import numpy as np

from AppWindow import MainWindow
import math
import sys  # we'll need this later to run our Qt application

from object_constructors import create_cube
from utilities import screen_pos_to_vector

# functions that create SceneObject should be defined in file object_constructors.py and imported here


# TODO : MAKE THIS SHIT LOOK BETTER
class GLWidget(QtOpenGL.QGLWidget):
    ROT_Y_MIN = math.pi * (0.1 / 360)
    ROT_Y_MAX = math.pi * (359.9 / 360)

    ARM_MIN = 20
    ARM_MAX = 100

    SENSITIVITY_X = 360
    SENSITIVITY_Y = 480
    SENSITIVITY_ARM = 5

    FIELD_OF_VIEW = 60.0
    ASPECT_RATIO = 1.0
    RENDER_DISTANCE_NEAR = 1.0
    RENDER_DISTANCE_FAR = 10000.0

    def __init__(self, parent=None):
        self.parent = parent

        self.armLength = 20

        self.rotX = math.pi * (10 / 360)
        self.rotY = math.pi * (10 / 360)

        self.camX = 0.0
        self.camY = 0.0
        self.camZ = 0.0

        self.objects = []
        self.pickedObjects = []
        self.hoveredObject = None
        self.viewTarget = None

        self.mouseCaptured = False
        self.mouseCapturedEvent = None
        self.mousePrevEvent = None

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
        self.ASPECT_RATIO = width / float(height)

        GLU.gluPerspective(self.FIELD_OF_VIEW, self.ASPECT_RATIO, self.RENDER_DISTANCE_NEAR, self.RENDER_DISTANCE_FAR)
        gl.glMatrixMode(gl.GL_MODELVIEW)


    def mousePressEvent(self, a0):
        self.mouseCaptured = True

        self.mouseCapturedEvent = (a0.x(), a0.y())
        self.mousePrevEvent = (a0.x(), a0.y())
        # print("Pressed", a0.x(), a0.y())


    def mouseMoveEvent(self, a0):
        if not self.mouseCaptured:
            return
        dx, dy = a0.x() - self.mousePrevEvent[0], a0.y() - self.mousePrevEvent[1]

        if max(abs(dx), abs(dy)) > 0:
            # print("Moved", dx, dy)
            self.addRotX(dx)
            self.addRotY(dy)
            self.mousePrevEvent = (a0.x(), a0.y())


    def mouseReleaseEvent(self, a0):
        clicked = self.mousePrevEvent == self.mouseCapturedEvent

        self.mouseCaptured = False

        self.mouseCapturedEvent = None
        self.mousePrevEvent = None

        if clicked:
            self.mouseClickEvent(a0)
        # print("Released", a0.x(), a0.y())


    def mouseClickEvent(self, a0):
        cam = glm.vec3([self.camX, self.camY, self.camZ])
        direction = screen_pos_to_vector(a0.x(), a0.y(), self.width(), self.height(), cam, glm.vec3(self.viewTarget.location))
        dir_t = glm.normalize(glm.vec3(self.viewTarget.location) - glm.vec3([self.camX, self.camY, self.camZ]))

        print(direction, dir_t)
        for obj in self.objects:
            if self.objects[obj].enabled and self.objects[obj].collision.enabled:
                if self.check_collision(direction, self.objects[obj]) > 0.0:
                    print(obj)

    def wheelEvent(self, a0):
        if not self.mouseCaptured:
            return

        da = a0.angleDelta().y() / 15 / 8 * self.SENSITIVITY_ARM
        self.armLength = max(self.ARM_MIN, min(self.ARM_MAX, self.armLength - da))


    def check_collision(self, direction, obj):
        tMin = self.RENDER_DISTANCE_NEAR
        tMax = self.RENDER_DISTANCE_FAR
        obj_pos = glm.vec3([obj.matrix[3].x, obj.matrix[3].y, obj.matrix[3].z])
        loc = glm.vec3([self.camX, self.camY, self.camZ])
        delta = obj_pos - loc

        pts_beg = obj.collision.pointBegin
        pts_end = obj.collision.pointEnd
        for i in range(3):
            axis = glm.vec3([obj.matrix[i].x, obj.matrix[i].y, obj.matrix[i].z])
            e = glm.dot(axis, delta)
            f = glm.dot(direction, axis)

            if math.fabs(f) > 0:
                t1 = (e + pts_beg[i]) / f
                t2 = (e + pts_end[i] * obj.scale[i]) / f

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

        gl.glDrawElements(obj.mesh.surface_mode, len(obj.mesh.surfaces), gl.GL_UNSIGNED_INT, obj.mesh.surfaces)
        gl.glPopMatrix()


    def _compute_camera(self):
        if self.viewTarget is not None:
            x, y, z = self.viewTarget.location
            self.camX = x + self.armLength * math.sin(self.rotY) * math.cos(self.rotX)
            self.camY = y + self.armLength * math.cos(self.rotY)
            self.camZ = z + self.armLength * math.sin(self.rotY) * math.sin(self.rotX)



    def _position_camera(self):
        if self.viewTarget is not None:
            x, y, z = self.viewTarget.location
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



        gl.glPopMatrix()
        gl.glPushMatrix()

        self._position_camera()


    def _init_geometry(self):
        obj1 = create_cube()
        obj1.scale = np.array([10.0, 10.0, 10.0])
        obj1.location = np.array([-10.0, 0.0, -50.0])
        obj1.calculate_matrix()

        obj2 = create_cube()
        obj2.scale = np.array([1.0, 1.0, 1.0])
        obj2.location = np.array([10.0, 0.0, -50.0])
        obj2.calculate_matrix()
        self.objects = {obj1.id : obj1,
                        obj2.id : obj2}

        self.viewTarget = obj1


    def set_perspective_top(self):
        self.rotX = 0.0
        self.rotY = self.ROT_Y_MIN


    def set_perspective_side(self, side=0):
        self.rotX = math.pi * side / 2
        self.rotY = math.pi / 2


    def set_perspective_bottom(self):
        self.rotX = 0.0
        self.rotY = self.ROT_Y_MAX


    def setRotX(self, val):
        self.rotX = math.pi * (val / 180)

    def setRotY(self, val):
        self.rotY = math.pi * (val / 360)

    def addRotX(self, val):
        self.rotX += math.pi * (val / self.SENSITIVITY_X)

    def addRotY(self, val):
        self.rotY = max(self.ROT_Y_MIN, min(self.ROT_Y_MAX, self.rotY - math.pi * (val / self.SENSITIVITY_Y)))

    def setArm(self, val):
        self.armLength = 20 + val



if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    win = MainWindow(GLWidget())
    win.show()

    sys.exit(app.exec_())

