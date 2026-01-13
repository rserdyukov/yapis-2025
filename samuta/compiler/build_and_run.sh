#!/bin/bash

MINGW_PATH="C:/mingw"
CLANG_TARGET="x86_64-w64-mingw32"

rm -f program.o runtime.o program.exe

./gradlew jar

java -jar build/libs/compiler-1.0-SNAPSHOT.jar $1

clang -c program.ll -o program.o -target $CLANG_TARGET -I"$MINGW_PATH/include" -O2
if [ $? -ne 0 ]; then
    exit 1
fi

gcc -c runtime.c -o runtime.o -I"$MINGW_PATH/include" -O2
if [ $? -ne 0 ]; then
    exit 1
fi

gcc program.o runtime.o -o program.exe -L"$MINGW_PATH/lib" -lmsvcrt
if [ $? -ne 0 ]; then
    exit 1
fi

./program.exe
