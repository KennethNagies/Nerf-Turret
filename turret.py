from targeting_system import TargetingSystem, StaticCameraTargetingSystem
from gpiozero import AngularServo, Button, Device
from gpiozero.pins.pigpio import PiGPIOFactory
from signal import pause
from random import randrange
from time import sleep

CAMERA_FOV = (70.42, 43.3)
SERVO_ANGLE_RANGE = (-90, 90)
SERVO_PULSE_WIDTH_RANGE = (0.0005, 0.0025)

BUTTON_PIN = 14
X_AXIS_PIN = 15
Y_AXIS_PIN = 18

class Turret():
    def __init__(self, x_axis_servo: AngularServo, y_axis_servo: AngularServo, targeting_system: TargetingSystem):
        self._targeting_system = targeting_system
        self._x_axis_servo = x_axis_servo
        self._x_axis_servo.angle = 0.0
        self._y_axis_servo = y_axis_servo
        self._y_axis_servo.angle = 0.0

    def target(self):
        target_angle = self._targeting_system.searchForTarget(self._x_axis_servo.angle, self._y_axis_servo.angle)
        if target_angle == None:
            print("No target found. Moving to idle angle")
            target_angle = self._targeting_system.getNextIdleAngle()
        self._x_axis_servo.angle = 0 - target_angle[0]
        self._y_axis_servo.angle = target_angle[1]
        print(f"Targeting Angle     : ({target_angle[0]}, {target_angle[1]})")

def main():
    Device.pin_factory = PiGPIOFactory()
    min_angle = SERVO_ANGLE_RANGE[0]
    max_angle = SERVO_ANGLE_RANGE[1]
    min_pulse_width = SERVO_PULSE_WIDTH_RANGE[0]
    max_pulse_width = SERVO_PULSE_WIDTH_RANGE[1]
    x_axis_servo = AngularServo(X_AXIS_PIN, min_angle=min_angle, max_angle=max_angle, min_pulse_width=min_pulse_width, max_pulse_width=max_pulse_width)
    y_axis_servo = AngularServo(Y_AXIS_PIN, min_angle=min_angle, max_angle=max_angle, min_pulse_width=min_pulse_width, max_pulse_width=max_pulse_width)
    targeting_system = StaticCameraTargetingSystem(CAMERA_FOV, x_axis_servo, y_axis_servo)
    turret = Turret(x_axis_servo, y_axis_servo, targeting_system)
    button = Button(BUTTON_PIN)
    button.when_pressed = turret.target
    while True:
        turret.target()
    pause()


if __name__=="__main__":
    main()

