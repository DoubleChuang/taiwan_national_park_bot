#!/bin/bash

DOCKER_REPO=doublehub/tnpb
BASE_DIR=$(dirname "$0")
PROJECT_DIR=$(cd "$BASE_DIR/.."; pwd -P)

if [[ -f $PROJECT_DIR/.env ]]; then
    docker run -it --rm \
        --env-file $PROJECT_DIR/.env \
        -v $PROJECT_DIR:/workspace \
        -w /workspace \
        $DOCKER_REPO
else
    docker run -it --rm \
        -e ID=$ID \
        -e EMAIL=$EMAIL \
        -e CHROME_REMOTE_URL=$CHROME_REMOTE_URL \
        -e FINAL_SCREEN_PATH=/final_screen \
        -v $PROJECT_DIR:/workspace \
        -v $PROJECT_DIR:/final_screen \
        -w /workspace \
        $DOCKER_REPO
fi


