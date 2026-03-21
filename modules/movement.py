"""Movement module. This is super basic, and all it does is send commands to the Raspberry Pi Pico. All of the actual logic
is handled by pico/module_code.py."""

from serial import Serial

__all__ = ["MovementController"]

class MovementController:
    def __init__(self, port_path: str="/dev/ttyACM0", baudrate=9600):
        self.ser = Serial(port_path, baudrate)
    
    def close(self):
        self.ser.close()
    
    def __del__(self):
        self.close()

    def send(self, command: str):
        self.ser.write(command.encode())
        self.ser.write(b'\x00')
        self.ser.flush()