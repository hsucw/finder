CC=/mnt/data/CSProject/tools/android-toolchain/bin/arm-linux-androideabi-gcc
CXX=/mnt/data/CSProject/tools/android-toolchain/bin/arm-linux-androideabi-g++
CFLAGS=-fPIE -c -o logger.o -std=c++11
LDFLAGS=-pie -o logger -std=c++11

all: logger.o
	${CXX} ${LDFLAGS} $<
	rm -f *.o

%.o: %.cpp
	${CXX} ${CFLAGS} $^

push:
	make
	adb push logger /sdcard/Documents/

clean:
	rm -f *.o logger
