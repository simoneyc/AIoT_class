#include <WiFi.h>
#include <HTTPClient.h>
#include <DHT.h>

#define WIFI_SSID "simone"
#define WIFI_PASSWORD "0968832955"
#define SERVER_IP "http://127.0.0.1:5003/post_data" // e.g., "192.168.1.100"
#define SERVER_PORT 5003
#define SENSOR_PIN 2
#define DHTTYPE DHT11

DHT dht(SENSOR_PIN, DHTTYPE);

void setup() {
  Serial.begin(115200);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");
  dht.begin();
}

void loop() {
  delay(2000);
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();
  if (isnan(temperature) || isnan(humidity)) {
    Serial.println("Failed to read from DHT sensor");
    return;
  }
  Serial.print("Temperature: ");
  Serial.print(temperature);
  Serial.println(" °C");
  Serial.print("Humidity: ");
  Serial.print(humidity);
  Serial.println(" %");
  sendSensorData(temperature, humidity);
}

void sendSensorData(float temperature, float humidity) {
  WiFiClient client;
  HTTPClient http;

  String data = "{\"temperature\":" + String(temperature) + ",\"humidity\":" + String(humidity) + "}";
  
  if (http.begin(client,String(SERVER_IP))) {
    http.addHeader("Content-Type", "application/json");
    int httpResponseCode = http.POST(data);
    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.println(response);
    } else {
      Serial.print("Error on sending POST: ");
      Serial.println(http.errorToString(httpResponseCode).c_str());
    }
    http.end();
  } else {
    Serial.println("Unable to connect to server");
  }
}
