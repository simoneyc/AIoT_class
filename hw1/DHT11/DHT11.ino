#include <ESP32Firebase.h>
#include <WiFi.h>
#include <SimpleDHT.h>

#define DHTPIN 4
// #define DHTTYPE SimpleDHT11

SimpleDHT11 dht11(DHTPIN);

const char* ssid = "TOTOLINK_N200RE";
const char* password = "4110056008";

const char* host = "https://test2-7a221-default-rtdb.firebaseio.com/";
// const String databaseURL = "/test2-7a221-default-rtdb-export.json";

Firebase firebase(host);

void setup() {
  Serial.begin(9600);
  // Connect to Wi-Fi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");
}

void loop() {
    byte temperature = 0;
    byte humidity = 0;
    int err = SimpleDHTErrSuccess;
    // start working...
    Serial.println("=================================");
    if ((err = dht11.read(DHTPIN, &temperature, &humidity, NULL)) != SimpleDHTErrSuccess) {
       Serial.print("Read DHT11 failed, err="); Serial.println(err);delay(1000);
       return;
    }
    Serial.print("Humidity = ");   
    Serial.print((int)humidity);   
    Serial.print("% , ");   
    Serial.print("Temperature = ");   
    Serial.print((int)temperature);   
    Serial.println("C ");   

    String pushData = "temperature : " + String((int)temperature) + " / humidity : " + String((int)humidity);
    firebase.pushString("DHT11",pushData);
 
    delay(1000);  //每3秒顯示一次
}

