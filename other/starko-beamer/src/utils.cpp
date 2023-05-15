#include <iostream>
#include <string>
#include <cstring>
#include <map>

#include "utils.h"

const std::string X_FLAG = "-x";
const std::string Y_FLAG = "-y";
const std::string FADE_FLAG = "-f";
const std::string AUDIO_FLAG = "-a";
const std::string BLANK_FLAG = "-b";
const std::string OUTSIDE_FLAG = "-o";

std::map <std::string, std::string> PARAMETERS = {
    {X_FLAG, ""},
    {Y_FLAG, ""},
    {FADE_FLAG, ""},
    {AUDIO_FLAG, ""},
    {BLANK_FLAG, ""},
    {OUTSIDE_FLAG, ""}  // Заглушка
};

const int REFRESH_FRAMES = 100;

std::string get_command_from_args(int argc, char* argv[]) {
    bool outside = false;

    for (int i = 1; i < argc; i++) {
        if (strcmp(OUTSIDE_FLAG.c_str(), argv[i]) == 0) {
            outside = true;
            continue;
        }

        if (PARAMETERS.find(argv[i + 1]) == PARAMETERS.end()) {
            PARAMETERS[argv[i]] = argv[i + 1];
            i++;
        } else {
            return "";
        }
    }

    std::string command;

    if (!PARAMETERS[X_FLAG].empty()) {
        command.append("INFOBEAMER_ENV_GRID_X=");
        command.append(PARAMETERS[X_FLAG]);
        command.append(" ");
    }

    if (!PARAMETERS[Y_FLAG].empty()) {
        command.append("INFOBEAMER_ENV_GRID_Y=");
        command.append(PARAMETERS[Y_FLAG]);
        command.append(" ");
    }

    if (!PARAMETERS[FADE_FLAG].empty()) {
        command.append("INFOBEAMER_ENV_FADE_TIME=");
        command.append(PARAMETERS[FADE_FLAG]);
        command.append(" ");
    }

    if (!PARAMETERS[AUDIO_FLAG].empty()) {
        command.append("INFOBEAMER_AUDIO_TARGET=");
        command.append(PARAMETERS[AUDIO_FLAG]);
        command.append(" ");
    }

    if (outside) {
        command.append("INFOBEAMER_OUTSIDE_SOURCES=1 ");
    }

    if (!PARAMETERS[BLANK_FLAG].empty()) {
        command.append("INFOBEAMER_BLANK_MODE=");
        command.append(PARAMETERS[BLANK_FLAG]);
        command.append(" ");
    }

    command.append(
        "INFOBEAMER_LOG_LEVEL=4 info-beamer /var/starko/media 2>&1"
    );

    return command;
}

void monitor_beamer(std::string command) {
    int frames = 0;

    char buffer[1024];

    FILE* pipe = popen(command.c_str(), "r");

    if (!pipe) {
        throw std::runtime_error("Failed to open beamer");
    }

    try {
        if (command.find("INFOBEAMER_OUTSIDE_SOURCES=1") == std::string::npos) {
            while (fgets(buffer, sizeof buffer, pipe) != NULL) {
                ;
            }
        }

        while (fgets(buffer, sizeof buffer, pipe) != NULL) {
            if (strstr(buffer, "[glvideo.c]") != NULL) {
                frames = 0;

            } else {
                if (frames++ > REFRESH_FRAMES) {
                    frames = 0;
                    system("touch /var/starko/media/node.lua");
                    std::cout << "Reloading!" << std::endl;
                }
            }
        }

    } catch(...) {
        pclose(pipe);
        throw;
    }

    pclose(pipe);
}
