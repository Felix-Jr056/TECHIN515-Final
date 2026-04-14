# Agent: Vision ML Lead (Member B)

## Role

Owns hand posture classification — data collection, Edge Impulse model training, deployment to Grove Vision AI V2, and I2C integration with XIAO ESP32S3.

## Domains

- `prototyping/vision/preprocess.py` — resize/grayscale conversion for Edge Impulse upload
- `prototyping/vision/data_collection_log.md` — log every session (date, count, conditions)
- `prototyping/vision/datasets/` — gitignored; only metadata tracked
- `firmware/src/i2c_vision.*` — I2C reader on XIAO side

## Model Spec

- **Platform**: Edge Impulse (impulse.edgeimpulse.com)
- **Hardware target**: Grove Vision AI V2 (Arm Cortex-M55 + Ethos-U55 NPU)
- **Input**: 96×96 grayscale images, side-view of right hand
- **Classes** (3):
  - `correct` — proper arch, wrist level, curved fingers
  - `wrist_dropped` — wrist below keyboard level
  - `fingers_flat` — fingers extended instead of curved
- **Target accuracy**: ≥80% on 3-class validation set
- **Model type**: CNN INT8 (quantized for NPU)

## Data Collection Plan

| Phase | Dataset Size | Hands |
|-------|-------------|-------|
| Phase 1 | 150–200 images/class | 1 person |
| Phase 2 | Add 2–3 more hands | After Phase 1 validation |

Log every session in `data_collection_log.md`: date, lighting, camera angle, count per class.

## I2C Interface (coordinate with Member A / D)

Grove Vision AI V2 sends posture result over I2C Grove connector to XIAO.
- Packet: `[class_id: uint8, confidence: uint8]` — confirm format with firmware team
- XIAO firmware reads this in `i2c_vision.cpp` and forwards over BLE

## Verification Targets

- ≥80% 3-class validation accuracy in Edge Impulse
- Inference runs on-device without XIAO involvement (autonomous on Grove Vision AI)
- I2C zero packet loss over 5-min continuous test

## Key Rules

- Always log data collection sessions — date, count, conditions
- Never commit raw image datasets to git (use `.gitignore`)
- Confirm I2C packet format with Member A before finalising firmware reader
- Ask before adding a 4th class or changing image resolution
