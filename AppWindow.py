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
        self.menuToolBar = QtWidgets.QToolBar()
        self.initMenu()
        self.initToolBar()



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


        dxf_file = None
        for entry in os.listdir(folder_path):
            if entry.lower().endswith('.dxf'):
                dxf_file = os.path.join(folder_path, entry)
                break

        if dxf_file:
            # Передать найденный dxf файл в функцию инициализации геометрии
            self.glWidget._init_geometry(dxf_file)

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

        parent = item.parent()
        if parent is None:
            self.model.removeRow(item.row())
        else:
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
    def initToolBar(self):
        self.menuToolBar = QtWidgets.QToolBar('Меню с иконками')
        self.menuToolBar.setMovable(False)
        self.addToolBar(QtCore.Qt.TopToolBarArea, self.menuToolBar)
        #self.insertToolBar(self.menuBar, self.menuToolBar)

        icon1 = QtGui.QIcon('icons/x.png')
        icon3 = QtGui.QIcon('icons/y.png')
        icon2 = QtGui.QIcon('icons/z.png')

        proj_yz = QtWidgets.QAction(icon1, '', self)
        proj_yx = QtWidgets.QAction(icon2, '', self)
        proj_zx = QtWidgets.QAction(icon3, '', self)

        self.menuToolBar.setIconSize(QtCore.QSize(24, 24))
        self.menuToolBar.addSeparator()

        proj_yz.setToolTip('Вид сбоку')
        proj_yx.setToolTip('Показать все')
        proj_zx.setToolTip('Вид сверху')

        proj_yx.triggered.connect(lambda val: self.glWidget.setArm(val))
        proj_zx.triggered.connect(lambda checked: self.glWidget.set_perspective_top())
        proj_yz.triggered.connect(lambda val: self.glWidget.set_perspective_side())

        self.menuToolBar.addAction(proj_yx)
        self.menuToolBar.addAction(proj_zx)
        self.menuToolBar.addAction(proj_yz)
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



        gui_layout.addLayout(right_layout, 3)

    def initTimer(self):
        timer = QtCore.QTimer(self)
        timer.setInterval(20)  # 20 мс
        timer.timeout.connect(self.glWidget.updateGL)
        timer.start()

