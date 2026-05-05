#include <Arduino.h>
#include <Wire.h>
#include "i2c_vision.h"

void i2c_scan() {
    Serial.println("I2C scan:");
    for (int addr = 1; addr < 127; addr++) {
        Wire.beginTransmission(addr);
        if (Wire.endTransmission() == 0)
            Serial.printf("  found 0x%02X\n", addr);
    }
}

void setup() {
    Serial.begin(115200);
    Wire.begin();
    delay(1000);
    i2c_scan();
    Serial.println("Waiting for Grove Vision AI to boot...");
    delay(20000);
    i2c_scan();
    vision_init();
    Serial.println("Vision XIAO online");
}

void loop() {
    int cls = vision_get_class();
    Serial.printf("POSTURE:%d CLASS:%s\n", cls, vision_class_name(cls));
    delay(500);
}
