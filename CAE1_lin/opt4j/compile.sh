#!/bin/bash
set -e

LIBPATH=$(pwd)/lib
CLASSPATH=$(ls $LIBPATH/*.jar | tr '\n' ':')

mkdir -p /tmp/vrp_bin

find src/Drones -name "*.java" > /tmp/sources.txt
javac -source 8 -target 8 -cp "$CLASSPATH" @/tmp/sources.txt -d /tmp/vrp_bin/

jar cf plugins/Drones.jar -C /tmp/vrp_bin/ .

echo "Done — plugins/Drones.jar updated"

## Cleanup
rm -rf /tmp/vrp_bin
