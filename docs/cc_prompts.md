# Claude Code Setup Prompt

Paste this into Claude Code when you first open the `Piano/` workspace.

---

## First-time setup prompt:

```
Read CLAUDE.md, then read all files in .claude/agents/ and .claude/rules/. 
Confirm you understand:
1. The project architecture (XIAO ESP32S3 + Grove Vision AI V2 + INMP441)
2. The 4 team roles and their domains
3. The key constraints (no autonomous decisions, budget, deadlines)

Then tell me what you're ready to help with.
```

---

## Per-member prompts (daily use):

### Member A — Audio DSP
```
I'm Member A (Audio DSP Lead). Read the audio-dsp agent. 
My working directories are prototyping/audio/ and firmware/src/. 
What should I work on next based on our pre-hardware sprint plan?
```

### Member B — Vision ML
```
I'm Member B (Vision ML Lead). Read the vision-ml agent.
My working directory is prototyping/vision/. 
Help me set up the Edge Impulse project and data collection pipeline.
```

### Member C — Web App
```
I'm Member C (Web App + Comms Lead). Read the webapp agent.
My working directory is webapp/. 
Help me scaffold the web app with BLE connection and MIDI parser.
```

### Member D — Hardware
```
I'm Member D (Hardware + Systems Lead). Read the hardware agent.
My working directories are hardware/kicad/, hardware/enclosure/, and hardware/cloud/. 
Help me start the KiCad schematic for the XIAO + Grove Vision AI + INMP441 circuit.
```

---

## Useful mid-session prompts:

### Check deadlines
```
Read docs/syllabus_deadlines.md. What's due this week and next week?
```

### Cross-member integration
```
Read CLAUDE.md and the audio-dsp and webapp agents. I need to define the BLE GATT 
characteristic schema that both firmware and web app will use. Help me draft a shared 
interface spec.
```

### Pre-milestone check
```
Read CLAUDE.md. Milestone [1/2/3] is coming up. Based on the verification criteria 
in CLAUDE.md, what should each member demonstrate? List the specific tests to run.
```

### Code review
```
Review the files in [directory]. Check against the rules in .claude/rules/safety.md 
and the relevant agent file. Flag any issues.
```
