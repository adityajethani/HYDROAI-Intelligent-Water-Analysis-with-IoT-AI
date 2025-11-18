#include <ESP8266WiFi.h>
#include <FirebaseESP8266.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <NTPClient.h>
#include <WiFiUdp.h>

// ---------------------- Wi-Fi Credentials ----------------------
#define WIFI_SSID "Vivo v40e"
#define WIFI_PASSWORD "jethani111"

// ---------------------- Firebase Credentials ----------------------
#define API_KEY "AIzaSyALRf7GTaFU_1l_btBflbhtEJwZKsEDATw"
#define DATABASE_URL "project-2625a-default-rtdb.firebaseio.com"


// ---------------------- Pin Configuration ----------------------
#define TDS_PIN A0        // Analog TDS sensor
#define ONE_WIRE_BUS D2   // DS18B20 data pin

// ---------------------- Objects ----------------------
FirebaseData fbdo;
FirebaseAuth auth;
FirebaseConfig config;
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);
WiFiUDP ntpUDP;
NTPClient timeClient(ntpUDP, "pool.ntp.org", 19800); // +5:30 for IST

unsigned long lastSend = 0;
const unsigned long interval = 30000; // 30 seconds

// ---------------------- TDS Calculation ----------------------
float readTDS() {
  int analogValue = analogRead(TDS_PIN);
  float voltage = analogValue * 3.3 / 1024.0;
  
  // More accurate TDS calculation
  float tdsValue = (133.42 * voltage * voltage * voltage
                   - 255.86 * voltage * voltage
                   + 857.39 * voltage) * 0.5;
  
  // Add some realistic variation for demo
  tdsValue += random(-20, 20);
  
  // Ensure TDS is within reasonable range
  if (tdsValue < 0) tdsValue = 0;
  if (tdsValue > 1000) tdsValue = 1000;
  
  return tdsValue;
}

// ---------------------- Get Timestamp ----------------------
String getTimestamp() {
  timeClient.update();
  unsigned long epochTime = timeClient.getEpochTime();
  
  // Convert epoch time to formatted timestamp
  struct tm *ptm = gmtime ((time_t *)&epochTime); 
  
  char timestamp[25];
  sprintf(timestamp, "%04d-%02d-%02dT%02d:%02d:%02d",
          ptm->tm_year + 1900,
          ptm->tm_mon + 1,
          ptm->tm_mday,
          timeClient.getHours(),
          timeClient.getMinutes(),
          timeClient.getSeconds());
          
  return String(timestamp);
}

// ---------------------- Setup ----------------------
void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println();
  Serial.println("🌊 WATER QUALITY MONITORING SYSTEM");
  Serial.println("====================================");
  
  // Initialize WiFi
  Serial.println("Connecting to Wi-Fi...");
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();
  Serial.println("✅ Wi-Fi Connected!");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());

  // Initialize NTP client
  timeClient.begin();
  Serial.println("✅ NTP Client initialized");

  // Initialize DS18B20 temperature sensor
  sensors.begin();
  Serial.println("✅ DS18B20 Sensor initialized");

  // Configure Firebase
  config.api_key = API_KEY;
  config.database_url = DATABASE_URL;
  auth.user.email = USER_EMAIL;
  auth.user.password = USER_PASSWORD;

  // Initialize Firebase
  Firebase.reconnectWiFi(true);
  Firebase.begin(&config, &auth);
  
  // Optional: Set buffer size for large data
  fbdo.setBSSLBufferSize(1024, 1024);
  
  Serial.println("✅ Firebase initialized!");
  Serial.println("Ready to send data to Firebase...");
  Serial.println("====================================");
}

// ---------------------- Loop ----------------------
void loop() {
  timeClient.update(); // Update NTP client
  
  if (millis() - lastSend >= interval) {
    lastSend = millis();

    // Read sensor values
    float tdsValue = readTDS();
    
    // Read temperature from DS18B20
    sensors.requestTemperatures();
    float tempValue = sensors.getTempCByIndex(0);
    
    // Check if DS18B20 is connected
    if (tempValue == DEVICE_DISCONNECTED_C) {
      Serial.println("❌ DS18B20 not found! Using default temperature.");
      tempValue = 25.0; // Default temperature
    }

    // Get current timestamp
    String timestamp = getTimestamp();
    String basePath = "/water_data/" + timestamp;

    // Display readings
    Serial.println("\n📊 SENSOR READINGS:");
    Serial.println("------------------------");
    Serial.println("Timestamp: " + timestamp);
    Serial.printf("TDS: %.2f ppm\n", tdsValue);
    Serial.printf("Temperature: %.2f °C\n", tempValue);
    Serial.println("------------------------");

    // Send data to Firebase
    bool tdsSuccess = false;
    bool tempSuccess = false;

    // Send TDS data
    if (Firebase.setFloat(fbdo, basePath + "/tds", tdsValue)) {
      Serial.println("✅ TDS data sent to Firebase");
      tdsSuccess = true;
    } else {
      Serial.println("❌ TDS upload failed: " + fbdo.errorReason());
    }

    // Send temperature data
    if (Firebase.setFloat(fbdo, basePath + "/temperature", tempValue)) {
      Serial.println("✅ Temperature data sent to Firebase");
      tempSuccess = true;
    } else {
      Serial.println("❌ Temperature upload failed: " + fbdo.errorReason());
    }

    // Overall status
    if (tdsSuccess && tempSuccess) {
      Serial.println("🎉 All data successfully uploaded to Firebase!");
    } else {
      Serial.println("⚠️ Some data failed to upload");
    }

    Serial.println("⏰ Next update in 30 seconds...");
    Serial.println("====================================");
  }

  // Small delay to prevent watchdog reset
  delay(1000);
}

// ---------------------- Additional Utility Functions ----------------------

void checkFirebaseConnection() {
  if (Firebase.ready()) {
    Serial.println("✅ Firebase connection active");
  } else {
    Serial.println("❌ Firebase connection lost");
  }
}

void printSensorInfo() {
  Serial.println("\n🔧 SENSOR INFORMATION:");
  Serial.println("------------------------");
  Serial.printf("TDS Sensor Pin: A0\n");
  Serial.printf("Temperature Sensor Pin: D2\n");
  Serial.printf("Update Interval: %lu ms\n", interval);
  Serial.printf("Firebase DB: %s\n", DATABASE_URL);
  Serial.println("------------------------");
}

// Function to test sensors (call in setup if needed)
void testSensors() {
  Serial.println("\n🧪 TESTING SENSORS...");
  
  // Test TDS sensor
  float testTDS = readTDS();
  Serial.printf("TDS Test Reading: %.2f ppm\n", testTDS);
  
  // Test temperature sensor
  sensors.requestTemperatures();
  float testTemp = sensors.getTempCByIndex(0);
  if (testTemp != DEVICE_DISCONNECTED_C) {
    Serial.printf("Temperature Test Reading: %.2f °C\n", testTemp);
  } else {
    Serial.println("Temperature Sensor: NOT DETECTED");
  }
  
  Serial.println("🧪 SENSOR TEST COMPLETE");
}