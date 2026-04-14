// session.js — Owner: Member C — Session lifecycle tracking and per-note event logging

function startSession() {
    // TODO: record session start timestamp, reset note log and stats
}

function endSession() {
    // TODO: mark session end, trigger summary computation and optional cloud upload
}

function logNote(event) {
    // TODO: append event { note, expected, timingMs, posture, ts } to session log
}

function getSummary() {
    // TODO: compute and return { totalNotes, correctNotes, avgTimingMs, postureAlerts }
}
