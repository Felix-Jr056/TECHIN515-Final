#include "ble_service.h"
#include <Arduino.h>
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>

#define SERVICE_UUID "a1c40001-b5a3-f393-e0a9-e50e24dcca9e"
#define CHAR_UUID    "a1c40002-b5a3-f393-e0a9-e50e24dcca9e"
#define DEVICE_NAME  "Posiano-01"

static BLEServer*         server_handle    = nullptr;
static BLECharacteristic* char_handle      = nullptr;
static bool               is_connected     = false;
static uint8_t            frame_counter    = 0;

class ServerCallbacks : public BLEServerCallbacks {
    void onConnect(BLEServer*) override {
        is_connected = true;
        digitalWrite(D7, HIGH);
    }
    void onDisconnect(BLEServer*) override {
        is_connected = false;
        digitalWrite(D7, LOW);
        BLEDevice::startAdvertising();
    }
};

void ble_init() {
    BLEDevice::init(DEVICE_NAME);

    server_handle = BLEDevice::createServer();
    server_handle->setCallbacks(new ServerCallbacks());

    BLEService* service = server_handle->createService(SERVICE_UUID);

    char_handle = service->createCharacteristic(
        CHAR_UUID,
        BLECharacteristic::PROPERTY_NOTIFY
    );
    char_handle->addDescriptor(new BLE2902());

    service->start();
    BLEDevice::startAdvertising();
}

bool ble_connected() { return is_connected; }

void ble_notify(uint8_t midi, uint8_t confidence, bool onset) {
    if (!is_connected) return;
    uint8_t pkt[4] = {midi, confidence, onset ? 0x01u : 0x00u, frame_counter++};
    char_handle->setValue(pkt, 4);
    char_handle->notify();
}
