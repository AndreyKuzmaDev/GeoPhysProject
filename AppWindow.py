import sys

from PyQt5 import QtCore, QtWidgets  # core Qt functionality
from PyQt5 import QtGui  # extends QtCore with GUI functionality
from PyQt5 import QtOpenGL
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, glWidget):
        super().__init__()

        self.resize(800, 600)
        self.setWindowTitle('Seismic Visualiser')

        self.glWidget = glWidget

        # Создаём меню-бар как поле класса
        self.menuBar = self.menuBar()
        self.initMenu()

        # Создаём многоуровневый список (QTreeWidget)
        self.treeWidget = QtWidgets.QTreeWidget()
        self.treeWidget.setHeaderLabels(['Имя', 'Описание'])

        self.initGUI()
        self.initTimer()

    def initMenu(self):
        fileMenu = self.menuBar.addMenu('Файл')
        exitAction = QtWidgets.QAction('Выход', self)
        exitAction.triggered.connect(self.close)
        fileMenu.addAction(exitAction)

    def initGUI(self):
        central_widget = QtWidgets.QWidget()
        gui_layout = QtWidgets.QHBoxLayout()  # Можно горизонтальный, чтобы разместить список и OpenGL

        central_widget.setLayout(gui_layout)
        self.setCentralWidget(central_widget)

        # Слева дерево, справа OpenGL и слайдеры
        gui_layout.addWidget(self.treeWidget, 1)  # занимает 1 часть

        right_layout = QtWidgets.QVBoxLayout()

        right_layout.addWidget(self.glWidget, 5)

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

        for slider in (sliderX, sliderY, sliderZ):
            right_layout.addWidget(slider)

        gui_layout.addLayout(right_layout, 3)

    def initTimer(self):
        timer = QtCore.QTimer(self)
        timer.setInterval(20)  # 20 мс
        timer.timeout.connect(self.glWidget.updateGL)
        timer.start()

