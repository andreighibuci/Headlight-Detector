from PyQt5.QtGui import QImage
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import cv2


class ImageWorker(QThread):
    ImageUpdate = pyqtSignal(QImage)
    imagesource = ""
    def ShowImage(self):
        image = cv2.imread(self.imagesource)
        image_greyed = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        cv2.imwrite('gray_image.png', image_greyed)

        blur_image = cv2.blur( image_greyed, (15, 15))
        cv2.imwrite('blur_image.png', blur_image)

        ret, thresh = cv2.threshold(blur_image, 150, 255, 0)
        contours, contour_image = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(blur_image, contours, -1, (0, 255, 0), 3)

        moments = [cv2.moments(cnt) for cnt in contours]
        y_centroids = [int(round(m['m01'] / m['m00'])) for m in moments]

        x = len(y_centroids)

        i = 0
        while i < x:
            y_centroids[i] = y_centroids[i] // 10
            i = i + 1

        flag = 0
        i = 0
        while i < x:
            j = i + 1
            while j < x:
                if y_centroids[i] == y_centroids[j]:
                    flag = 1
                    break
                j = j + 1
            i = i + 1

        Image = cv2.cvtColor(blur_image, cv2.COLOR_BGR2RGB)
        ConvertToQtFormat = QImage(Image.data, Image.shape[1], Image.shape[0], QImage.Format_RGB888)
        Pic = ConvertToQtFormat.scaled(1000, 700, Qt.KeepAspectRatio)
        self.ImageUpdate.emit(Pic)
