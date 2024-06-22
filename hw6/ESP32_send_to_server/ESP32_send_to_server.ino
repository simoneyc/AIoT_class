#include <ArduinoJson.h>
#include <DHT11.h>
#include <HTTPClient.h>
#include <WiFi.h>

const char *ssid = "sc-i13";
const char *password = "00000002";
const char *serverAddress = "http://172.20.10.3:5000/post_data";

DHT11 dht11(2);

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }

  Serial.println("Connected to WiFi");
  Serial.println(WiFi.localIP());
}

void loop() {
  ///////////////////////Collect data ///////////////////////
  int temperature = 0;
  int humidity = 0;

  // Attempt to read the temperature and humidity values from the DHT11 sensor.
  int result = dht11.readTemperatureHumidity(temperature, humidity);

  if (result == 0) {
    Serial.print("Temperature: ");
    Serial.print(temperature);
    Serial.print(" °C\tHumidity: ");
    Serial.print(humidity);
    Serial.println(" %");
  } else {
    // Print error message based on the error code.
    Serial.println(DHT11::getErrorString(result));
  }

  ///////////////////////Send to server ///////////////////////

  // Create an object JSON
  DynamicJsonDocument jsonDoc(200);
  jsonDoc["temperature"] = temperature;
  jsonDoc["humidity"] = humidity;

  String payload;
  serializeJson(jsonDoc, payload);

  HTTPClient http;
  Serial.println("Server Address: " + String(serverAddress));

  http.begin(serverAddress);
  http.addHeader("Content-Type", "application/json");
  int httpResponseCode = http.POST(payload);

  if (httpResponseCode > 0) {
    Serial.printf("HTTP Response code: %d\n", httpResponseCode);
    String response = http.getString();
    Serial.println(response);
  } else {
    Serial.printf("HTTP Request failed: %s\n",
                  http.errorToString(httpResponseCode).c_str());
  }

  http.end();

  delay(5000);
  Serial.println();
}
