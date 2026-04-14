// midi-parser.js — Owner: Member C — MIDI file parsing and note event extraction

// Uses midifile-ts or manual parsing — TBD

function loadMidiFile(file) {
    // TODO: read File object as ArrayBuffer, parse MIDI header and track chunks
}

function getNoteEvents() {
    // TODO: return array of { tick, note, velocity, durationTicks } from parsed MIDI
}

function getTempoMap() {
    // TODO: return array of { tick, bpm } tempo change events for tick-to-ms conversion
}
