#pragma once
#include <stdint.h>

void ble_init();
bool ble_connected();
void ble_notify(uint8_t midi, uint8_t confidence, bool onset);
