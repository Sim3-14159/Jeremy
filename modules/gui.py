"""
GUI module for rendering the camera feed and radar visualization.
"""

import pygame
import math
import time
from pyrplidar import PyRPlidar
from picamera2 import Picamera2

import __main__

pygame.init()

__all__ = ["GUI"]


class GUI:
    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = self.screen.get_size()
        self.camera_visual = _CameraVisual(screen, pygame.Rect(0, 0, self.width // 2, self.height))
        self.radar_visual = _LiDARVisual(screen, pygame.Rect(self.width // 2, 0, self.width // 2, self.height // 2))
        self.chat_visual = _ChatVisual(screen, pygame.Rect(0, self.height // 2, self.width // 2, self.height // 2))

        self.BACKGROUND_COLOR = (0, 0, 0)

    def update(self, message_text=None):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                __main__.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                    __main__.running = False
                elif event.key == pygame.K_h:
                    pygame.mouse.set_visible(not pygame.mouse.get_visible())
        
        self.camera_visual.update()
        self.radar_visual.update()
        if message_text is not None:
            self.chat_visual.update(message_text)
    
    def draw(self):
        self.screen.fill(self.BACKGROUND_COLOR)
        self.radar_visual.blit()
        self.camera_visual.blit()
        self.chat_visual.blit()
        pygame.display.flip()


class _CameraVisual:
    def __init__(self, screen, subscreen_rect):
        self.screen = screen
        self.subscreen_rect = subscreen_rect
        self.width, self.height = self.subscreen_rect.size
        self.camera = Picamera2()
        self.camera.preview_configuration.main.size = (self.width, self.height)
        self.camera.preview_configuration.main.format = 'RGB888'
        self.camera.configure("preview")
        self.camera.start()

    def update(self):
        self.array = self.camera.capture_array()
        self.image = pygame.image.frombuffer(self.array.data, (self.width, self.height), 'BGR')

    def blit(self):
        self.screen.blit(self.image, (self.width, 0))


class _LiDARVisual:
    def __init__(self, screen, subscreen_rect):
        self.screen = screen
        self.subscreen_rect = subscreen_rect
        self.width, self.height = self.subscreen_rect.size
        self.center = (self.width // 2, self.height // 2)

        self.lidar = PyRPlidar()
        self.lidar.connect(port="/dev/ttyUSB0", baudrate=460800, timeout=3)
        self.lidar.set_motor_pwm(500)
        time.sleep(2) # wait to initialize
        self.scan_generator = self.lidar.force_scan()

        self.RADAR_COLOR = (0, 255, 0)
        self.COLOR1 = (255, 0, 0)  # close
        self.COLOR2 = (255, 255, 0)  # medium
        self.COLOR3 = (0, 255, 0) # far

    def update(self):
        self.points = []
        for scan in self.scan_generator():
            if 50 <= scan.distance <= 3000:
                self.points.append((scan.angle, scan.distance))
            if len(self.points) > 360:  # Limit to one full sweep
                break
    
    def blit(self):
        self.draw_radar(self.points)

    def draw_radar(self, points):
        for angle, distance in points:
            x, y = self._polar_to_cartesian(angle, distance)
            color = self.COLOR1 if distance < 1000 else self.COLOR2 if distance < 2000 else self.COLOR3
            pygame.draw.circle(self.screen, color, (x, y), 3)

    def _polar_to_cartesian(self, angle_deg, radius):
        angle_rad = math.radians(angle_deg)
        r = radius * (self.width // 2) / 3000
        x = self.center[0] + int(r * math.cos(angle_rad))
        y = self.center[1] - int(r * math.sin(angle_rad))
        return x, y

    def __del__(self):
        self.lidar.stop()
        self.lidar.disconnect()


class _ChatVisual:
    def __init__(self, screen, subscreen_rect, font_size=20):
        self.screen = screen
        self.subscreen_rect = subscreen_rect
        self.width, self.height = self.subscreen_rect.size
        self.messages = []
        self.font = pygame.font.SysFont("monospace", font_size)
        self.font_size = font_size

        self.COLOR = (0, 255, 0)

    def update(self, message_text):
        self.messages.append(message_text)

    def blit(self):
        #pygame.draw.rect(self.screen, BACKGROUND_COLOR, self.subscreen_rect)
        y_offset = 10
        for msg in self.messages[-10:]:  # Show last 10 messages
            for line in self._text_wrap(msg, self.width - 20):
                text_surface = self.font.render(line, True, self.COLOR)
                self.screen.blit(text_surface, (10, y_offset))
                y_offset += self.font_size + 5
    
    def _text_wrap(self, text, max_width):
        """
        Helper function to wrap text within a certain pixel width, to prevent messages from spilling over screen.
        """
        lines = [text[i:i+max_width//self.font_size] for i in range(0, len(text), max_width//self.font_size)]
        print(lines)
        return lines