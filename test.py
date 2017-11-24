

from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QGridLayout, QMainWindow
from PyQt5.QtGui import QIcon, QPixmap
import sys
from Screenshot import calibrate_screenshot


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.win = ImgWindow()
        self.win.show()

        self.setCentralWidget(self.win)


class ImgWindow(QWidget):
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


if __name__ == "__main__":

    app = QApplication(sys.argv)
    mwin = MainWindow()
    mwin.show()
    sys.exit(app.exec_())
