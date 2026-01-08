import pygame
import serial
import time

PORT_MEGA = 'COM4'
PORT_ESP = 'COM6'
VITEZA = 115200

try:
    ser_mega = serial.Serial(PORT_MEGA, VITEZA, timeout=0.05)
    print(f"Conectat la Mega pe {PORT_MEGA}")
except:
    print(f"EROARE: Nu gasesc Mega pe {PORT_MEGA}")
    exit()

ser_esp = None
try:
    ser_esp = serial.Serial(PORT_ESP, VITEZA, timeout=0.05, dsrdtr=False, rtscts=False)
    ser_esp.dtr = False
    ser_esp.rts = False
    time.sleep(2)
    print(f"Conectat la ESP32 pe {PORT_ESP}")
except:
    print(f"ATENTIE: ESP32 nu e conectat pe {PORT_ESP}.")

pygame.init()
BLOCK_SIZE = 30
GRID_WIDTH = 10 * BLOCK_SIZE
GRID_HEIGHT = 20 * BLOCK_SIZE
INFO_WIDTH = 200
TOTAL_WIDTH = GRID_WIDTH + INFO_WIDTH

win = pygame.display.set_mode((TOTAL_WIDTH, GRID_HEIGHT))
pygame.display.set_caption("Tetris System (Laptop Bridge)")
COLORS = [(0, 0, 0), (0, 255, 255), (0, 0, 255), (255, 165, 0), (255, 255, 0), (0, 255, 0), (128, 0, 128), (255, 0, 0)]


def draw_start_screen():
    win.fill((20, 20, 20))

    font_title = pygame.font.SysFont('Arial Black', 50)
    title_text = font_title.render("TETRIS", True, (0, 255, 255))
    rect_title = title_text.get_rect(center=(TOTAL_WIDTH // 2, GRID_HEIGHT // 3))
    win.blit(title_text, rect_title)

    font_small = pygame.font.SysFont('Arial', 20)
    msg_text = font_small.render("Press Joystick to Start", True, (255, 255, 255))
    rect_msg = msg_text.get_rect(center=(TOTAL_WIDTH // 2, GRID_HEIGHT // 2))
    win.blit(msg_text, rect_msg)

    pygame.display.update()


def draw_game(grid_data, score, high_score):
    win.fill((30, 30, 30))
    pygame.draw.rect(win, (0, 0, 0), (0, 0, GRID_WIDTH, GRID_HEIGHT))

    if len(grid_data) >= 200:
        for i in range(200):
            try:
                val = int(grid_data[i])
                if val > 0 and val < 8:
                    row = i // 10
                    col = i % 10
                    pygame.draw.rect(win, COLORS[val],
                                     (col * BLOCK_SIZE, row * BLOCK_SIZE, BLOCK_SIZE - 1, BLOCK_SIZE - 1))
            except:
                pass

    pygame.draw.rect(win, (255, 255, 255), (0, 0, GRID_WIDTH, GRID_HEIGHT), 2)

    font = pygame.font.SysFont('Arial', 20, bold=True)
    win.blit(font.render(f"SCOR: {score}", True, (0, 255, 0)), (GRID_WIDTH + 20, 50))
    win.blit(font.render(f"RECORD: {high_score}", True, (255, 215, 0)), (GRID_WIDTH + 20, 100))

    if ser_esp:
        win.blit(font.render("Wi-Fi: ON", True, (0, 255, 0)), (GRID_WIDTH + 20, 200))
    else:
        win.blit(font.render("Wi-Fi: OFF", True, (255, 0, 0)), (GRID_WIDTH + 20, 200))

    pygame.display.update()


running = True
last_esp_update = 0
last_sent_grid = ""
in_start_screen = False

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False

    if ser_mega.in_waiting > 0:
        try:
            line = ser_mega.readline().decode('utf-8', errors='ignore').strip()

            if line == "START":
                draw_start_screen()
                in_start_screen = True

                now = time.time()
                if ser_esp and (now - last_esp_update > 0.5):
                    empty_grid = "0" * 200
                    if empty_grid != last_sent_grid:
                        ser_esp.write(f"G:{empty_grid},0\n".encode('utf-8'))
                        last_sent_grid = empty_grid
                        last_esp_update = now

            elif line.startswith("FRAME:"):
                in_start_screen = False
                parts = line.split(":")

                if len(parts) >= 3:
                    current_grid = parts[1]
                    current_score = parts[2]
                    if len(parts) >= 4:
                        current_high = parts[3]
                    else:
                        current_high = "0"

                    draw_game(current_grid, current_score, current_high)

                    # Trimitem la ESP32 
                    now = time.time()
                    if ser_esp and (now - last_esp_update > 0.2):
                        if current_grid != last_sent_grid:
                            try:
                                msg = f"G:{current_grid},{current_score}\n"
                                ser_esp.write(msg.encode('utf-8'))
                                last_sent_grid = current_grid
                                last_esp_update = now
                            except Exception as e:
                                pass

            elif line == "GAMEOVER":
                print("Game Over - Waiting for reset")

        except:
            pass

pygame.quit()