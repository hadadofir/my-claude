// ESP32 + servo "SwitchBot" that presses the laptop power button, controlled via Telegram.
//
// Libraries (Arduino IDE > Library Manager): UniversalTelegramBot, ArduinoJson, ESP32Servo
// Board: "ESP32 Dev Module"
//
// Wiring: servo signal -> GPIO 13, servo V+ -> 5V (VIN), servo GND -> GND.
//
// Commands (only accepted from ALLOWED_CHAT_ID):
//   /status   - is the laptop reachable (TCP port 22)?
//   /on       - short press (power on). Refuses if laptop already answers.
//   /press    - short press, no checks
//   /forceoff - hold button 6s (hard power off)
//   /calibrate <rest> <press> - try servo angles live, e.g. /calibrate 90 60

#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <UniversalTelegramBot.h>
#include <ESP32Servo.h>

// ---------- config ----------
const char* WIFI_SSID     = "YOUR_WIFI";
const char* WIFI_PASS     = "YOUR_WIFI_PASSWORD";
const char* BOT_TOKEN     = "NEW_TOKEN_FROM_BOTFATHER";   // make a separate bot for this
const char* ALLOWED_CHAT_ID = "YOUR_CHAT_ID";             // get it from @userinfobot
const char* LAPTOP_IP     = "192.168.0.108";              // reserve this IP in your router's DHCP
const uint16_t LAPTOP_PORT = 22;                          // sshd is listening here

const int SERVO_PIN   = 13;
int restAngle  = 90;    // arm away from the key
int pressAngle = 60;    // arm pushing the key -- tune with /calibrate
const int SHORT_PRESS_MS = 600;
const int LONG_PRESS_MS  = 6000;
// ----------------------------

WiFiClientSecure tls;
UniversalTelegramBot bot(BOT_TOKEN, tls);
Servo servo;
unsigned long lastPoll = 0;

// Attach only while moving: an idle attached servo jitters and can bump the key.
void moveTo(int angle, int settleMs) {
  servo.attach(SERVO_PIN, 500, 2400);
  servo.write(angle);
  delay(settleMs);
  servo.detach();
}

void pressButton(int holdMs) {
  servo.attach(SERVO_PIN, 500, 2400);
  servo.write(pressAngle);
  delay(holdMs);
  servo.write(restAngle);
  delay(400);
  servo.detach();
}

bool laptopUp() {
  WiFiClient c;
  bool ok = c.connect(LAPTOP_IP, LAPTOP_PORT, 2000);
  c.stop();
  return ok;
}

void ensureWifi() {
  if (WiFi.status() == WL_CONNECTED) return;
  WiFi.disconnect();
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  for (int i = 0; i < 40 && WiFi.status() != WL_CONNECTED; i++) delay(500);
}

void handle(const telegramMessage& m) {
  if (m.chat_id != ALLOWED_CHAT_ID) return;  // ignore strangers silently
  String t = m.text;

  if (t == "/status") {
    bot.sendMessage(m.chat_id, laptopUp() ? "Laptop is UP" : "Laptop is DOWN (or unreachable)");
  } else if (t == "/on") {
    if (laptopUp()) { bot.sendMessage(m.chat_id, "Already up, not pressing (use /press to force)."); return; }
    pressButton(SHORT_PRESS_MS);
    bot.sendMessage(m.chat_id, "Pressed. Checking in 90s...");
    for (int i = 0; i < 18 && !laptopUp(); i++) delay(5000);
    bot.sendMessage(m.chat_id, laptopUp() ? "Laptop is UP" : "Still down after 90s - check the arm with /calibrate");
  } else if (t == "/press") {
    pressButton(SHORT_PRESS_MS);
    bot.sendMessage(m.chat_id, "Pressed.");
  } else if (t == "/forceoff") {
    pressButton(LONG_PRESS_MS);
    bot.sendMessage(m.chat_id, "Held 6s.");
  } else if (t.startsWith("/calibrate")) {
    int r, p;
    if (sscanf(t.c_str(), "/calibrate %d %d", &r, &p) == 2) {
      restAngle = constrain(r, 0, 180);
      pressAngle = constrain(p, 0, 180);
      moveTo(pressAngle, 500);   // brief touch so you can see the reach; too short to power on
      moveTo(restAngle, 500);
      bot.sendMessage(m.chat_id, "rest=" + String(restAngle) + " press=" + String(pressAngle) +
                      " (not saved; put final values in the sketch)");
    } else {
      bot.sendMessage(m.chat_id, "Usage: /calibrate <rest> <press>");
    }
  } else {
    bot.sendMessage(m.chat_id, "/status /on /press /forceoff /calibrate <rest> <press>");
  }
}

void setup() {
  Serial.begin(115200);
  moveTo(restAngle, 500);
  WiFi.mode(WIFI_STA);
  ensureWifi();
  tls.setCACert(TELEGRAM_CERTIFICATE_ROOT);
  bot.sendMessage(ALLOWED_CHAT_ID, "Power-button bot online (power was restored?). Laptop: " +
                  String(laptopUp() ? "UP" : "DOWN"));
}

void loop() {
  if (millis() - lastPoll < 3000) return;
  lastPoll = millis();
  ensureWifi();
  int n = bot.getUpdates(bot.last_message_received + 1);
  for (int i = 0; i < n; i++) handle(bot.messages[i]);
}
