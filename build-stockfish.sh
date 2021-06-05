#!/bin/sh

echo "- Getting latest Stockfish ..."

if [ -d Stockfish/src ]; then
    cd Stockfish/src
    make clean > /dev/null
    git pull
else
    git clone --depth 1 https://github.com/official-stockfish/Stockfish.git
    cd Stockfish/src
fi

echo "- Determining CPU architecture ..."

ARCH=x86-64
EXE=stockfish-x86_64

if [ -f /proc/cpuinfo ]; then
    if grep "^flags" /proc/cpuinfo | grep -q popcnt ; then
        ARCH=x86-64-modern
        EXE=stockfish-x86_64-modern
    fi

    if grep "^flags" /proc/cpuinfo | grep bmi2 | grep -q popcnt ; then
        ARCH=x86-64-bmi2
        EXE=stockfish-x86_64-bmi2
    fi
else
    # check for apple silicon
    arch_name="$(uname -m)"
    if [ "${arch_name}" = "arm64" ]; then
        echo "Running on ARM"
        ARCH=apple-silicon
        EXE=stockfish-arm64
    elif [ "${arch_name}" = "x86_64" ];  then
        if [ "$(sysctl -in sysctl.proc_translated)" = "1" ]; then
            echo "Running on Rosetta 2"
        else
            echo "Running on native Intel"
        fi
        exit 1
    else
        echo "Unknown architecture: ${arch_name}"
        exit 1
    fi
fi

echo "- Building and profiling $EXE ... (patience advised)"
make profile-build ARCH=$ARCH EXE=../../$EXE > /dev/null

cd ../..
echo "- Done!"
