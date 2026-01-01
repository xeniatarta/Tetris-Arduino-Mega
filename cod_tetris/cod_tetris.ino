#include <Arduino.h>

const int pinX = A0;
const int pinY = A1;
const int pinButon = 2;

const int WIDTH = 10;
const int HEIGHT = 20;
int grid[HEIGHT][WIDTH]; 

unsigned long lastDropTime = 0;
unsigned long lastMoveTime = 0;
int dropInterval = 500; // Viteza de cadre
int moveInterval = 150; // Viteza de miscare stanga/dreapta

int currentX, currentY;
int currentType;
int currentRotation;
int score = 0;
bool gameOver = false;

// Stocam pozitiile blocurilor
const int shapes[7][4][4][2] = {
  { { {0,1},{1,1},{2,1},{3,1} }, { {2,0},{2,1},{2,2},{2,3} }, { {0,2},{1,2},{2,2},{3,2} }, { {1,0},{1,1},{1,2},{1,3} } }, // I

  { { {0,0},{0,1},{1,1},{2,1} }, { {1,0},{2,0},{1,1},{1,2} }, { {0,1},{1,1},{2,1},{2,2} }, { {1,0},{1,1},{0,2},{1,2} } }, // J
 
  { { {2,0},{0,1},{1,1},{2,1} }, { {1,0},{1,1},{1,2},{2,2} }, { {0,1},{1,1},{2,1},{0,2} }, { {0,0},{1,0},{1,1},{1,2} } }, // L

  { { {1,0},{2,0},{1,1},{2,1} }, { {1,0},{2,0},{1,1},{2,1} }, { {1,0},{2,0},{1,1},{2,1} }, { {1,0},{2,0},{1,1},{2,1} } }, // O

  { { {1,0},{2,0},{0,1},{1,1} }, { {1,0},{1,1},{2,1},{2,2} }, { {1,1},{2,1},{0,2},{1,2} }, { {0,0},{0,1},{1,1},{1,2} } }, // S

  { { {1,0},{0,1},{1,1},{2,1} }, { {1,0},{1,1},{2,1},{1,2} }, { {0,1},{1,1},{2,1},{1,2} }, { {1,0},{0,1},{1,1},{1,2} } }, // T

  { { {0,0},{1,0},{1,1},{2,1} }, { {2,0},{1,1},{2,1},{1,2} }, { {0,1},{1,1},{1,2},{2,2} }, { {1,0},{0,1},{1,1},{0,2} } } // Z
};

void spawnPiece() {
  currentType = random(0, 7);
  currentRotation = 0;
  currentX = 3;
  currentY = 0;
  
  if (!isValid(currentX, currentY, currentRotation)) {
    gameOver = true;
    Serial.println("GAMEOVER");
  }
}

void setup() {
  Serial.begin(115200); 
  pinMode(pinButon, INPUT_PULLUP);
  randomSeed(analogRead(A5)); 
  spawnPiece();
}

// Verifica daca o pozitie e valida
bool isValid(int x, int y, int rot) {
  for (int i = 0; i < 4; i++) {
    int px = x + shapes[currentType][rot][i][0];
    int py = y + shapes[currentType][rot][i][1];
    
    if (px < 0 || px >= WIDTH || py >= HEIGHT) 
      return false;
    if (py >= 0 && grid[py][px] != 0) 
      return false;
  }
  return true;
}

// Blocheaza piesa in matrice
void lockPiece() {
  for (int i = 0; i < 4; i++) {
    int px = currentX + shapes[currentType][currentRotation][i][0];
    int py = currentY + shapes[currentType][currentRotation][i][1];
    if (py >= 0) 
      grid[py][px] = currentType + 1; // +1 pentru a avea culori 1-7
  }
  
  // Verificam liniile  incomplete
  for (int i = HEIGHT - 1; i >= 0; i--) {
    bool full = true;
    for (int j = 0; j < WIDTH; j++) 
      if (grid[i][j] == 0) 
        full = false;
    
    if (full) {
      score += 10;
      // Stergem linia si mutam totul jos
      for (int k = i; k > 0; k--) {
        for (int j = 0; j < WIDTH; j++) 
          grid[k][j] = grid[k-1][j];
      }
      for (int j = 0; j < WIDTH; j++) 
        grid[0][j] = 0;
      i++; // Verificam din nou aceeasi linie
    }
  }
  spawnPiece();
}

void sendDisplayData() {
  // Trimitem matricea la display intr-un mod codificat
  Serial.print("FRAME:");
  
  int tempGrid[HEIGHT][WIDTH];
  for(int i=0; i<HEIGHT; i++) 
    for(int j=0; j<WIDTH; j++) 
      tempGrid[i][j] = grid[i][j];
      
  for (int i = 0; i < 4; i++) {
    int px = currentX + shapes[currentType][currentRotation][i][0];
    int py = currentY + shapes[currentType][currentRotation][i][1];
    if (py >= 0 && py < HEIGHT && px >= 0 && px < WIDTH)
      tempGrid[py][px] = currentType + 1;
  }

  // Serializam matricea
  for(int i=0; i<HEIGHT; i++) {
    for(int j=0; j<WIDTH; j++) {
      Serial.print(tempGrid[i][j]);
    }
  }
  Serial.print(":"); 
  Serial.println(score); 
}

void loop() {
  if (gameOver) {

    // Reset la buton
    if (digitalRead(pinButon) == LOW) { 
      memset(grid, 0, sizeof(grid));
      score = 0;
      gameOver = false;
      spawnPiece();
      delay(500);
    }
    return;
  }

  unsigned long now = millis();

  if (now - lastMoveTime > moveInterval) {
    int xVal = analogRead(pinX);
    int yVal = analogRead(pinY);
    
    if (xVal > 800) { // Stanga
      if (isValid(currentX - 1, currentY, currentRotation)) 
        currentX--;
      lastMoveTime = now;
    } else if (xVal < 200) { // Dreapta
      if (isValid(currentX + 1, currentY, currentRotation)) 
        currentX++;
      lastMoveTime = now;
    }
    
    // Rotire (Sus)
    if (yVal < 200) { 
      int newRot = (currentRotation + 1) % 4;
      if (isValid(currentX, currentY, newRot)) 
        currentRotation = newRot;
      delay(150); 
    }
    
    // Sa cada mai repede piesele (Jos)
    if (yVal > 800) 
      dropInterval = 50; 
    else 
      dropInterval = 500;
  }

  if (now - lastDropTime > dropInterval) {
    if (isValid(currentX, currentY + 1, currentRotation)) {
      currentY++;
    } else {
      lockPiece();
    }
    lastDropTime = now;
  }

  sendDisplayData();
  delay(30); 
}