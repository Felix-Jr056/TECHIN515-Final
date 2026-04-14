# AI Agent Teams — How to Use

This repo includes pre-configured AI agents that any team member can spin up inside **Claude Code** to get domain-specific help. Each agent knows its own part of the project — files, constraints, interfaces — and nothing outside it.

## What You Need

- [Claude Code](https://claude.ai/code) installed — desktop app or VS Code extension
- Clone this repo and open it as your working directory in Claude Code

That's it. No extra setup. The agents and commands are already in the repo.

---

## Launching Agents

Type any of these slash commands in the Claude Code chat input:

### One agent at a time

| Command | Agent | Helps with |
|---------|-------|------------|
| `/agent-audio` | audio-dsp | FFT pitch detection, onset detection, MIDI, firmware audio |
| `/agent-vision` | vision-ml | Edge Impulse model, data collection, image preprocessing |
| `/agent-webapp` | webapp | Web Bluetooth, MIDI parser, feedback UI, session history |
| `/agent-hardware` | hardware | KiCad PCB, enclosure design, MQTT cloud backend |

### Two agents at once

| Command | Agents | Good for |
|---------|--------|----------|
| `/team-audio-vision` | audio-dsp + vision-ml | Signal pipeline and ML model work |
| `/team-app-hw` | webapp + hardware | Comms and backend work |

### All four agents

| Command | Launches |
|---------|----------|
| `/team-all` | audio-dsp, vision-ml, webapp, hardware — all at once |

---

## How It Works

When you type a slash command, Claude Code reads the matching file from `.claude/commands/` and spins up the agent(s) in the background. The agents start up and wait for your instructions — they don't do anything until you tell them to.

Each agent runs in its own window. You can talk to them at the same time, in parallel.

> To see multiple agent windows side by side, use the **Claude Code desktop app** or **VS Code extension**. The terminal CLI only shows one window at a time.

---

## Example Session

```
/team-audio-vision
```

Two windows open. Then you direct each one:

```
You (to audio-dsp):  Review pitch_detect.py and flag edge cases in the HPS algorithm
You (to vision-ml):  Update data_collection_log.md with today's session notes
```

Both agents work in parallel and report back when done.

---

## What Each Agent Knows

| Agent | Owner | Files it works in |
|-------|-------|-------------------|
| audio-dsp | Member A | `prototyping/audio/`, `firmware/` |
| vision-ml | Member B | `prototyping/vision/` |
| webapp | Member C | `webapp/` |
| hardware | Member D | `hardware/` |

Agents are scoped to their domain. They won't touch files outside their area, and they know the project's constraints, interfaces, and verification targets for their role.
