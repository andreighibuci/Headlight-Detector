import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import cv2
from tkinter.filedialog import askopenfilename

from VideoWorker import *
from ImageWorker import *
from LiveWorker import *

class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.VBL = QVBoxLayout()

        self.FeedLabel = QLabel()
        self.VBL.addWidget(self.FeedLabel)

        self.CancelBTN = QPushButton("Video")
        self.CancelBTN.clicked.connect(self.VideoFeed)
        self.VBL.addWidget(self.CancelBTN)
        self.CancelBTN = QPushButton("Image")
        self.CancelBTN.clicked.connect(self.ImageFeed)
        self.VBL.addWidget(self.CancelBTN)
        self.CancelBTN = QPushButton("Live")
        self.CancelBTN.clicked.connect(self.LiveFeed)
        self.VBL.addWidget(self.CancelBTN)
        self.Worker1 = LiveWorker()
        self.Worker1.ImageUpdate.connect(self.ImageUpdateSlot)
        self.Worker1.start()
        self.setLayout(self.VBL)


    def ImageUpdateSlot(self, Image):
        self.FeedLabel.setPixmap(QPixmap.fromImage(Image))

    def VideoFeed(self):
        if (self.Worker1.ThreadActive):
            self.Worker1.stop()
        filename = askopenfilename()
        self.Worker1 = VideoWorker()
        self.Worker1.ImageUpdate.connect(self.ImageUpdateSlot)
        self.Worker1.video = filename
        self.Worker1.start()

    def LiveFeed(self):
        if(self.Worker1.ThreadActive):
            self.Worker1.stop()
        self.Worker1 = LiveWorker()
        self.Worker1.ImageUpdate.connect(self.ImageUpdateSlot)
        self.Worker1.start()

    def ImageFeed(self):
        if (self.Worker1.ThreadActive):
            self.Worker1.stop()
        filename = askopenfilename()
        ImageProc = ImageWorker()
        ImageProc.ImageUpdate.connect(self.ImageUpdateSlot)
        ImageProc.imagesource = filename
        ImageProc.ShowImage()


