from gpiozero import AngularServo
from typing import Tuple, Optional
from math import sqrt
import cv2

CLASSIFIER_PATH = "./haarcascade_frontalface_default.xml"


class TargetingSystem:
    def searchForTarget(self, x_axis_angle: float, y_axis_angle: float) -> Optional[Tuple[float, float]]:
        pass

    def getNextIdleAngle(self) -> Tuple[float, float]:
        pass

class StaticCameraTargetingSystem(TargetingSystem):
    def __init__(self, camera_fov: Tuple[float, float], x_axis_servo: AngularServo, y_axis_servo: AngularServo):
        self._camera_fov = camera_fov
        self._axis_min_angles = (x_axis_servo.min_angle, y_axis_servo.min_angle)
        self._axis_max_angles = (x_axis_servo.max_angle, y_axis_servo.max_angle)
        self._capture_session = cv2.VideoCapture(0)
        self._camera_resolution = (self._capture_session.get(cv2.CAP_PROP_FRAME_WIDTH), self._capture_session.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self._classifier = cv2.CascadeClassifier(CLASSIFIER_PATH)
        self._capture_session.read()

    def searchForTarget(self, x_axis_angle: float, y_axis_angle: float) -> Optional[Tuple[float, float]]:
        _, image = self._capture_session.read()
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        targets = self._classifier.detectMultiScale(image)
        current_x = self._getCameraCoordFromServoAngle(x_axis_angle, 0)
        current_y = self._getCameraCoordFromServoAngle(y_axis_angle, 1)
        current_coords = (current_x, current_y)
        target_coords = (-1, -1)
        min_target_dist = -1
        for x, y, width, height in targets:
            current_target_coords = (int(x + (width / 2)), int(y + (height / 2)))
            target_dist = dist(current_coords, current_target_coords)
            if min_target_dist == -1 or min_target_dist > target_dist:
                min_target_dist = target_dist
                target_coords = current_target_coords
        if min_target_dist == -1:
            print(f"No targets found")
            return None
        cv2.circle(image, target_coords, 10, (0, 255, 0), -1)
        cv2.imwrite("./target.jpeg", image)
        target_x_angle = self._getProcessedAxisAngle(target_coords[0], 0)
        target_y_angle = self._getProcessedAxisAngle(target_coords[1], 0)
        print(f"Found target at: coords {target_coords}, angle {(target_x_angle, target_y_angle)}")
        return (target_x_angle, target_y_angle)

    def getNextIdleAngle(self) -> Tuple[float, float]:
        return (0.0, 0.0)

    def _getCameraCoordFromServoAngle(self, servo_axis_angle: float, axis_index: int) -> int:
        max_camera_angle = self._camera_fov[axis_index] / 2
        min_camera_angle = 0 - max_camera_angle
        camera_axis_angle = max(servo_axis_angle, min_camera_angle)
        camera_axis_angle = min(camera_axis_angle, max_camera_angle)
        image_ratio = (camera_axis_angle - min_camera_angle) / self._camera_fov[axis_index]
        return int(image_ratio * self._camera_resolution[axis_index])

    def _getProcessedAxisAngle(self, camera_axis_value: int, axis_index: int):
        angle = (0 - (self._camera_fov[axis_index] / 2)) + ((camera_axis_value / self._camera_resolution[axis_index]) * self._camera_fov[axis_index]) if self._camera_resolution[axis_index] > 0 else self._axis_max_angles[axis_index] - self._axis_min_angles[axis_index]
        angle = max(self._axis_min_angles[axis_index], angle)
        angle = min(self._axis_max_angles[axis_index], angle)
        return angle

def dist(coords1: Tuple[int, int], coords2: Tuple[int, int]) -> float:
    x_dist = abs(coords1[0] - coords2[0])
    y_dist = abs(coords1[1] - coords2[1])
    return sqrt((x_dist ** 2) + (y_dist ** 2))

