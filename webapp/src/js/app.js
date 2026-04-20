// app.js — Owner: Member C — Entry point: module init, UI wiring on DOMContentLoaded

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('connect-btn').addEventListener('click', () => {
        connect().then(() => {
            document.getElementById('ble-status').textContent = 'Connected';
        }).catch(e => {
            document.getElementById('ble-status').textContent = 'Failed: ' + e.message;
        });
    });

    const midiFileInput = document.getElementById('midi-file');
    midiFileInput.addEventListener('change', (e) => {
        // TODO: call loadMidiFile(e.target.files[0]), display info in #midi-info
    });

    onNoteReceived((midi, confidence, onsetFlag) => {
        if (onsetFlag) {
            showNote(midi);
            showOnset();
        }
    });

    onPostureReceived((cls) => {
        showPostureAlert(cls);
    });
});
