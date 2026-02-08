import serial
import time
import pygame

PORT = '/dev/ttyACM0'
BAUD_RATE = 115200

pygame.init()
screen = pygame.display.set_mode([500, 500])

try:
    with serial.Serial(PORT, BAUD_RATE, timeout=0.1) as ser:
        print("Connected to the sensor on", PORT)
        time.sleep(2)

        latest = {}

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()
                    
            screen.fill((255, 255, 255))
            
            line = ser.readline()
            if not line:
                continue

            try:
                text = line.decode('utf-8').strip()
                if ':' not in text:
                    continue

                key, values = text.split(':', 1)
                latest[key] = values.split(',')

                # Optional: print once you have a "complete" update
                if len(latest) >= 8:   # or whatever makes sense
                    #print(latest)
                    
                    for num, val in enumerate(latest):
                        for i in range(8):
                            size = int(latest[val][i]) // 100
                            #print(size)
                            
                            pygame.draw.circle(screen, (min(size * 10, 255), 0, 255),
                                               (50 + num * 50, 50 + i * 50), size)
                    
                    pygame.display.flip()

            except UnicodeDecodeError:
                print("UnicodeDecodeError LOL")
                continue
            
            except Exception as e:
                print("Error:", e)
                continue

except serial.SerialException as e:
    print("Error:", e)
except KeyboardInterrupt:
    print("Program terminated by user.")

"""
# Run until the user asks to quit
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Fill the background with white
    screen.fill((255, 255, 255))

    # Draw a blue circle
    pygame.draw.circle(screen, (0, 0, 255), (250, 250), 50)

    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
"""
pygame.quit()