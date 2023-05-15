TARGET = /usr/bin/starko-beamer
HDRS_DIR = include

SRCS = \
	src/main.cpp \
	src/utils.cpp

.PHONY: all clean

all: $(SRCS)
	g++ -Wall -Wextra -Werror -O3 -Ofast -I $(HDRS_DIR) -o $(TARGET) $(CFLAGS) $(SRCS) -lm

clean:
	rm -rf $(TARGET)
