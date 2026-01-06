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
    # dsrdtr=False si rtscts=False ca sa prevenim restartarea ESP ului la conectare
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


def draw_game(grid_data, score, high_score):
    win.fill((30, 30, 30))

    # Desenare grid
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
        status_color = (0, 255, 0)
        status_text = "Wi-Fi: ON"
    else:
        status_color = (255, 0, 0)
        status_text = "Wi-Fi: OFF"
    win.blit(font.render(status_text, True, status_color), (GRID_WIDTH + 20, 200))

    pygame.display.update()

running = True
current_grid = "0" * 200
current_score = "0"
current_high = "0"

# Variabile pentru limitarea vitezei spre ESP
last_esp_update = 0
last_sent_grid = ""

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False

    if ser_mega.in_waiting > 0:
        try:
            line = ser_mega.readline().decode('utf-8', errors='ignore').strip()

            if line.startswith("FRAME:"):
                parts = line.split(":")

                if len(parts) >= 3:
                    current_grid = parts[1]
                    current_score = parts[2]

                    if len(parts) >= 4:
                        current_high = parts[3]
                    else:
                        current_high = "0"

                    # Desenam pe Laptop
                    draw_game(current_grid, current_score, current_high)

                    # Trimitem la ESP32 live. Trimitem doar daca au trecut 0.2 secunde
                    now = time.time()
                    if ser_esp and (now - last_esp_update > 0.2):

                        # Trimitem doar daca s-a schimbat ceva in grila
                        if current_grid != last_sent_grid:
                            try:
                                msg = f"G:{current_grid},{current_score}\n"
                                ser_esp.write(msg.encode('utf-8'))

                                last_sent_grid = current_grid
                                last_esp_update = now
                            except Exception as e:
                                print(f"Eroare trimitere ESP: {e}")

            elif line == "GAMEOVER":
                print("Game Over")
        except:
            pass

pygame.quit()