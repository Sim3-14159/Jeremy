import serial
import time
from ansi_colors import AnsiCodes, color_text

# Specify the serial port and baud rate
PORT = '/dev/ttyACM0'  # Change this to match the port your sensor is connected to
BAUD_RATE = 115200  # Default baud rate for the sensor

try:
    # Open the serial port
    with serial.Serial(PORT, BAUD_RATE, timeout=1) as ser:
        print("Connected to the sensor on", PORT)
        time.sleep(2)  # Give the sensor time to initialize

        while True:
            # Attempt to read a line from the sensor
            line = ser.readline().decode('utf-8').strip()
            if line:
                values = {line.split(":")[0]: line.split(":")[1]}
                print(color_text(values, AnsiCodes.fg_rgb(100, 200, 255)))

except serial.SerialException as e:
    print("Error: ", e)
except KeyboardInterrupt:
    print("Program terminated by user.")
