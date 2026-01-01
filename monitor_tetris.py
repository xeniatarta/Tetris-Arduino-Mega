import pygame
import serial
import time

PORT_ARDUINO = 'COM4'
VITEZA_SERIALA = 115200

try:
    ser = serial.Serial(PORT_ARDUINO, VITEZA_SERIALA, timeout=0.1)
    time.sleep(2)
    print("Conectat la Arduino (Mod Display).")
except:
    print("Nu s-a putut conecta la Arduino!")
    exit()

pygame.init()
BLOCK_SIZE = 30
WIDTH = 10 * BLOCK_SIZE
HEIGHT = 20 * BLOCK_SIZE
win = pygame.display.set_mode((WIDTH + 150, HEIGHT))  # +150 pt scor
pygame.display.set_caption("Tetris Arduino")

COLORS = [
    (0, 0, 0),
    (0, 255, 255),
    (0, 0, 255),
    (255, 165, 0),
    (255, 255, 0),
    (0, 255, 0),
    (128, 0, 128),
    (255, 0, 0)
]


def draw_grid(data_str, score):
    win.fill((20, 20, 20))

    # Desenam blocurile
    if len(data_str) >= 200:
        for i in range(200):
            try:
                val = int(data_str[i])
                row = i // 10
                col = i % 10
                if val > 0 and val < 8:
                    color = COLORS[val]
                    pygame.draw.rect(win, color, (col * BLOCK_SIZE, row * BLOCK_SIZE, BLOCK_SIZE - 1, BLOCK_SIZE - 1))
            except:
                pass

    # Desenam conturul gridului
    pygame.draw.rect(win, (255, 255, 255), (0, 0, WIDTH, HEIGHT), 2)

    # Afisam Scorul
    font = pygame.font.SysFont('Arial', 25)
    text = font.render(f"Scor: {score}", True, (255, 255, 255))
    win.blit(text, (WIDTH + 10, 50))

    pygame.display.update()


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Citire date de la arduino
    if ser.in_waiting > 0:
        try:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if line.startswith("FRAME:"):
                parts = line.split(":")
                if len(parts) == 3:
                    grid_data = parts[1]
                    score_val = parts[2]
                    draw_grid(grid_data, score_val)
            elif line == "GAMEOVER":
                print("Joc terminat!")
        except Exception as e:
            pass

pygame.quit()