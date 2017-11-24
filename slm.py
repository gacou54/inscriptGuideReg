#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
    Script for the pyQt program
"""
import sys
import time
import numpy as np
import Main
from Screenshot import calibrate_screenshot
import matplotlib.pyplot as plt
import libPhase as lp
import clibPhase as clp
from PyQt5.QtWidgets import (QApplication, QWidget,
                             QCheckBox, QPushButton,
                             QMainWindow, QAction,
                             qApp, QLabel,
                             QGridLayout, QHBoxLayout,
                             QSpinBox, QDoubleSpinBox,
                             QTextEdit, QDesktopWidget,
                             QTabWidget)
from PyQt5.QtCore import Qt, QByteArray, QPoint
from PyQt5.QtGui import (QPixmap, QImage)
from PyQt5 import QtGui, QtCore


LENGHT_LA = 792
LENGHT_HA = 600


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        # menu bar
        ##############################################
        exitAction = QAction('&Exit', self)
        exitAction.triggered.connect(qApp.quit)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAction)
        ##############################################

        # main window
        self.img_widget = ImgWindow()
        # second screen window
        self.img_SLM_widget = ImgSLM()
        self.img_SLM_widget.setAutoFillBackground(True)

        palette = self.img_SLM_widget.palette()
        palette.setColor(self.img_SLM_widget.backgroundRole(), QtCore.Qt.black)
        self.img_SLM_widget.setPalette(palette)

        self.show_widgets()

        # if there is a second screen, show the second window on the second screen
        #   in full screen
        if QDesktopWidget().screenCount() > 1:
            self.img_SLM_widget.windowHandle().setScreen(qApp.screens()[1])
            self.img_SLM_widget.showFullScreen()

        self.img_widget.procStart.connect(self.img_SLM_widget.on_procStart)
        self.img_SLM_widget.procDone.connect(self.img_widget.img_SLM_procDone)

        self.setCentralWidget(self.img_widget)

        # Window settings
        self.setGeometry(100, 0, 792, 800)
        self.setWindowTitle('The LCOS-SLM Imgage Generator')
        # self.show_widgets()


    @QtCore.pyqtSlot()
    def show_widgets(self):
        self.img_widget.show()
        self.img_SLM_widget.show()


class ImgWindow(QWidget):
    procStart = QtCore.pyqtSignal(QImage)

    def __init__(self, parent=None):
        super(QWidget, self).__init__(parent)
        # calibration window
        self.calibWindow = CalibWindow()

        # running at start
        self._running = True
        # layout main window
        bigGrid = QGridLayout()

        # image
        ##############################################
        self.img = QImage(792, 600, QImage.Format_Grayscale8)
        # Initialisation
        self.img.fill(0)

        self.label = QLabel(self)
        self.label.setPixmap(QPixmap.fromImage(self.img))
        bigGrid.addWidget(self.label, 0, 0, 0, 3)
        ##############################################

        # Corrections Initialisation
        self.corrArrayAndCorrValue = lp.correctionsArray(1030)

        # Button
        self.goBtn = QPushButton("Go")
        self.goBtn.setFixedSize(250, 60)
        bigGrid.addWidget(self.goBtn, *(8, 0))

        self.calibBtn = QPushButton("Calibration")
        self.calibBtn.setFixedSize(220, 60)
        bigGrid.addWidget(self.calibBtn, *(8, 1))

        self.stopBtn = QPushButton("Pause")
        self.stopBtn.setFixedSize(220, 60)
        bigGrid.addWidget(self.stopBtn, *(8, 2))

        bigGrid.setHorizontalSpacing(50)

        self.goBtn.clicked.connect(self.goBtnPushed)
        self.calibBtn.clicked.connect(self.calibBtnPushed)
        self.stopBtn.clicked.connect(self.stopBtnPushed)

        # calib
        self.calib = False

        # zernike polynomials
        n_max_zernike_poly = 4
        self.zernike_list = []

        idx = []
        for n in range(n_max_zernike_poly):
            for m in range(-n, n+1):
                if n % 2 == 0 and m % 2 == 0:
                    idx.append([n, m])

                elif m == 0:
                    pass

                elif n % 2 == 1 and m % 2 == 1:
                    idx.append([n, m])
        
        print('Creation of the Zernike polynomials')
        for i in idx:
            self.zernike_list.append(clp.czernike(i[0], i[1]))

        print('Done')
        
        self.weigths = []
        for i in self.zernike_list:
            self.weigths.append(1)

        ##############################################
        self.setLayout(bigGrid)


    def stopBtnPushed(self):
        # TODO should pause the program
        if self._running is False:
            self._running = True

        elif self._running is True:
            self._running = False


    def calibBtnPushed(self):
        self.calib = True
        self.calibWindow.show()


    @QtCore.pyqtSlot()
    def img_SLM_procDone(self):
        self.raise_()


    def set_zernike_polynomials(self, weigths):
        """
            Arrange le slm selon le polynome de zernike associé au point

            :param weights: ndarray: matrice D x 1 des poids associés
                            aux polynomes dans un certain ordre
            :return: None
        """
        print("Starting ....")
        print("Values attribution ...")
        # generating the weight
        
        array = np.zeros(shape=(LENGHT_HA, LENGHT_LA))
        for i in range(len(self.zernike_list)):
            array += (weigths[i] * self.zernike_list[i]).astype(np.uint8)
            
        array = (array.astype(np.uint8) + self.corrArrayAndCorrValue[0].astype(np.uint8))*self.corrArrayAndCorrValue[1]

        for i in range(600):
            for j in range(792):
                element = array[i, j]
                gray = QtGui.QColor(QtGui.qRgb(element, element, element))
                self.img.setPixelColor(QPoint(j, i), gray)

        print('Actualisation of the image')

        self.label.setPixmap(QPixmap.fromImage(self.img))
        self.procStart.emit(self.img)
        print('Done')


    @QtCore.pyqtSlot()
    def goBtnPushed(self):
        # example_run_bayesian()
        self.set_zernike_polynomials(self.weigths)

        # TODO petit test pour changer les poids
        for i in range(len(self.weigths)):
            self.weigths[i] += 10


class ImgSLM(QWidget):
    procDone = QtCore.pyqtSignal(QImage)

    def __init__(self, parent=None):
        super(ImgSLM, self).__init__(parent)

        self.imgLayout = QGridLayout()
        self.img = QImage(792, 600, QImage.Format_Grayscale8)
        # Initialisation
        self.img.fill(0)

        self.label = QLabel(self)
        self.myPixmap = QPixmap.fromImage(self.img)
        # self.myScaledPixmap = self.myPixmap.scaled(self.label.size(), QtCore.Qt.IgnoreAspectRatio)
        self.label.setPixmap(self.myPixmap)

        self.imgLayout.setContentsMargins(0, 0, 0, 0)

        self.imgLayout.addWidget(self.label)
        self.setLayout(self.imgLayout)

    @QtCore.pyqtSlot(QImage)
    def on_procStart(self, img_arg):
        self.label.setPixmap(QPixmap.fromImage(img_arg))
        self.raise_()


class CalibWindow(QWidget):
    def __init__(self, parent=None):
        super(CalibWindow, self).__init__(parent)

        self.cornerWindow = CornerWindow()

        self.grid = QGridLayout()

        # number
        for i in range(1, 21):
            exec("self.no_{0} = QLabel('{0}.')".format(i))
            exec("self.grid.addWidget(self.no_{0}, {0}, 0)".format(i))

        # starting position
        self.labelPosi = QLabel('Starting position')
        self.grid.addWidget(self.labelPosi, 0, 1)

        for i in range(1, 21):
            exec("self.pos_{0} = QDoubleSpinBox()".format(i))
            exec("self.grid.addWidget(self.pos_{0}, {0}, 1)".format(i))

        # range [min, max]
        self.labelMin = QLabel('min')
        self.labelMax = QLabel('max')
        self.grid.addWidget(self.labelMin, 0, 2)
        self.grid.addWidget(self.labelMax, 0, 3)

        for i in range(1, 21):
            exec("self.rangeMin_{0} = QDoubleSpinBox()".format(i))
            exec("self.rangeMax_{0} = QDoubleSpinBox()".format(i))
            exec("self.grid.addWidget(self.rangeMin_{0}, {0}, 2)".format(i))
            exec("self.grid.addWidget(self.rangeMax_{0}, {0}, 3)".format(i))

        self.cornerBtn = QPushButton('Capture box')
        self.cornerOpen = False
        self.cornerBtn.clicked.connect(self.cornerBtnPushed)
        self.grid.addWidget(self.cornerBtn, 19, 4)

        self.closeBtn = QPushButton('Close')
        self.closeBtn.clicked.connect(self.closeBtnPushed)
        self.grid.addWidget(self.closeBtn, 20, 4)

        self.setLayout(self.grid)

    def closeBtnPushed(self):
        self.close()

    def cornerBtnPushed(self):
        if self.cornerOpen is False:
            self.cornerOpen = True
            self.cornerWindow.show()
        elif self.cornerOpen is True:
            self.cornerOpen = False
            self.cornerWindow.close()


class CornerWindow(QWidget):
    def __init__(self):
        super().__init__()
        print("1")
        self.grid = QGridLayout()

        calibrate_screenshot(0, 0, 0, 0, "ScreenCaps/1Calibration")

        self.label = QLabel()
        self.label.setPixmap(QPixmap("ScreenCaps/1Calibration.png"))
        self.label.setObjectName("image")
        self.label.mousePressEvent = self.getPos
        self.corners = []

        self.grid.addWidget(self.label)
        self.setLayout(self.grid)

    def getPos(self, event):
        if len(self.corners) == 4:
            self.corners = []
        x = event.pos().x()
        y = event.pos().y()
        self.corners.append(x)
        self.corners.append(y)
        print(self.corners)


if __name__ == '__main__':

    app = QApplication(sys.argv)

    mwin = MainWindow()
    mwin.show()

    sys.exit(app.exec_())
