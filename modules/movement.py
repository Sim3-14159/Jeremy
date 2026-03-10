from serial import Serial
import time

__all__ = ["MovementController"]

class MovementControllerV1:
    def __init__(self, port='/dev/ttyUSB1', baudrate=115200):
        self.serial_port = Serial(port, baudrate)

    def drive(self, distance_mm: int, time_s: int=5):
        print(f"Driving {distance_mm} mm for {time_s} seconds")
        self.serial_port.write(f"$spd:0,{distance_mm},0,{distance_mm}#".encode())
        self.serial_port.flush()  # Ensure the command is sent immediately
        time.sleep(time_s)  # Simulate time taken to drive
        self.stop()

    def turn(self, num_degrees: int):
        ...

    def stop(self):
        print("Stopping movement")
        self.serial_port.write(b"$pwm:0,0,0,0#")

    def close(self):
        print("Closing serial connection")
        if self.serial_port.is_open:
            print("Stopping movement before closing")
            self.stop()
            self.serial_port.close()
    
    def __del__(self):
        self.close()



import serial
import time

class MovementController:
    def __init__(self):
        self.ser = serial.Serial("/dev/ttyUSB1", 115200)

    def set_speed(self, lf, rf, lb, rb):
        cmd = f"$spd:{lf},{rf},{lb},{rb}#"
        self.ser.write(cmd.encode())

    def read_enc(self):
        for tries in range(5): # try a few times to get a valid response from the microcontroller, since it can be a bit flaky sometimes
            self.ser.write(b"$upload:1,0,0#")
            time.sleep(0.1) # wait a bit for the microcontroller to respond
            line = self.ser.readline().decode()
            print(f"Encoder read attempt {tries+1}: {line.strip()}")
            if line:
                vals = line.split(":")[1].strip("#\r\n")
                break
        else:
            raise ValueError("Failed to get valid encoder values")
        return list(map(int, vals.split(",")))
    
    def turn(self, degrees):
        pass

    def stop(self):
        self.set_speed(0,0,0,0)

    def drive(self, num_meters):

        ticks_per_meter = 10
        target = num_meters * ticks_per_meter

        start = self.read_enc()
        start_avg = (start[0] + start[1]) / 2

        self.set_speed(200,200,200,200)
        time.sleep(0.1) # let the motor controllers actually start moving before we start checking the encoders, otherwise the controller will get locked up listening to our reads while it's trying to start the motors, which can cause it to miss encoder updates and get stuck in an infinite loop

        while True:
            enc = self.read_enc()
            avg = (enc[0] + enc[1]) / 2
            print(f"Current encoder values: {enc}, average: {avg}, target: {target}, start_avg: {start_avg}")
            if avg - start_avg >= target:
                break

        self.stop()

    def __del__(self):
        self.stop()
        self.ser.close()


def main():
    import serial
    import time

    ser = serial.Serial("/dev/ttyUSB1",115200)

    def set_speed(lf,rf,lb,rb):
        cmd = f"$spd:{lf},{rf},{lb},{rb}#"
        ser.write(cmd.encode())

    def read_enc():
        ser.write(b"$upload:1,0,0#")
        line = ser.readline().decode()
        vals = line.split(":")[1].strip("#\r\n")
        return list(map(int, vals.split(",")))

    def move_distance(meters):

        ticks_per_meter = 943
        target = meters * ticks_per_meter

        start = read_enc()
        start_avg = (start[0] + start[1]) / 2

        set_speed(100,100,100,100)

        while True:
            enc = read_enc()
            avg = (enc[0] + enc[1]) / 2
            if avg - start_avg >= target:
                break

        set_speed(0,0,0,0)

    move_distance(1)

if __name__ == "__main__":
    main()