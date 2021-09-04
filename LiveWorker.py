from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QImage
import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import cv2

class LiveWorker(QThread):
    ImageUpdate = pyqtSignal(QImage)
    def run(self):
        self.ThreadActive = True
        import cv2
        import numpy as np
        import random
        random.seed(100)
        # ===============================================
        # get video

        cap = cv2.VideoCapture(1)
        # fg bg subtract model (MOG2)
        fgbg = cv2.createBackgroundSubtractorMOG2(history=500,
                                                  detectShadows=True)  # filter model detec gery shadows for removing
        # for writing video:
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter('night_output.avi', fourcc, 20.0, (704, 576))
        # ==============================================
        frameID = 0
        contours_info = []
        while self.ThreadActive:
            ret, frame = cap.read()
            if ret:

                # ====================== get and filter foreground mask ================
                original_frame = frame.copy()
                fgmask = fgbg.apply(frame)
                # ==================================================================
                # filter kernel for denoising:
                kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
                # Fill any small holes
                closing = cv2.morphologyEx(fgmask, cv2.MORPH_CLOSE, kernel)
                # Remove noise
                opening = cv2.morphologyEx(closing, cv2.MORPH_OPEN, kernel)
                # Dilate to merge adjacent blobs
                dilation = cv2.dilate(opening, kernel, iterations=2)
                # threshold (remove grey shadows)
                dilation[dilation < 240] = 0

                # ====================== switch and filter ================
                col_switch = cv2.cvtColor(frame, 70)
                lower = np.array([0,0,0])
                upper = np.array([40,10,255])
                mask = cv2.inRange(col_switch, lower, upper)
                res = cv2.bitwise_and(col_switch, col_switch, mask=mask)
                # ======================== get foreground mask=====================
                fgmask = fgbg.apply(res)
                kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
                # Dilate to merge adjacent blobs
                d_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
                dilation = cv2.dilate(fgmask, d_kernel, iterations=2)
                dilation[dilation < 255] = 0
                # =========================== contours ======================
                contours, im = cv2.findContours(dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                # extract every contour and its information:
                for cID, contour in enumerate(contours):
                    M = cv2.moments(contour)
                    # neglect small contours:
                    if M['m00'] < 100:
                        continue
                    # centroid
                    c_centroid = int(M['m10'] / M['m00']), int(M['m01'] / M['m00'])
                    # area
                    c_area = M['m00']
                    # perimeter
                    try:
                        c_perimeter = cv2.arcLength(contour, True)
                    except:
                        c_perimeter = cv2.arcLength(contour, False)

                    # convexity
                    c_convexity = cv2.isContourConvex(contour)
                    # boundingRect
                    (x, y, w, h) = cv2.boundingRect(contour)
                    # br centroid
                    br_centroid = (x + int(w / 2), y + int(h / 2))
                    # draw rect for each contour:
                    cv2.rectangle(original_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    # draw id:
                    cv2.putText(original_frame, str(cID), (x + w, y + h), cv2.FONT_HERSHEY_PLAIN, 3, (127, 255, 255), 1)
                    # save contour info
                    contours_info.append(
                        [cID, frameID, c_centroid, br_centroid, c_area, c_perimeter, c_convexity, w, h])

                # save frame image:
                cv2.imwrite('pics/{}.png'.format(str(frameID)), original_frame)
                cv2.imwrite('pics/fb-{}.png'.format(str(frameID)), dilation)
                frameID += 1
                k = cv2.waitKey(30) & 0xff
                if k == 27:
                    cap.release()
                    cv2.destroyAllWindows()
                    break
            else:
                break

            if ret:
                Image = cv2.cvtColor(original_frame, cv2.COLOR_BGR2RGB)
                FlippedImage = cv2.flip(Image, 1)
                ConvertToQtFormat = QImage(Image.data, Image.shape[1], Image.shape[0], QImage.Format_RGB888)
                Pic = ConvertToQtFormat.scaled(1000, 700, Qt.KeepAspectRatio)
                self.ImageUpdate.emit(Pic)
    def stop(self):
        self.ThreadActive = False
        self.quit()