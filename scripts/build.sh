#!/bin/bash

BASE_DIR=$(dirname "$0")
PROJECT_DIR=$(cd "$BASE_DIR/.."; pwd -P)

docker build $PROJECT_DIR \
    -t "chenjr0719/tnp_bot"

docker tag chenjr0719/tnp_bot doublehub/tnpb