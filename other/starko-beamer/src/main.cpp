#include <string>
#include <cstring>
#include <iostream>

#include "utils.h"

int main(int argc, char* argv[]) {
    const std::string command = get_command_from_args(argc, argv);

    std::cout << command << std::endl;

    monitor_beamer(command);

    return 0;
}
