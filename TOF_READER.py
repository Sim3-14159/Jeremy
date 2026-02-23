import serial
import time
import pygame

PORT = '/dev/ttyACM0'
BAUD_RATE = 115200

pygame.init()
screen = pygame.display.set_mode([500, 500])

font = pygame.font.SysFont("monospace", 36)
ERRORTEXT = font.render("E", True, (255, 0, 0))

try:
    with serial.Serial(PORT, BAUD_RATE, timeout=0.1) as ser:
        print("Connected to the sensor on", PORT)
        time.sleep(2)

        readings = {}

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
                readings[key] = values.split(',')

                # once you have a complete update (expecting at least 8 sensors/keys)
                if len(readings) >= 8:
                    # ensure every collected key has at least 8 values
                    valid_keys = [k for k, v in readings.items() if len(v) >= 8]
                    if len(valid_keys) < 8:
                        # not a full frame yet; wait for more data
                        continue

                    # draw a stable layout by sorting keys (insertion order can vary)
                    for num, key in enumerate(sorted(valid_keys)):
                        for i in range(8):
                            try:
                                raw = int(readings[key][i])
                            except (ValueError, IndexError):
                                raw = 0

                            # scale raw -> size, avoid zero radius and use a sensible minimum
                            size = max(2, raw // 100)

                            # color: red when reading is suspiciously small
                            errorcolor = 255 if raw < 50 else 0
                            goodcolor = min(size * 10, 255)

                            pygame.draw.circle(screen, (errorcolor, goodcolor, 255),
                                               (50 + num * 50, 50 + i * 50), size)
                            if raw < 100:
                                screen.blit(ERRORTEXT, (50 + num * 50, 50 + i * 50))

                    pygame.display.flip()

                    # finished this frame; clear readings to collect the next frame
                    readings.clear()

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

pygame.quit()