// feedback.js — Owner: Member C — Real-time UI feedback rendering for notes and posture

const NOTE_NAMES = ['C','Cs','D','Ds','E','F','Fs','G','Gs','A','As','B'];

function midiToNoteName(midi) {
    return NOTE_NAMES[midi % 12] + String(Math.floor(midi / 12) - 1);
}

function showNote(midi) {
    const display = document.getElementById('note-display');
    document.querySelectorAll('#piano-keyboard .lit').forEach(el => el.classList.remove('lit'));
    if (midi === 0xFF || midi === 255) {
        display.textContent = '--';
        return;
    }
    display.textContent = midiToNoteName(midi);
    const key = document.querySelector(`[data-midi="${midi}"]`);
    if (key) key.classList.add('lit');
}

function showOnset() {
    const flash = document.getElementById('onset-flash');
    if (!flash) return;
    flash.classList.remove('onset-flash');
    void flash.offsetWidth;
    flash.classList.add('onset-flash');
    setTimeout(() => flash.classList.remove('onset-flash'), 150);
}

function showTimingError(ms) {
    // Stub — Milestone 2
}

function showPostureAlert(msg) {
    const el = document.getElementById('posture-alert');
    if (el) el.textContent = msg || '';
}

function clearFeedback() {
    const display = document.getElementById('note-display');
    if (display) display.textContent = '--';
    document.querySelectorAll('#piano-keyboard .lit').forEach(el => el.classList.remove('lit'));
}
