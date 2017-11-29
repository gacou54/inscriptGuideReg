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
                             QTabWidget, QFileDialog)
from PyQt5.QtCore import Qt, QByteArray, QPoint
from PyQt5.QtGui import (QPixmap, QImage)
from PyQt5 import QtGui, QtCore
from Main import *
import pickle
import threading
import time
import queue

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

        # Message système
        self.messagelabel = QLabel(self)
        self.messagelabel.setText("Test Message")
        bigGrid.addWidget(self.messagelabel, *(9, 0))

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
        self.calib = True
        self.corners = False
        self.variances = False
        self.mean = False

        # zernike polynomials
        n_max_zernike_poly = 4
        self.zernike_list = []

        idx = []
        for n in range(n_max_zernike_poly):
            for m in range(-n, n + 1):
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
        self.running = False
        ##############################################
        self.setLayout(bigGrid)
        #threading.Thread(daemon= True, target  = self.wait_for_signal()).start()
        self.queue = queue.Queue()

    def wait_for_signal(self):
        return None
        while True:
            time.sleep(5)
           # QApplication.processEvents()
            #print("counting")

    def stopBtnPushed(self):
        # TODO should pause the program
        if self.queue.empty():
            self.queue.put("Sleepy_slm")
        else:
            status = self.queue.get()

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

        array = (array.astype(np.uint8) + self.corrArrayAndCorrValue[0].astype(np.uint8)) * self.corrArrayAndCorrValue[
            1]

        for i in range(600):
            for j in range(792):
                element = array[i, j]
                gray = QtGui.QColor(QtGui.qRgb(element, element, element))
                self.img.setPixelColor(QPoint(j, i), gray)

        print('Actualisation of the image')

        self.label.setPixmap(QPixmap.fromImage(self.img))
        self.procStart.emit(self.img)
        QApplication.processEvents()
        print('Done')

    @QtCore.pyqtSlot()
    def goBtnPushed(self):
        box, mean, maxes, mins = pickle.load(open(self.calibWindow.filename, "rb"))
        # example_run_bayesian()
        if not self.calib or len(box) < 4:
            self.messagelabel.setText("No calibration Data: please calibrate the progam")
            return None
        elif self.running:
            self.messagelabel.setText("Program is already running")
            return None
        else:
            number = 5
            self.mainthread = threading.Thread(daemon=True, target=lambda : self.example_run_hadoc(box, mean, maxes, mins, number))
            #self.mainthread = threading.Thread(daemon=True, target=lambda : self.example_run_bayesian(box, mean, maxes, mins, number))

            self.mainthread.start()
            print("thread passed")
            self.running = True
            #self.set_zernike_polynomials(self.weigths)

            # TODO petit test pour changer les poids
            #for i in range(len(self.weigths)):
            #    self.weigths[i] += 4

    def example_run_hadoc(self,box,mean,maxes, mins, number):
        dimension = len(mean)
        x1, y1, x2, y2 = box[0], box[1], box[2], box[3]
        variances = []
        for i in range(0, len(maxes)):
            variances.append(abs(maxes[i] - mins[i]))

        print("generating test data")
        test_points = generate_sequence(mean, variances, dimension, number)
        print("gathering data")
        # Prise de données
        print(test_points.shape)
        for point in range(test_points.shape[0]):
            while not self.queue.empty():
                time.sleep(0.5)
            self.messagelabel.setText("Measurment progress : {}%".format(100 * (point+1) / test_points.shape[0]))

            self.set_zernike_polynomials(test_points[point])

            time.sleep(1)  # pour que le slm change de forme
            capture_box(x1, y1, x2, y2, "image{}".format(point), directory="ScreenCaps")
            time.sleep(0.2)

        score_list = []
        for point in range(test_points.shape[0]):
            self.messagelabel.setText("Score extraction progress : {}%".format(100 * point / test_points.shape[0]))
            score_list.append(round_score("ScreenCaps/image{}.png".format(point), "image{}contour.png".format(point),
                                          save_calibration=True))
        np.savetxt("Score_list", score_list)
        np.savetxt("Point_list", test_points)
        self.messagelabel.setText("Done : Score saved")
        # Fitting
        self.running = False

    def example_run_bayesian(self,box,mean, maxes, mins, number):
        # initialisation
        x1, y1, x2, y2 = box[0], box[1], box[2], box[3]
        dimension = len(mean)
        space = {}
        for x in range(dimension):
            try:
                space["{}".format(x)] = choco.uniform(maxes[x],mins[x])
            except:
                self.messagelabel.setText("Erreur : Un intervalle nul est invalide dans la calibration")
                self.running = False
                return None

        # pip install sclite3
        # sclite3 TEST.db
        conn = choco.SQLiteConnection("sqlite:///TEST.db")
        conn.lock()
        bay = choco.Bayes(conn, space, clear_db=True)
        (token, point_next) = bay.next()
        point = format_next(point_next)

        all_pos = []
        all_score = []
        for x in range(number):
            while not self.queue.empty():
                time.sleep(0.2)
            self.messagelabel.setText("Progress : {}%".format(100*(x+1)//number))

            loss = self.extract_score(x, x1, y1, x2, y2, point)
            bay.update(token, loss)
            (token, point_next) = bay.next()
            point = format_next(point_next)
            all_pos.append(point)
            all_score.append(1-loss)

        np.savetxt("Score_list", all_score)
        np.savetxt("Point_list", all_pos)
        self.messagelabel.setText("Done : Score and polynomial weighs saved")
        self.running = False
        return True

    def extract_score(self,number, x1, y1, x2, y2, test_point):
        '''
        Measures the score of a given point
        :param number: number of the point (for filename)
        :param x1: Int: Coordonnée x du coin supérieur gauche de la boîte à capturer [pixels]
        :param y1: Int: Coordonnée y du coin supérieur gauche de la boîte à capturer [pixels]
        :param x2: Int: Coordonnée x du coin inférieur droit de la boîte à capturer [pixels]
        :param y2: Int: Coordonnée y du coin inférieur droit de la boîte à capturer [pixels]
        :param test_point: Poids des polynomes de zernick à tester
        :return:
        '''
        self.set_zernike_polynomials(test_point)

        time.sleep(1)  # pour que le slm change de forme
        capture_box(x1, y1, x2, y2, "image{}".format(number), directory="ScreenCaps")
        time.sleep(0.2)
        score = round_score("ScreenCaps/image{}.png".format(number), "image{}contour.png".format(number),
                            save_calibration=True)
        return score


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

        self.loadBtn = QPushButton('Load')
        self.loadBtn.clicked.connect(self.loadBtnPushed)
        self.grid.addWidget(self.loadBtn, 19, 4)

        self.cornerBtn = QPushButton('Capture box')
        self.cornerOpen = False
        self.cornerBtn.clicked.connect(self.cornerBtnPushed)
        self.grid.addWidget(self.cornerBtn, 18, 4)

        self.closeBtn = QPushButton('Close')
        self.closeBtn.clicked.connect(self.closeBtnPushed)
        self.grid.addWidget(self.closeBtn, 21, 4)
        self.filename = "default"

        self.saveBtn = QPushButton('Save')
        self.saveBtn.clicked.connect(self.saveBtnPushed)
        self.grid.addWidget(self.saveBtn, 20, 4)
        # Message système
        self.messagelabel = QLabel(self)
        self.messagelabel.setText("Currently using default calibration".format(self.cornerWindow.corners))
        self.grid.addWidget(self.messagelabel, 22, 0,22,4)

        self.setLayout(self.grid)
    def loadBtnPushed(self):
        self.loaddialog = QFileDialog()
        self.loaddialog.setDirectory("CalibrationFiles")
        self.filename = self.loaddialog.getOpenFileName()[0]
        self.messagelabel.setText("Using file : {}".format(self.filename))

    def saveBtnPushed(self):
        if len(self.cornerWindow.corners) < 4:
            self.messagelabel.setText("Error : No corners selected")
            return None
        self.mean = []
        self.maxes = []
        self.mins = []

        for i in range(1, 21):
            exec("self.mean.append(self.pos_{0}.value())".format(i))
            exec("self.maxes.append(self.rangeMax_{0}.value())".format(i))
            exec("self.mins.append(self.rangeMin_{0}.value())".format(i))


        self.savedialog = QFileDialog()
        self.savedialog.setDirectory("CalibrationFiles")
        filename = self.savedialog.getSaveFileName()[0]


        pickle.dump((self.cornerWindow.corners,self.mean,self.maxes, self.mins),open(filename,"wb"))
        self.messagelabel.setText("Using file : {}".format(filename))
        self.filename = filename




    def closeBtnPushed(self):
        # getting the values
        self.mean = []
        self.variances = []
        for i in range(1, 21):
            pass
            #exec("self.pos_{0}_value = self.pos_{0}.value()".format(i))
            #exec("self.rangeMin_{0}_value = self.rangeMin_{0}.value()".format(i))
            #exec("self.rangeMax_{0}_value = self.rangeMax_{0}.value()".format(i))

        self.close()

    def cornerBtnPushed(self):
        if self.cornerOpen is False:
            self.cornerOpen = True
            self.cornerWindow.show()
        elif self.cornerOpen is True:
            self.cornerOpen = False
            self.cornerWindow.close()
        self.messagelabel.setText("Corners : {}".format(self.cornerWindow.corners))


class CornerWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.grid = QGridLayout()

        calibrate_screenshot(0, 0, 0, 0, "ScreenCaps/1Calibration")

        self.label = QLabel()
        self.label.setPixmap(QPixmap("ScreenCaps/1Calibration.png"))
        self.label.setObjectName("image")
        self.label.mousePressEvent = self.getPos
        self.corners = []

        self.grid.addWidget(self.label)
        self.setLayout(self.grid)
        self.resize(500,500)

        # Message système
        self.messagelabel = QLabel(self)
        self.messagelabel.setText("Corners : Select top left then bottom right")
        self.grid.addWidget(self.messagelabel, *(2, 0))

        self.corners = []

    def getPos(self, event):

        x = event.pos().x()
        y = event.pos().y()
        self.corners.append(x)
        self.corners.append(y)
        self.messagelabel.setText("Corners : {}".format(self.corners))

        if len(self.corners) == 4:
            self.close()



if __name__ == '__main__':
    app = QApplication(sys.argv)

    mwin = MainWindow()
    mwin.show()

    sys.exit(app.exec_())
