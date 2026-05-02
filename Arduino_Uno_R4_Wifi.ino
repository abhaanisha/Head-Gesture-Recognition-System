#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <WiFiS3.h>
#include <WiFiUdp.h>

// =========================
// OLED CONFIG
// =========================
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1
#define SCREEN_ADDRESS 0x3C

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// =========================
// WIFI CONFIG
// =========================
const char* ssid     = "Parthibg60";
const char* password = "Parthib123";

WiFiUDP udp;
#define UDP_PORT 5006

// =========================
// BUZZER CONFIG
// =========================
#define BUZZER_PIN 9

// =========================
// GLOBALS
// =========================
char packetBuffer[64];
String lastGesture = "";

// =========================
// DISPLAY HELPER
// =========================
void showGesture(String cls, String name) {
  display.clearDisplay();

  // Title
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 0);
  display.println("Gesture Detected:");

  // Gesture name (big)
  display.setTextSize(2);
  display.setCursor(0, 20);
  display.println(name);

  // Class number (small, bottom)
  display.setTextSize(1);
  display.setCursor(0, 52);
  display.print("Class: ");
  display.print(cls);

  display.display();
}

void showIdle() {
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 0);
  display.println("Waiting for");
  display.setTextSize(2);
  display.setCursor(0, 20);
  display.println("Gesture...");
  display.display();
}

// =========================
// BUZZER HELPER
// =========================
void buzzOnce() {
  digitalWrite(BUZZER_PIN, HIGH);
  delay(150);
  digitalWrite(BUZZER_PIN, LOW);
}

// =========================
// SETUP
// =========================
void setup() {
  Serial.begin(115200);
  pinMode(BUZZER_PIN, OUTPUT);
  digitalWrite(BUZZER_PIN, LOW);

  // OLED init
  if (!display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) {
    Serial.println("SSD1306 allocation failed");
    for (;;);
  }
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 0);
  display.println("Connecting WiFi...");
  display.display();

  // WiFi connect
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  // Wait for valid IP
  while (WiFi.localIP() == IPAddress(0, 0, 0, 0)) {
    delay(500);
  }

  Serial.println("\nConnected!");
  Serial.print("IP: ");
  Serial.println(WiFi.localIP());

  // Start UDP
  udp.begin(UDP_PORT);

  // Show ready on OLED
  showIdle();

  // Buzz once to signal ready
  buzzOnce();
}

// =========================
// LOOP
// =========================
void loop() {
  int packetSize = udp.parsePacket();

  if (packetSize) {
    int len = udp.read(packetBuffer, sizeof(packetBuffer) - 1);
    if (len > 0) packetBuffer[len] = '\0';

    String received = String(packetBuffer);
    Serial.println("Received: " + received);

    // Parse "cls,gesture_name"  e.g. "1,Nod"
    int commaIdx = received.indexOf(',');
    if (commaIdx != -1) {
      String cls  = received.substring(0, commaIdx);
      String name = received.substring(commaIdx + 1);

      // Only update display + buzz on gesture change
      if (name != lastGesture) {
        lastGesture = name;

        if (name == "Idle") {
          showIdle();
        } else {
          showGesture(cls, name);
          buzzOnce();
        }
      }
    }
  }
}