#include <WiFi.h>
#include <WebServer.h>
#include "esp32-hal-cpu.h"

const char* ssid = "Tetris_Arena";
const char* password = "parola_tetris";

WebServer server(80);
String gameData = "0"; 

const char index_html[] PROGMEM = R"rawliteral(
<!DOCTYPE HTML><html>
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1, user-scalable=no">
  <style>
    body { background-color: #121212; color: white; font-family: Arial; text-align: center; margin: 0; touch-action: none;}
    h2 { margin: 10px 0; color: #00bcd4; font-size: 18px; }
    
    #game-container {
      display: grid;
      grid-template-columns: repeat(10, 1fr); /* 10 coloane */
      grid-gap: 1px;
      width: 90vw; /* 90% din latimea telefonului */
      max-width: 300px;
      aspect-ratio: 1 / 2;
      margin: 0 auto;
      background-color: #333;
      border: 2px solid #555;
    }
    
    .cell { width: 100%; height: 100%; background-color: black; }
    
    .c0 { background: #000; }
    .c1 { background: #00ffff; } /* I - Cyan */
    .c2 { background: #0000ff; } /* J - Blue */
    .c3 { background: #ffa500; } /* L - Orange */
    .c4 { background: #ffff00; } /* O - Yellow */
    .c5 { background: #00ff00; } /* S - Green */
    .c6 { background: #800080; } /* T - Purple */
    .c7 { background: #ff0000; } /* Z - Red */

    #score-box { font-size: 24px; color: #0f0; margin-top: 10px; font-weight: bold; }
  </style>
</head>
<body>
  <h2>Tetris Live View</h2>
  <div id="game-container">
    </div>
  <div id="score-box">SCOR: <span id="sVal">0</span></div>

<script>
  const container = document.getElementById('game-container');
  for(let i=0; i<200; i++) {
    let div = document.createElement('div');
    div.className = 'cell c0';
    div.id = 'c'+i;
    container.appendChild(div);
  }

  setInterval(function() {
    fetch('/data').then(response => response.text()).then(data => {
      // Data vine sub forma: "000120...00,150" (Grid,Scor)
      let parts = data.split(",");
      if(parts.length < 2) return;
      
      let gridStr = parts[0];
      let scoreStr = parts[1];
      
      document.getElementById("sVal").innerText = scoreStr;

      if(gridStr.length >= 200) {
        for(let i=0; i<200; i++) {
          let val = gridStr.charAt(i);
          let cell = document.getElementById('c'+i);
          cell.className = 'cell c' + val;
        }
      }
    }).catch(e => console.log(e));
  }, 250); 
</script>
</body>
</html>)rawliteral";

void handleRoot() { 
  server.send(200, "text/html", index_html); 
}

void handleData() {
  // Trimitem datele curente catre telefon
  server.send(200, "text/plain", gameData);
}

void setup() {
  setCpuFrequencyMhz(80); 
  Serial.begin(115200);
  Serial.setTimeout(5);
  
  WiFi.mode(WIFI_AP);
  WiFi.softAP(ssid, password);
  WiFi.setTxPower(WIFI_POWER_11dBm); // Putere redusa pt stabilitate
  
  server.on("/", handleRoot);
  server.on("/data", handleData); 
  server.begin();
}

void loop() {
  server.handleClient();
  
  if (Serial.available()) {
    String raw = Serial.readStringUntil('\n');
    raw.trim();
    if (raw.startsWith("G:")) {
      gameData = raw.substring(2); // Salvam tot ce e dupa G:
    }
  }
  delay(1);
}