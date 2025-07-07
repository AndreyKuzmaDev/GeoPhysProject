import sys

from PyQt5 import QtCore, QtWidgets  # core Qt functionality
from PyQt5 import QtGui  # extends QtCore with GUI functionality
import os
from PyQt5 import QtOpenGL
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel



class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, glWidget):
        super().__init__()

        self.resize(800, 600)
        self.setWindowTitle('Seismic Visualiser')

        self.glWidget = glWidget

        self.menuBar = self.menuBar()
        self.initMenu()


        self.treeView = QtWidgets.QTreeView()
        self.model = QtGui.QStandardItemModel()
        self.model.setHorizontalHeaderLabels(["Открытые проекты"])
        self.treeView.setModel(self.model)

        self.initGUI()
        self.initTimer()

    def openProject(self):
        folder_path = QtWidgets.QFileDialog.getExistingDirectory(self, "Выберите папку")
        if not folder_path:
            return

        rootNode = self.model.invisibleRootItem()
        project_item = QtGui.QStandardItem(os.path.basename(folder_path))
        rootNode.appendRow(project_item)

        def addItems(parent_item, path):
            for entry in os.listdir(path):
                entry_path = os.path.join(path, entry)
                item = QtGui.QStandardItem(entry)
                parent_item.appendRow(item)
                if os.path.isdir(entry_path):
                    addItems(item, entry_path)

        addItems(project_item, folder_path)

    def closeSelectedProject(self):
        index = self.treeView.currentIndex()
        if not index.isValid():
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Проект не выбран")
            return

        item = self.model.itemFromIndex(index)

        # Если проект — корневой элемент (проверка по необходимости)
        parent = item.parent()
        if parent is None:
            # Удаляем корневую папку из модели
            self.model.removeRow(item.row())
        else:
            # Тут можно добавить логику, если хотите закрывать не только корень
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Выделена не корневая папка")
    def initMenu(self):
        fileMenu = self.menuBar.addMenu('Файл')
        optionsMenu = self.menuBar.addMenu('Настройки')

        exitAction = QtWidgets.QAction('Закрыть проект', self)
        createFileAction = QtWidgets.QAction('Создать проект', self)
        openFileAction = QtWidgets.QAction('Открыть проект', self)
        openFileAction.triggered.connect(self.openProject)
        changeColorAction = QtWidgets.QAction('Цвета', self)

        exitAction.triggered.connect(self.closeSelectedProject)
        fileMenu.addAction(createFileAction)
        fileMenu.addAction(openFileAction)
        fileMenu.addAction(exitAction)

        optionsMenu.addAction(changeColorAction)
    def openFile(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(None, "Выберите файл")

        print("Выбранный файл:", file_path)

    def initGUI(self):
        central_widget = QtWidgets.QWidget()
        gui_layout = QtWidgets.QHBoxLayout()  # Можно горизонтальный, чтобы разместить список и OpenGL

        central_widget.setLayout(gui_layout)
        self.setCentralWidget(central_widget)
        gui_layout.addWidget(self.treeView, 1)  # занимает 1 часть

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

