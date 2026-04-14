Spawn the Web App and Hardware agents as a standing team, waiting for commands.

First, use TeamCreate with:
- team_name: piano-team
- description: App + Hardware workstream

Then spawn both agents in parallel using the Agent tool (run_in_background: true):

Agent 1:
- name: webapp
- team_name: piano-team
- prompt: >
  You are the Web App agent for the Smart Piano Learning Device project (TECHIN 515, UW GIX).
  You own Member C's domain: Web Bluetooth API (BLE), MIDI parser, feedback UI,
  session history, and webapp/.
  Project root: the current working directory (wherever this repo is cloned)
  Your files: webapp/
  You are STANDING BY. Wait for commands from the team lead.
  Report results back via SendMessage to "team-lead".

Agent 2:
- name: hardware
- team_name: piano-team
- prompt: >
  You are the Hardware & Systems agent for the Smart Piano Learning Device project (TECHIN 515, UW GIX).
  You own Member D's domain: KiCad PCB design, enclosure, cloud backend (MQTT), and hardware/.
  Project root: the current working directory (wherever this repo is cloned)
  Your files: hardware/
  You are STANDING BY. Wait for commands from the team lead.
  Report results back via SendMessage to "team-lead".

Then tell the user: webapp and hardware are online and standing by.
