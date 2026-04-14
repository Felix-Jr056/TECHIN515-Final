// ble.js — Owner: Member C — Web Bluetooth API wrapper for XIAO ESP32S3 GATT connection

// GATT service UUID: TBD — coordinate with Member A

function connect() {
    // TODO: navigator.bluetooth.requestDevice(), connect to GATT server, cache characteristics
}

function disconnect() {
    // TODO: drop GATT connection, update UI status
}

function onNoteReceived(callback) {
    // TODO: subscribe to note/rhythm GATT characteristic notifications, invoke callback(event)
}

function onPostureReceived(callback) {
    // TODO: subscribe to posture GATT characteristic notifications, invoke callback(className)
}
