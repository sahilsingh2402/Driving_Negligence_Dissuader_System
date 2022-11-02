# PREP DEPENDENCIES
from PyQt5.QtCore import Qt, pyqtSignal, QThread  # To send out video frames to our PyQt5 GUI page
from PyQt5.QtGui import QImage  # To convert the OpenCV frames into PyQt5 image
import cv2 as cv  # For enabling computer vision
import numpy as np  # For SCi-Calculations
from imutils.object_detection import non_max_suppression  # To detect multiple humans in a single frame

# Histogram of Oriented Gradients Detector
HOGCV = cv.HOGDescriptor()
HOGCV.setSVMDetector(cv.HOGDescriptor_getDefaultPeopleDetector())
# Variable to record total detections
person = 0


# Pedestrian Detection Thread class (The PDS will run in a separate thread when called by the start button from GUI pge)
class StartPDS(QThread):
    # Variable that will be sent to GUI page
    ImageUpdate = pyqtSignal(QImage)
    TotalPeople = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.ThreadActive = None
    
    # {Pedestrian} Detection begins here (The method will run when the thread starts)
    def run(self):
        # Activating thread
        global person
        self.ThreadActive = True
        # Capture video
        video_stream = cv.VideoCapture("dependencies/video/ped1.mp4")
        # While the PDS thread is active, Do detections
        while self.ThreadActive:
            # Split video into frames
            ret, frame = video_stream.read()
            if ret:
                try:
                    # Resize the frame
                    frame = cv.resize(frame, (280, 175))
                    # USing Sliding window concept to detect humans in the frame
                    rects, weights = HOGCV.detectMultiScale(frame, winStride=(4, 4), padding=(8, 8), scale=2)
                    rects = np.array([[x, y, x + w, y + h] for (x, y, w, h) in rects])
                    pick = non_max_suppression(rects, probs=None, overlapThresh=0.65)
                    person = 1
                    # Draw bounding boxes front hte detected humans
                    for x, y, w, h in pick:
                        cv.rectangle(frame, (x, y), (w, h), (255, 255, 255), 1)
                        cv.rectangle(frame, (x, y - 20), (w, y), (33, 33, 33), -1)
                        cv.putText(frame, f'P{person}', (x, y), cv.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                        person += 1
                
                except TypeError or ValueError or AttributeError:
                    pass
                
                # Set the total detections value string that wil be sent to the GUI frame
                total_people = f"People: {person-1}"
                # Convert the frame from OpenCV format to PyQt5 format
                frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
                convert_to_qt_format = QImage(
                    frame.data, frame.shape[1],
                    frame.shape[0],
                    QImage.Format_RGB888)
                frame = convert_to_qt_format.scaled(800, 600, Qt.KeepAspectRatio)
                
                # Send the frames and Stats to the GUI window
                self.ImageUpdate.emit(frame)
                self.TotalPeople.emit(total_people)
        
        # Close all opened windows and stop video Capture
        video_stream.release()
        cv.destroyAllWindows()
    
    # Thread stop method (De-Activate the thread and Quit the operation when method is called from GUI window)
    def stop(self):
        self.ThreadActive = False
        self.quit()