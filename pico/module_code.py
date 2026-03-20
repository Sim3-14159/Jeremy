"""
module_code.py: this is put at the top of temp_code.py to give it the motor functionality.
"""

import uasyncio as asyncio
from machine import Pin, PWM
import math


# --- Physical Constants for L-Type 520 motors w/ 65mm Wheels ---
WHEEL_DIAMETER_MM = 65
GEAR_RATIO = 40
TICKS_PER_MOTOR_REV = 11 

TICKS_PER_WHEEL_REV = TICKS_PER_MOTOR_REV * GEAR_RATIO
CIRCUMFERENCE = WHEEL_DIAMETER_MM * math.pi
MM_PER_TICK = CIRCUMFERENCE / TICKS_PER_WHEEL_REV



class Wheel:
    def __init__(self, in1: int, in2: int, e1: int, e2: int, backward=False):
        """Initialize a Wheel. e1 (encoder 1) and e2 (encoder 2) are the wheel
        encoder pins, with e1 being the "trigger" pin, activated on machine.Pin.IRQ_RISING.
        in1 and in2 are inputs for the motors, and OUTPUTS FOR THE PICO. I labeled
        e1, e2, in1, and in2 so that they would match the labels on the Yahboom
        2-channel motor driver.
        """
        self.backward = backward
        self.encoder_count = 0 
        self.in1, self.in2, self.e1, self.e2 = PWM(Pin(in1)), Pin(in2, Pin.OUT), Pin(e1, Pin.IN), Pin(e2, Pin.IN)
        
        self.in1.freq(1000)
        self.e1.irq(trigger=Pin.IRQ_RISING, handler=self._encoder_handler)
        
    async def drive(self, distance: int, power: int=50): 
        """Drive the specified distance in mm and power (0-100)."""
        self.encoder_count = 0  # Reset distance for this move
        target_ticks = abs(distance / MM_PER_TICK)
        actual_power = power if distance > 0 else -power
        self._power(actual_power)
        
        while abs(self.encoder_count) < target_ticks:
            await asyncio.sleep_ms(5)
            
        self.stop()
    
    def stop(self):
        """Stop the motor."""
        self._power(0)
            
    def _power(self, power: int):
        """Set the Wheel's power (not speed), between -100 and 100 for -100% to 100%."""
        if self.backward: power = -power
        duty = int(abs(power) * 655.35)
        
        if power >= 0:
            self.in2.value(0)
            self.in1.duty_u16(min(duty, 65535))
        else:
            self.in2.value(1)
            self.in1.duty_u16(max(65535 - duty, 0))

    def _encoder_handler(self, _):
        """Automaticaly called on self.e1.irq on machine.Pin.IRQ_RISING."""
        if self.e1.value() == self.e2.value():
            self.encoder_count += 1
        else:
            self.encoder_count -= 1



class Chassis:
    def __init__(self, motor1: Wheel, motor2: Wheel):
        """Create a Chassis instance. motor1 and motor2 must be Motors."""
        self.motor1, self.motor2 = motor1, motor2    
    
    async def drive(self, distance, power=50):
        """Drive both motors concurrently and wait for both to finish."""
        await asyncio.gather(
            self.motor1.drive(distance, power),
            self.motor2.drive(distance, power)
        )



left = Wheel(12, 13, 16, 17)
right = Wheel(14, 15, 18, 19, True)
robot = Chassis(left, right)


