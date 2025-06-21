# object_detector.py
from ultralytics import YOLO
import cv2

class ObjectDetector:
    def __init__(self):
        self.model = YOLO("yolov8n.pt")

    def detect_objects(self, frame):
        results = self.model.predict(frame, conf=0.5, verbose=False)
        objects = []
        if results:
            for box in results[0].boxes:
                cls = int(box.cls[0])
                label = self.model.names[cls]
                objects.append(label)
        return list(set(objects))  # Unique detected objects
