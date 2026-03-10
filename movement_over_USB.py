import serial
import time
import re
import math
import sys

# ----- CONFIG -----
PORT = "/dev/ttyUSB1"      # change to your serial port
BAUD = 115200

WHEEL_DIAMETER_MM = 67     # wheel diameter
ENCODER_LINES = 11         # $mline
GEAR_RATIO = 30            # $mphase

# pulses per wheel revolution
PULSES_PER_REV = ENCODER_LINES * GEAR_RATIO * 4

# wheel circumference
WHEEL_CIRC = math.pi * WHEEL_DIAMETER_MM


ser = serial.Serial(PORT, BAUD, timeout=0.1)


def send(cmd):
    ser.write((cmd + "\n").encode())


def read_line():
    try:
        return ser.readline().decode().strip()
    except:
        return ""


def get_encoder():
    """
    Reads encoder totals from serial
    """
    send("$upload:1,0,0#")

    while True:
        line = read_line()

        if line.startswith("$MAll:"):
            nums = re.findall(r'-?\d+', line)
            return list(map(int, nums))


def stop():
    send("$spd:0,0,0,0#")


def move(distance_mm, speed=200):
    """
    Move robot forward distance in mm
    """

    start = get_encoder()

    target_pulses = int((distance_mm / WHEEL_CIRC) * PULSES_PER_REV)

    send(f"$spd:{speed},{speed},{speed},{speed}#")
    ser.flush()
    time.sleep(0.1)

    while True:

        current = get_encoder()

        diff = abs(current[1] - start[1])
        print(f"Current encoder: {current}, Target pulses: {target_pulses}, Diff: {diff}, Start: {start[1]}")

        if diff >= target_pulses:
            break

        time.sleep(0.01)

    stop()

if __name__ == "__main__":
    try:
        distance = 50
        speed = 200
        if len(sys.argv) == 2:
            distance = int(sys.argv[1])
            speed = 200
        elif len(sys.argv) >= 3:
            distance = int(sys.argv[1])
            speed = int(sys.argv[2])

        move(distance, speed)
    except KeyboardInterrupt:
        stop()
        print("Stopped by user")