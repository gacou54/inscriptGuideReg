#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
    Script for the pyQt program
"""
import sys
import time
import numpy as np
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

        self.img_widget = ImgWindow()
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
        self.calibWindow = CalibWindow(self)

        # layout main window
        bigGrid = QGridLayout()

        # image
        ##############################################
        self.img = QImage(792, 600, QImage.Format_Grayscale8)
        # # Initialisation
        self.img.fill(0)

        self.label = QLabel(self)
        self.label.setPixmap(QPixmap.fromImage(self.img))
        bigGrid.addWidget(self.label, 0, 0, 0, 3)
        ##############################################

        # Corrections Initialisation
        self.corrArrayAndCorrValue = lp.correctionsArray(1030)

        # Button
        # btnGrid = QGridLayout()
        self.goBtn = QPushButton("Go")
        self.goBtn.setFixedSize(250, 60)
        bigGrid.addWidget(self.goBtn, *(8, 0))

        self.calibBtn= QPushButton("Calibration")
        self.calibBtn.setFixedSize(220, 60)
        bigGrid.addWidget(self.calibBtn, *(8, 1))
        
        self.stopBtn = QPushButton("Pause")
        self.stopBtn.setFixedSize(220, 60)
        bigGrid.addWidget(self.stopBtn, *(8, 2))

        bigGrid.setHorizontalSpacing(50)

        self.goBtn.clicked.connect(self.goBtnPushed)
        self.calibBtn.clicked.connect(self.calibBtnPushed)
        self.stopBtn.clicked.connect(self.stopBtnPushed)
        ##############################################

        self.setLayout(bigGrid)

        array = (self.corrArrayAndCorrValue[0].astype(np.uint8))*self.corrArrayAndCorrValue[1]

        for i in range(600):
            for j in range(792):
                element = array[i, j]
                gray = QtGui.QColor(QtGui.qRgb(element, element, element))
                self.img.setPixelColor(QPoint(j, i), gray)

        self.label.setPixmap(QPixmap.fromImage(self.img))
        self.procStart.emit(self.img)


    def stopBtnPushed(self):
        # TODO should pause the program
        print('Pas encore implémenté')
    
    
    def calibBtnPushed(self):
        # TODO
        print('test')
        self.calibWindow.show()

        

    @QtCore.pyqtSlot()
    def img_SLM_procDone(self):
        self.raise_()

    @QtCore.pyqtSlot()
    def goBtnPushed(self):
        print("Starting ....")

        print('Getting the values')

        # example
        # if self.centre.isChecked():
        #     colors = colors.astype(np.uint8) + (255*lp.centre(self.centre_a.value(), self.centre_h.value())).astype(np.uint8)

        print('Application des corrections')
        array = (self.corrArrayAndCorrValue[0].astype(np.uint8))*self.corrArrayAndCorrValue[1]



        print('Creation of the image ...')

        for i in range(600):
            for j in range(792):
                element = array[i, j]
                gray = QtGui.QColor(QtGui.qRgb(element, element, element))
                self.img.setPixelColor(QPoint(j, i), gray)

        print('Actualisation of the image')

        self.label.setPixmap(QPixmap.fromImage(self.img))
        self.procStart.emit(self.img)

        print('Ready')
        return None


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


class CalibWindow(QMainWindow):
    def __init__(self, parent=None):
        super(CalibWindow, self).__init__(parent)
        self.grid = QGridLayout()

        self.pos_1 = QSpinBox()

        self.grid.addWidget(self.pos_1, 0, 0)

        self.setLayout(self.grid)


if __name__ == '__main__':

    app = QApplication(sys.argv)

    mwin = MainWindow()
    mwin.show()

    sys.exit(app.exec_())

