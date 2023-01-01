"""
@Project_Description:
    This is a UI for the Project LEAFS.

@Author:
    Can Ali Ates
    Baha Kırbaşoğlu
    Abdullah Enes Ergün
"""

# Import Libraries.
import sys
import cv2
import numpy as np
from PyQt5.QtGui import QPixmap, QFont
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtWidgets import QWidget, QApplication, QLabel, QVBoxLayout, QGridLayout
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread
import torch

# Class to Reflect Camera Frame to PyQt5 App.
class VideoThread(QThread):

    # Create PyQtSignal Object to Reflection.
    change_pixmap_signal = pyqtSignal(np.ndarray)

    # Initialize Object.
    def __init__(self, yawning, sleeping, raising_hand, eating_drinking, taking_note, listening, playing_phone, efficiency):
        super().__init__()
        self.model = torch.hub.load("./yolov5", 'custom', source='local',
                               path=r"./weights/leafs_i640_e184_b64_281222_v7.pt ",
                               )
        self.yawning = yawning
        self.sleeping = sleeping
        self.raising_hand = raising_hand
        self.eating_drinking = eating_drinking
        self.taking_note = taking_note
        self.listening = listening
        self.playing_phone = playing_phone
        self.efficiency = efficiency

        self._run_flag = True

    # Run the Thread.
    def run(self):

        # Create Camera Object.
        camera = cv2.VideoCapture(0)


        # Check Status of Program.
        while self._run_flag:
            # Read Frame and Status From Camera Object.
            ret, frame = camera.read()

            # Frame Can Read From Camera.
            if ret:

                # Convert Frame to RGB.

                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                result = self.model(frame, size=640)
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

                df = result.pandas().xyxy[0]
                #self.label1.setText(f"Yawning {}")
                yawn_count = 0
                sleeping_count = 0
                raising_hand_count = 0
                eat_count = 0
                taking_note_count = 0
                listening_count = 0
                playing_phone_count = 0

                color = (0, 0, 0)
                for index, row in df.iterrows():
                    x, y, xMax, yMax = int(row[0]), int(row[1]), int(row[2]), int(row[3])
                    if row[5] == 0:
                        yawn_count += 1
                        color = (255, 0, 0)
                    elif row[5] == 1:
                        sleeping_count += 1
                        color = (0, 255, 0)
                    elif row[5] == 2:
                        raising_hand_count += 1
                        color = (0, 0, 255)
                    elif row[5] == 3:
                        eat_count += 1
                        color = (255, 255, 0)
                    elif row[5] == 4:
                        taking_note_count += 1
                        color = (255, 0, 255)
                    elif row[5] == 5:
                        listening_count += 1
                        color = (0, 255, 255)
                    elif row[5] == 6:
                        playing_phone_count += 1
                        color = (203, 192, 255)

                    frame = cv2.rectangle(frame, (x, y), (xMax, yMax), color, 2)
                    frame = cv2.putText(frame, f"{row['name']}: {row['confidence']:.2f}", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2, cv2.LINE_AA)

                total_count = yawn_count + sleeping_count + raising_hand_count + eat_count + taking_note_count + listening_count + playing_phone_count
                if total_count!=0:
                    eff = (yawn_count*0.5 + raising_hand_count + eat_count*0.75 + taking_note_count + listening_count) / total_count
                else:
                    eff = 0

                self.yawning.setText(f"Yawning {yawn_count}")
                self.sleeping.setText(f"Sleeping {sleeping_count}")
                self.raising_hand.setText(f"Raising Hand {raising_hand_count}")
                self.eating_drinking.setText(f"Eating/Drinking {eat_count}")
                self.taking_note.setText(f"Taking Note {taking_note_count}")
                self.listening.setText(f"Listening {listening_count}")
                self.playing_phone.setText(f"Playing Phone {playing_phone_count}")
                self.efficiency.setText(f"Lecture Efficiency {eff*100:.2f}")

                self.change_pixmap_signal.emit(frame)

            # Frame Can't Read From Camera.
            else:
                print("Frame Can't Read From Camera...")
                break

            # Terminate Program with ESC.
            if cv2.waitKey(1) & 0xFF == 27:
                break

        # Terminate Camera.
        camera.release()



    # Stop the Thread.
    def stop(self):
        self._run_flag = False
        self.wait()


# Class to Design App and Control Workflow..
class App(QWidget):

    # Initialize App.
    def __init__(self):

        # Initialize Window Settings.
        super().__init__()
        self.setWindowTitle("Project LEAFS")

        self.display_width = 1280
        self.display_height = 960

        # Create Label to Hold Camera Frame.
        self.image_label = QLabel(self)
        self.image_label.resize(640, 480)

        # Create Text Label.

        self.textLabel1 = QLabel("Yawning:")
        self.textLabel1.setFont(QFont('Times New Roman', 14))

        self.textLabel2 = QLabel("Raising Hand:")
        self.textLabel2.setFont(QFont('Times New Roman', 14))

        self.textLabel3 = QLabel("Playing with Phone:")
        self.textLabel3.setFont(QFont('Times New Roman', 14))

        self.textLabel4 = QLabel("Sleeping:")
        self.textLabel4.setFont(QFont('Times New Roman', 14))

        self.textLabel5 = QLabel("Eat or Drinking:")
        self.textLabel5.setFont(QFont('Times New Roman', 14))

        self.textLabel6 = QLabel("Taking Note:")
        self.textLabel6.setFont(QFont('Times New Roman', 14))

        self.textLabel7 = QLabel("Listening:")
        self.textLabel7.setFont(QFont('Times New Roman', 14))
        # Create a Vertical Box Layout and Add the Labels.
        vbox = QGridLayout()
        self.xbox = QVBoxLayout()

        self.xbox.addWidget(self.textLabel1)
        self.xbox.addWidget(self.textLabel2)
        self.xbox.addWidget(self.textLabel3)
        self.xbox.addWidget(self.textLabel4)
        self.xbox.addWidget(self.textLabel5)
        self.xbox.addWidget(self.textLabel6)
        self.xbox.addWidget(self.textLabel7)

        self.textLabel8 = QLabel("Lecture Efficiency: ")
        self.textLabel8.setFont(QFont('Times New Roman', 14))
        vbox.addWidget(self.image_label, 0, 0)
        vbox.addLayout(self.xbox, 0, 1)
        vbox.addWidget(self.textLabel8, 1, 0)

        # Set the Vbox Layout as the Widgets Layout.
        self.setLayout(vbox)

        # Create the Video Capture Thread.
        self.thread = VideoThread(self.textLabel1, self.textLabel2, self.textLabel3, self.textLabel4, self.textLabel5, self.textLabel6, self.textLabel7, self.textLabel8)

        # Connect Thread Signal to Update Frame Simultaneously.
        self.thread.change_pixmap_signal.connect(self.update_image)

        # Start the Thread.
        self.thread.start()

    # Stop the Thread.
    def closeEvent(self, event):
        self.thread.stop()
        event.accept()

    # Update Frame Simultaneously.
    @pyqtSlot(np.ndarray)
    def update_image(self, cv_img):
        qt_img = self.convert_cv_qt(cv_img)
        self.image_label.setPixmap(qt_img)

    # Convert an OpenCV Image to QPixmap.
    def convert_cv_qt(self, cv_img):
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        p = qt_format.scaled(self.display_width, self.display_height, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)

# Run Program.
if __name__ == '__main__':
    app = QApplication(sys.argv)
    a = App()
    a.show()
    sys.exit(app.exec_())
