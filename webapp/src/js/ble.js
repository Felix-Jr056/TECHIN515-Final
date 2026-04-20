// ble.js — Owner: Member C — Web Bluetooth API wrapper for XIAO ESP32S3 GATT connection

const SERVICE_UUID = 'a1c40001-b5a3-f393-e0a9-e50e24dcca9e';
const CHAR_UUID    = 'a1c40002-b5a3-f393-e0a9-e50e24dcca9e';

let _noteCallback    = null;
let _postureCallback = null;
let _device          = null;

async function connect() {
    _device = await navigator.bluetooth.requestDevice({
        filters: [{ name: 'Posiano-01' }],
        optionalServices: [SERVICE_UUID]
    });
    const server = await _device.gatt.connect();
    const service = await server.getPrimaryService(SERVICE_UUID);
    const characteristic = await service.getCharacteristic(CHAR_UUID);
    await characteristic.startNotifications();
    characteristic.addEventListener('characteristicvaluechanged', (event) => {
        const view        = event.target.value;
        const midi         = view.getUint8(0);
        const confidence   = view.getUint8(1);
        const onsetFlag    = view.getUint8(2);
        const frameCounter = view.getUint8(3);
        if (_noteCallback) _noteCallback(midi, confidence, onsetFlag, frameCounter);
    });
}

function disconnect() {
    if (_device && _device.gatt.connected) {
        _device.gatt.disconnect();
    }
    _device = null;
}

function onNoteReceived(callback) {
    _noteCallback = callback;
}

function onPostureReceived(callback) {
    _postureCallback = callback;
}
