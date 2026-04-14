// app.js — Owner: Member C — Entry point: module init, UI wiring on DOMContentLoaded

document.addEventListener('DOMContentLoaded', () => {
    // Wire BLE connect button
    const bleStatus = document.getElementById('ble-status');
    bleStatus.addEventListener('click', () => {
        // TODO: call connect(), update bleStatus text on success/failure
    });

    // Wire MIDI file input
    const midiFileInput = document.getElementById('midi-file');
    midiFileInput.addEventListener('change', (e) => {
        // TODO: call loadMidiFile(e.target.files[0]), display info in #midi-info
    });

    // Wire BLE data callbacks
    onNoteReceived((event) => {
        // TODO: compare against MIDI reference, call showNote() and logNote()
    });

    onPostureReceived((className) => {
        // TODO: call showPostureAlert(className), logNote posture field
    });
});
