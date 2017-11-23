

from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PyQt5.QtGui import QIcon, QPixmap
import  sys
from Screenshot import calibrate_screenshot
class ImgWindow(QWidget):
    def __init__(self):
        super().__init__()
        print("1")
        calibrate_screenshot(0,0,0,0,"1Calibration.jpg")

        self.image = QLabel()
        self.image.setPixmap(QPixmap("ScreenCaps/1Calibration.jpg"))
        self.image.setObjectName("image")
        self.image.mousePressEvent = self.getPos
        self.corners = []


    def getPos(self , event):
        if len(self.corners) == 4:
            self.corners = []
        x = event.pos().x()
        y = event.pos().y()
        self.corners.append(x)
        self.corners.append(y)


if __name__ == "__main__":

    app = QApplication(sys.argv)
    mwin = ImgWindow()
    mwin.show()
    sys.exit(app.exec_())
