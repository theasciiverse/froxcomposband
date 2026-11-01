#!/bin/sh
# Lays out the av archive in stage/: the start script at the top, and in
# game/ the binary with the lib/ folder it reads its data from.
set -eu
rm -rf stage && mkdir -p stage/game
cp asciiverse/froxcomposband stage/froxcomposband
cp src/froxcomposband stage/game/froxcomposband
mkdir -p stage/game/lib
tar -C lib --exclude=Makefile --exclude=.deps -cf - . | tar -C stage/game/lib -xf -
cp README.md PATCHES.md asciiverse/COPYING stage/
