#include "i2c_vision.h"
#include <Seeed_Arduino_SSCMA.h>
#include <Wire.h>

static SSCMA AI;

void vision_init() {
    bool ok = AI.begin(&Wire, 0x28);
    Serial.printf("AI.begin=%d\n", ok);
}

int vision_get_class() {
    int ret = AI.invoke(1, false, false);
    Serial.printf("invoke=%d classes=%d boxes=%d\n", ret, (int)AI.classes().size(), (int)AI.boxes().size());
    if (ret != 0) return -1;
    if (AI.classes().size() == 0) return -1;

    int best_class = -1;
    int best_score = 0;
    for (auto& c : AI.classes()) {
        if (c.score > best_score) {
            best_score = c.score;
            best_class = c.target;
        }
    }
    if (best_class < 0 || best_class > 2) return -1;
    return best_class;
}

const char* vision_class_name(int cls) {
    switch (cls) {
        case 0: return "correct";
        case 1: return "fingers_flat";
        case 2: return "wrist_dropped";
        default: return "unknown";
    }
}
