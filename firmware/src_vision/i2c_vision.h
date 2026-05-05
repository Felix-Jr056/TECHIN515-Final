#pragma once

void vision_init();

// Returns: 0 = correct, 1 = fingers_flat, 2 = wrist_dropped, -1 = no result / error
int vision_get_class();

const char* vision_class_name(int cls);
