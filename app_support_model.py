import sys
import os
sys.path.insert(0, os.path.abspath('ultralytics_local'))

from ultralytics import YOLO
import cv2
import numpy as np
import os
import sys
import logging
from threading import Thread
from queue import Queue
import sendtoserver as ss
import detection as det

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Determine the path to the bundled executable and adjust the model paths accordingly
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base_path, relative_path)

# Load the models
model_path = resource_path("saved_model/yolov8n.pt")
plate_model_path = resource_path("saved_model/best.pt")
model = YOLO(model_path)  # General vehicle detection model
plate_model = YOLO(plate_model_path)  # License plate detection model

class DetectionPipeline:
    def __init__(self):
        self.frame_queue = Queue(maxsize=25)
        self.plate_queue = Queue(maxsize=25)
        self.output_dir1 = resource_path('collect/')
        self.output_dir2 = resource_path('plate/')
        self.output_dir3 = resource_path('frame/')
        if not os.path.exists(self.output_dir1):
            os.makedirs(self.output_dir1)
        if not os.path.exists(self.output_dir2):
            os.makedirs(self.output_dir2)
        if not os.path.exists(self.output_dir3):
            os.makedirs(self.output_dir3)
        self.detector_thread = Thread(target=self.detect_vehicles)
        self.plate_thread = Thread(target=self.detect_plates)
        self.detector_thread.start()
        self.plate_thread.start()
        self.previous_frame = None
        

    def add_frame(self, frame, coo, US, PW):
        """ Add frames to the queue for processing. """
        self.frame_queue.put((frame, coo, US, PW))

    def detect_vehicles(self):
        """ Detect vehicles in the frame and push potential plates to the plate_queue. """
        while True:
            frame, coo, US, PW = self.frame_queue.get()
            try:
                

                processed_frame = self.preprocess_frame(frame, (400, 400, 1400, 800))
                k=0
                if coo<10:
                    self.previous_frame=processed_frame
                else:
                    print("k",k)
                    k=det.detch(self.previous_frame,processed_frame)
                    self.previous_frame=processed_frame
                    if k==1:
                        print("Vehicle")
                        cv2.rectangle(frame, (400,500), (1400,900), (0,255,0), 2)
                        name = f'{coo}.png'
                        cv2.imwrite(os.path.join(self.output_dir3, name), processed_frame)
                        results = model(processed_frame)
                        for boxe in results:
                            box = boxe.boxes
                            conf = box.conf[0]
                            cls = box.cls[0]
                            if conf > 0.75 and cls in [2, 3, 4, 7, 8]:
                                x1, y1, x2, y2 = map(int, box.xyxy[0])
                                vehicle_frame = processed_frame[y1:y2, x1:x2]
                                self.plate_queue.put((vehicle_frame, coo, US, PW))  # pushing to plate detection
                                name = f'{coo}_{conf}.png'
                                cv2.imwrite(os.path.join(self.output_dir1, name), vehicle_frame)
                    else:
                        print("No motion")

            except Exception as e:
                logging.error(f"Error in detect_vehicles: {e}")

    def detect_plates(self):
        """ Detect plates within regions identified as vehicles. """
        while True:
            frame, coo, US, PW = self.plate_queue.get()
            try:
                print("Plate")
                results_plate = plate_model(frame)
                if results_plate:
                    for plateee in results_plate:
                        plate = plateee.boxes
                        conf = plate.conf[0]
                        conf = "{:.2f}".format(conf)
                        conf = float(conf)
                        if conf >= .25:
                            a1, b1, a2, b2 = map(int, plate.xyxy[0])
                            numberplate = frame[b1:b2, a1:a2]
                            ff = ((a1 + a2) / 2, (b1 + b2) / 2)
                            cha = ss.send_plate(numberplate, US, PW)  # Push the number plate to ocr
                            a = a2 - a1
                            b = b2 - b1
                            name = f'{coo}_{conf}_{cha}.png'
                            cv2.imwrite(os.path.join(self.output_dir2, name), numberplate)
            except Exception as e:
                logging.error(f"Error in detect_plates: {e}")

    def preprocess_frame(self, frame, bbox):
        """ Crop and blacken areas outside the ROI to focus detection. """
        mask = np.zeros_like(frame)
        mask[bbox[1]:bbox[3], bbox[0]:bbox[2]] = 255
        return cv2.bitwise_and(frame, mask)

if __name__ == '__main__':
    pipeline = DetectionPipeline()
